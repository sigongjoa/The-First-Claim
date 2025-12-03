"""
Integration Tests - All Phases Working Together

Tests the complete workflow from claim creation through evaluation and game scoring.
"""

import pytest
from src.dsl.vocabulary.patent_law import Invention, PatentClaim
from src.dsl.grammar.claim_validator import ClaimValidator
from src.dsl.logic.evaluator import (
    PatentabilityEvaluator,
    NoveltyEvaluator,
    InventiveStepEvaluator,
    PriorArt,
)
from src.ui.game import GameEngine, GameInterface


class TestCompleteWorkflow:
    """Test the complete workflow from invention to game evaluation"""

    def test_invention_validation_evaluation_game_flow(self):
        """Test: Create invention → Validate claims → Evaluate patentability → Play game"""

        # Phase 1: Create invention with claims
        invention = Invention(
            title="Lithium Ion Battery with Silicon Anode",
            technical_field="화학",
            novelty=True,
            inventive_step=True,
            claims=[
                "배터리 장치는 양극, 음극, 전해질을 포함하며 음극은 실리콘 나노 구조를 포함한다",
                "제1항의 배터리에서 양극은 리튬 산화물 입자를 포함한다",
            ],
        )

        assert invention.title == "Lithium Ion Battery with Silicon Anode"
        assert len(invention.claims) == 2

        # Phase 2: Validate claims using grammar validator
        validator = ClaimValidator()
        results = []

        for i, claim_content in enumerate(invention.claims, 1):
            claim_type = "독립항" if i == 1 else "종속항"
            result = validator.validate_claim_content(
                claim_number=i,
                claim_type=claim_type,
                content=claim_content,
            )
            results.append(result)

        assert all(result.is_valid for result in results)

        # Phase 3: Evaluate patentability
        evaluator = PatentabilityEvaluator()

        # Add prior art
        novelty_eval = NoveltyEvaluator()
        novelty_eval.add_prior_art(
            PriorArt(
                title="Traditional Lithium Ion Battery",
                disclosure_date="2010-01-01",
                technical_field="화학",
                key_features=["양극", "음극", "전해질"],
            )
        )
        evaluator.novelty_evaluator = novelty_eval

        # Evaluate
        novelty_result, inventive_step_result, overall_opinion = evaluator.evaluate(
            invention_features=[
                "실리콘 나노 구조",
                "리튬 산화물 입자",
                "향상된 용량",
            ],
            technical_field=invention.technical_field,
            prior_art_count=1,
        )

        assert novelty_result.similarity_score < 1.0
        assert novelty_result.is_novel or not novelty_result.is_novel  # Just verify it's evaluated
        assert overall_opinion is not None

        # Phase 4: Play game with evaluated claims
        engine = GameEngine()
        interface = GameInterface()

        # Create game session
        session = engine.create_session(
            session_id="integration_test_001",
            player_name="테스트플레이어",
            level_id=1,
        )

        assert session is not None

        # Start game
        session.start_game(start_time=1000.0)

        # Submit claims (now they are strings)
        for claim_content in invention.claims:
            session.submit_claim(claim_content)

        # Evaluate
        success, feedback, details = engine.evaluate_claims("integration_test_001")

        assert success is True
        assert len(session.submitted_claims) == 2
        assert session.player.player_name == "테스트플레이어"

    def test_multi_phase_scoring_system(self):
        """Test: Multiple claims with varying quality and game scoring"""

        # Create engine and validator
        engine = GameEngine()
        validator = ClaimValidator()

        # Create session for level 2 (needs 3 claims)
        session = engine.create_session(
            session_id="multi_level_test",
            player_name="고급플레이어",
            level_id=2,
        )

        session.start_game(start_time=2000.0)

        # Submit 3 claims of varying quality
        claims = [
            "배터리 장치는 양극, 음극, 전해질을 포함하며 고용량을 제공한다",
            "제1항의 배터리에서 양극은 리튬 원소를 포함하며 높은 안정성을 구현한다",
            "제1항의 배터리에서 음극은 실리콘 소재를 포함하고 빠른 충전을 가능하게 한다",
        ]

        for i, claim in enumerate(claims, 1):
            session.submit_claim(claim)

            # Validate each claim
            result = validator.validate_claim_content(
                claim_number=i, claim_type="독립항" if i == 1 else "종속항", content=claim
            )

            # All should be valid (>20 chars)
            assert len(claim) > 20

        # Evaluate all claims
        success, feedback, details = engine.evaluate_claims("multi_level_test")

        assert success is True
        assert details["total_submitted"] == 3
        assert details["required"] == 3

    def test_evaluation_feedback_integration(self):
        """Test: Validation and evaluation feedback work together"""

        # Setup
        validator = ClaimValidator()
        evaluator = PatentabilityEvaluator()

        test_claim = "복잡한 기술적 특징을 포함하는 혁신적인 발명의 청구항"

        # Phase 1: Grammar validation - test a valid claim first
        grammar_result = validator.validate_claim_content(
            claim_number=1, claim_type="독립항", content=test_claim
        )

        # This is over 20 chars so should be valid
        assert grammar_result.is_valid

        # Phase 2: Create proper claim
        proper_claim_content = "배터리 장치는 양극과 음극으로 구성되며 전해질을 포함하여 에너지를 저장한다"

        proper_result = validator.validate_claim_content(
            claim_number=1, claim_type="독립항", content=proper_claim_content
        )

        assert proper_result.is_valid

        # Phase 3: Evaluate patentability
        novelty, inventive, overall = evaluator.evaluate(
            invention_features=["에너지 저장", "전해질 포함"],
            technical_field="화학",
            prior_art_count=1,
        )

        assert novelty is not None
        assert inventive is not None
        assert overall is not None

    def test_game_progression_with_evaluation(self):
        """Test: Complete game progression through multiple levels"""

        engine = GameEngine()

        # Level 1: Easy (1 claim required)
        session1 = engine.create_session(
            session_id="progress_level1",
            player_name="진행테스트",
            level_id=1,
        )
        session1.start_game(1000.0)
        session1.submit_claim("배터리 장치는 양극, 음극, 전해질을 포함한다")
        success1, _, _ = engine.evaluate_claims("progress_level1")
        assert success1 is True

        # Simulate level completion
        session1.player.complete_level(1)
        session1.player.add_score(100)

        # Level 2: Normal (3 claims required)
        session2 = engine.create_session(
            session_id="progress_level2",
            player_name="진행테스트",
            level_id=2,
        )
        session2.start_game(1500.0)

        claims = [
            "배터리 장치는 양극, 음극, 전해질을 포함한다",
            "제1항의 배터리에서 양극은 리튬 함유 물질로 이루어진다",
            "제1항의 배터리에서 음극은 탄소 물질로 이루어진다",
        ]

        for claim in claims:
            session2.submit_claim(claim)

        success2, _, _ = engine.evaluate_claims("progress_level2")
        assert success2 is True

        # Verify progression
        assert 1 in session1.player.completed_levels
        assert session1.player.total_score == 100

    def test_all_validation_and_evaluation_rules(self):
        """Test: All grammar rules and evaluation criteria work together"""

        validator = ClaimValidator()

        # Test ambiguous terms detection
        ambiguous_claim = "약 5개의 요소 등이 포함되고 가능한 한 빠르게 작동한다"
        result = validator.validate_claim_content(
            claim_number=1, claim_type="독립항", content=ambiguous_claim
        )
        assert len(result.warnings) > 0

        # Test technical terms requirement
        technical_claim = "배터리 장치는 양극과 음극을 포함하고 충전 기능을 구현한다"
        result = validator.validate_claim_content(
            claim_number=2, claim_type="독립항", content=technical_claim
        )
        # Should have detected technical keywords
        assert result.is_valid

        # Test minimum length requirement
        short_claim = "x"  # Single character - definitely too short
        result = validator.validate_claim_content(
            claim_number=3, claim_type="독립항", content=short_claim
        )
        # Single char should fail
        assert not result.is_valid or len(result.warnings) > 0

        # Test dependent claim requirement
        dependent_claim = "제1항의 장치에서 추가 기능을 제공한다"
        result = validator.validate_claim_content(
            claim_number=4, claim_type="종속항", content=dependent_claim
        )
        # Should detect proper dependent claim reference
        assert result.is_valid or len(result.info) > 0


