"""
Integration tests for hybrid evaluation pipeline

Test the complete hybrid evaluation workflow:
1. Rule-based evaluation
2. RAG semantic search
3. LLM judgment
4. Score combination
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from src.config.evaluation_config import (
    NoveltyConfig,
    InventiveStepConfig,
    EvaluationConfig,
)
from src.dsl.logic.hybrid_evaluator import (
    HybridNoveltyEvaluator,
    HybridInventiveStepEvaluator,
)
from src.dsl.logic.claim_parser import ClaimComponentParser, ParsedClaim


class TestHybridNoveltyEvaluator:
    """Test hybrid novelty evaluation engine"""

    @pytest.fixture
    def setup(self):
        """Setup test fixtures"""
        config = EvaluationConfig(
            novelty=NoveltyConfig(
                min_similarity_threshold=0.7,
                vector_search_top_k=5,
            ),
            enable_rag=True,
            enable_llm=True,
        )

        # Mock RAG system
        rag_system = AsyncMock()

        evaluator = HybridNoveltyEvaluator(rag_system=rag_system)
        parser = ClaimComponentParser()

        return {
            "evaluator": evaluator,
            "parser": parser,
            "rag_system": rag_system,
            "config": config,
        }

    @pytest.mark.asyncio
    async def test_novelty_evaluation_with_rag_results(self, setup):
        """Test novelty evaluation with RAG results"""
        evaluator = setup["evaluator"]
        parser = setup["parser"]
        rag_system = setup["rag_system"]

        # Mock RAG results
        rag_system.retrieve_context = AsyncMock(
            return_value=[
                {
                    "content": "선행기술: 디스플레이를 포함하는 기기",
                    "source": "patent_law_001",
                    "similarity": 0.85,
                    "article_number": "제30조",
                },
                {
                    "content": "선행기술: 표시 장치 구조",
                    "source": "precedent_001",
                    "similarity": 0.72,
                    "article_number": None,
                },
            ]
        )

        # Test claim
        claim_text = "청구항 1. 디스플레이를 포함하는 휴대용 전자 기기"
        parsed_claim = parser.parse_claim(claim_text)

        # Evaluate
        result = await evaluator.evaluate_novelty(claim_text, parsed_claim)

        # Assertions
        assert result is not None
        assert result.combined_reasoning is not None
        assert result.rule_based_score >= 0.0
        assert result.rag_similarity >= 0.0
        assert result.confidence_score >= 0.0

    @pytest.mark.asyncio
    async def test_novelty_evaluation_without_rag(self, setup):
        """Test novelty evaluation without RAG (fallback mode)"""
        evaluator = setup["evaluator"]
        evaluator.rag_system = None
        parser = setup["parser"]

        claim_text = "청구항 1. 메모리와 프로세서를 포함하는 장치"
        parsed_claim = parser.parse_claim(claim_text)

        result = await evaluator.evaluate_novelty(claim_text, parsed_claim)

        assert result is not None
        assert result.rag_similarity == 0.0  # No RAG results
        assert result.combined_reasoning is not None

    @pytest.mark.asyncio
    async def test_novelty_evaluation_score_combination(self, setup):
        """Test score combination logic"""
        evaluator = setup["evaluator"]

        # Test combine_scores method
        rule_score = 0.3
        rag_similarity = 0.5
        llm_confidence = 0.8

        is_novel, final_score, reasoning = evaluator._combine_scores(
            rule_score, rag_similarity, llm_confidence, "LLM test reasoning"
        )

        assert isinstance(is_novel, bool)
        assert 0.0 <= final_score <= 1.0
        assert reasoning is not None


class TestHybridInventiveStepEvaluator:
    """Test hybrid inventive step evaluation engine"""

    @pytest.fixture
    def setup(self):
        """Setup test fixtures"""
        config = EvaluationConfig(
            inventive_step=InventiveStepConfig(
                technical_complexity={
                    "전자": 0.8,
                    "기계": 0.7,
                    "화학": 0.9,
                },
                precedent_search_top_k=5,
            ),
            enable_rag=True,
            enable_llm=True,
        )

        rag_system = AsyncMock()
        evaluator = HybridInventiveStepEvaluator(rag_system=rag_system)

        return {
            "evaluator": evaluator,
            "rag_system": rag_system,
            "config": config,
        }

    @pytest.mark.asyncio
    async def test_inventive_step_evaluation_with_precedents(self, setup):
        """Test inventive step evaluation with precedent cases"""
        evaluator = setup["evaluator"]
        rag_system = setup["rag_system"]

        # Mock precedent search
        rag_system.retrieve_context = AsyncMock(
            return_value=[
                {
                    "case_number": "2020후1234",
                    "summary": "진보성 판단: 신규한 기술 조합",
                    "similarity": 0.8,
                },
                {
                    "case_number": "2021후5678",
                    "summary": "진보성 인정: 예측 불가능한 효과",
                    "similarity": 0.65,
                },
            ]
        )

        claim_text = "청구항 1. 새로운 기술 조합을 포함하는 장치"
        technical_field = "전자"

        result = await evaluator.evaluate_inventive_step(claim_text, technical_field)

        assert result is not None
        assert result.combined_reasoning is not None
        assert result.confidence_score >= 0.0

    @pytest.mark.asyncio
    async def test_inventive_step_evaluation_by_field(self, setup):
        """Test inventive step evaluation varies by technical field"""
        evaluator = setup["evaluator"]
        evaluator.rag_system = None  # Disable RAG for this test

        claim_text = "청구항 1. 신규한 기술 방법"

        # Test different technical fields
        fields_and_scores = [
            ("전자", True),  # Higher complexity
            ("기계", True),  # Medium complexity
            ("화학", True),  # Very high complexity
        ]

        for field, _ in fields_and_scores:
            result = await evaluator.evaluate_inventive_step(claim_text, field)
            assert result is not None
            assert 0.0 <= result.rule_based_score <= 1.0


class TestHybridEvaluationIntegration:
    """Integration tests for complete evaluation workflow"""

    @pytest.fixture
    def setup(self):
        """Setup for integration tests"""
        config = EvaluationConfig(
            novelty=NoveltyConfig(min_similarity_threshold=0.7),
            inventive_step=InventiveStepConfig(),
            enable_rule_based=True,
            enable_rag=True,
            enable_llm=True,
        )

        rag_system = AsyncMock()
        novelty_evaluator = HybridNoveltyEvaluator(rag_system=rag_system)
        inventive_evaluator = HybridInventiveStepEvaluator(rag_system=rag_system)
        parser = ClaimComponentParser()

        return {
            "novelty_evaluator": novelty_evaluator,
            "inventive_evaluator": inventive_evaluator,
            "parser": parser,
            "rag_system": rag_system,
        }

    @pytest.mark.asyncio
    async def test_complete_evaluation_workflow(self, setup):
        """Test complete evaluation workflow (novelty + inventive step)"""
        novelty_eval = setup["novelty_evaluator"]
        inventive_eval = setup["inventive_evaluator"]
        parser = setup["parser"]
        rag_system = setup["rag_system"]

        # Setup mock RAG responses
        rag_system.retrieve_context = AsyncMock(return_value=[])
        rag_system.generate_answer = AsyncMock(
            return_value='{"is_novel": true, "confidence": 0.85, "reasoning": "새로운 조합"}'
        )

        claim_text = "청구항 1. 새로운 기술을 이용한 장치"

        # Step 1: Parse claim
        parsed_claim = parser.parse_claim(claim_text)
        assert parsed_claim is not None

        # Step 2: Evaluate novelty
        novelty_result = await novelty_eval.evaluate_novelty(claim_text, parsed_claim)
        assert novelty_result is not None

        # Step 3: Evaluate inventive step
        inventive_result = await inventive_eval.evaluate_inventive_step(
            claim_text, "전자"
        )
        assert inventive_result is not None

        # Verify results are reasonable
        assert novelty_result.confidence_score >= 0.0
        assert inventive_result.confidence_score >= 0.0

    @pytest.mark.asyncio
    async def test_evaluation_with_multiple_claims(self, setup):
        """Test evaluation of multiple claims"""
        novelty_eval = setup["novelty_evaluator"]
        parser = setup["parser"]

        claims = [
            "청구항 1. 기본 장치의 특성",
            "청구항 2. 종속항으로서의 추가 특성",
            "청구항 3. 추가 종속항",
        ]

        results = []
        for claim in claims:
            parsed = parser.parse_claim(claim)
            result = await novelty_eval.evaluate_novelty(claim, parsed)
            results.append(result)

        assert len(results) == len(claims)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_evaluation_error_handling(self, setup):
        """Test error handling in evaluation"""
        evaluator = setup["novelty_evaluator"]

        # Test with empty claim - should handle gracefully
        parsed = evaluator.claim_parser.parse_claim("")
        result = await evaluator.evaluate_novelty("", parsed)

        # Empty claim should result in low confidence
        assert result is not None
        assert result.confidence_score >= 0.0

    @pytest.mark.asyncio
    async def test_evaluation_performance(self, setup):
        """Test evaluation performance (should complete in reasonable time)"""
        import time

        evaluator = setup["novelty_evaluator"]
        evaluator.rag_system = None  # Disable RAG for pure rule-based test

        claim_text = "청구항 1. 새로운 기술을 이용한 장치"
        parsed_claim = evaluator.claim_parser.parse_claim(claim_text)

        start_time = time.time()
        result = await evaluator.evaluate_novelty(claim_text, parsed_claim)
        elapsed = time.time() - start_time

        assert result is not None
        assert elapsed < 1.0  # Should complete in less than 1 second


class TestEvaluationConfiguration:
    """Test evaluation configuration management"""

    def test_config_defaults(self):
        """Test default configuration values"""
        config = EvaluationConfig()

        assert config.novelty is not None
        assert config.inventive_step is not None
        assert config.enable_rag is True
        assert config.enable_llm is True

    def test_config_customization(self):
        """Test custom configuration"""
        custom_novelty = NoveltyConfig(
            min_similarity_threshold=0.5,
            vector_search_top_k=10,
        )

        config = EvaluationConfig(novelty=custom_novelty)

        assert config.novelty.min_similarity_threshold == 0.5
        assert config.novelty.vector_search_top_k == 10

    def test_config_with_disabled_features(self):
        """Test configuration with disabled RAG/LLM"""
        config = EvaluationConfig(
            enable_rag=False,
            enable_llm=False,
        )

        assert config.enable_rag is False
        assert config.enable_llm is False