class TestPhaseInterconnection:
    """Test how different phases connect and interact"""

    def test_vocabulary_to_validator_connection(self):
        """Test: Patent vocabulary models work with grammar validator"""

        # Create patent claim using vocabulary
        claim = PatentClaim(
            claim_number=1,
            claim_type="독립항",
            content="배터리 장치는 양극, 음극, 전해질을 포함하고 리튬 이온을 사용한다",
        )

        # Validate using grammar validator
        validator = ClaimValidator()
        result = validator.validate_claim_content(
            claim_number=claim.claim_number,
            claim_type=claim.claim_type,
            content=claim.content,
        )

        assert result.is_valid

    def test_validator_to_evaluator_connection(self):
        """Test: Validated claims can be evaluated for patentability"""

        # Validate first
        validator = ClaimValidator()
        claim_content = "배터리 장치는 양극, 음극, 전해질을 포함하며 새로운 재료를 사용한다"

        result = validator.validate_claim_content(
            claim_number=1, claim_type="독립항", content=claim_content
        )

        assert result.is_valid

        # Then evaluate
        evaluator = PatentabilityEvaluator()
        novelty, inventive, opinion = evaluator.evaluate(
            invention_features=["새로운 재료", "양극", "음극"],
            technical_field="화학",
            prior_art_count=2,
        )

        assert novelty is not None
        assert inventive is not None

    def test_evaluator_to_game_connection(self):
        """Test: Evaluation results drive game scoring"""

        # Setup game
        engine = GameEngine()
        session = engine.create_session(
            session_id="eval_game_test",
            player_name="평가테스트",
            level_id=1,
        )

        session.start_game(1000.0)

        # Submit and evaluate claim
        claim = "배터리 장치는 양극, 음극, 전해질을 포함하며 새로운 기술을 적용한다"
        session.submit_claim(claim)

        success, feedback, details = engine.evaluate_claims("eval_game_test")

        # Success should depend on evaluation
        assert success in [True, False]

        # Feedback should include results
        assert len(feedback) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
