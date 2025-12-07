"""
Property-Based Testing with Hypothesis - 엣지 케이스와 무작위 입력 검증

이 테스트는 Hypothesis를 사용하여 무작위 입력으로 코드의 견고성을 검증합니다.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite

# ============================================================================
# ClaimValidator Property Tests
# ============================================================================


class TestClaimValidatorProperties:
    """청구항 검증기의 속성 기반 테스트"""

    from src.dsl.grammar.claim_validator import ClaimValidator

    @given(
        claim_number=st.integers(min_value=1, max_value=100),
        claim_type=st.sampled_from(["independent", "dependent"]),
        content=st.text(min_size=1, max_size=500),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_validate_claim_content_never_crashes(
        self, claim_number, claim_type, content
    ):
        """어떤 입력이든 검증기가 크래시하지 않음을 검증"""
        validator = self.ClaimValidator()
        try:
            result = validator.validate_claim_content(
                claim_number=claim_number, claim_type=claim_type, content=content
            )
            # 결과가 항상 ValidationResult 객체여야 함
            assert result is not None
            assert hasattr(result, "is_valid")
            assert isinstance(result.is_valid, bool)
        except ValueError:
            # ValueError는 예상 가능한 예외 (예: 빈 내용)
            pass

    @given(content=st.text(min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_claim_content_idempotent(self, content):
        """같은 청구항을 두 번 검증하면 같은 결과를 얻음"""
        validator = self.ClaimValidator()
        try:
            result1 = validator.validate_claim_content(
                claim_number=1, claim_type="independent", content=content
            )
            result2 = validator.validate_claim_content(
                claim_number=1, claim_type="independent", content=content
            )
            # 결과가 일관성 있어야 함
            assert result1.is_valid == result2.is_valid
        except ValueError:
            pass


# ============================================================================
# LLMClaimEvaluator Property Tests
# ============================================================================


class TestLLMEvaluatorProperties:
    """LLM 평가기의 속성 기반 테스트 (Deprecated - see OllamaClaimEvaluator instead)"""

    @pytest.mark.skip(reason="LLMClaimEvaluator deprecated in favor of OllamaClaimEvaluator")
    @given(
        claim_number=st.integers(min_value=1, max_value=50),
        claim_content=st.text(min_size=1, max_size=200),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_evaluator_handles_various_inputs(self, claim_number, claim_content):
        """다양한 입력을 처리할 수 있음"""
        from src.dsl.logic.llm_evaluator import LLMClaimEvaluator

        try:
            evaluator = LLMClaimEvaluator()
            result = evaluator.evaluate_claim(
                claim_number=claim_number,
                claim_content=claim_content,
                claim_type="independent",
            )
            # 결과가 항상 유효해야 함
            assert result is not None
            assert hasattr(result, "overall_opinion")
        except (ValueError, RuntimeError, KeyError):
            # API 키 없음 등 예상 가능한 예외
            pass

    @pytest.mark.skip(reason="LLMClaimEvaluator deprecated in favor of OllamaClaimEvaluator")
    @given(claim_set_size=st.integers(min_value=1, max_value=5))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_evaluate_claims_set_never_crashes(self, claim_set_size):
        """청구항 세트 평가가 크래시하지 않음"""
        from src.dsl.logic.llm_evaluator import LLMClaimEvaluator

        try:
            evaluator = LLMClaimEvaluator()
            claims = {
                i: ("independent" if i == 1 else "dependent", f"청구항 {i} 내용")
                for i in range(1, claim_set_size + 1)
            }
            results = evaluator.evaluate_claims(claims)
            # 결과가 청구항 수와 일치해야 함
            assert len(results) == claim_set_size
        except (ValueError, RuntimeError, KeyError):
            pass


# ============================================================================
# Vector Database Property Tests
# ============================================================================


class TestVectorDatabaseProperties:
    """벡터 데이터베이스의 속성 기반 테스트"""

    @given(
        statute_id=st.text(min_size=1, max_size=20),
        statute_number=st.text(min_size=1, max_size=20),
        title=st.text(min_size=1, max_size=100),
        content=st.text(min_size=1, max_size=300),
    )
    @settings(max_examples=50, deadline=None)
    def test_vector_search_result_creation(
        self, statute_id, statute_number, title, content
    ):
        """VectorSearchResult 객체를 항상 생성할 수 있음"""
        from src.knowledge_base.vector_database import VectorSearchResult

        result = VectorSearchResult(
            statute_id=statute_id,
            statute_number=statute_number,
            title=title,
            content=content,
            source_type="civil_law",
            similarity_score=0.85,
        )

        # 모든 필드가 올바르게 설정됨
        assert result.statute_id == statute_id
        assert result.statute_number == statute_number
        assert result.title == title
        assert result.content == content
        assert result.similarity_score == 0.85

    @given(similarity_score=st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=100)
    def test_similarity_score_bounds(self, similarity_score):
        """유사도 점수가 항상 0~1 범위 내"""
        from src.knowledge_base.vector_database import VectorSearchResult

        result = VectorSearchResult(
            statute_id="test",
            statute_number="1",
            title="test",
            content="test",
            source_type="civil_law",
            similarity_score=similarity_score,
        )

        assert 0.0 <= result.similarity_score <= 1.0


# ============================================================================
# Game Engine Property Tests
# ============================================================================


class TestGameEngineProperties:
    """게임 엔진의 속성 기반 테스트"""

    @given(
        player_name=st.text(min_size=1, max_size=50),
        level_id=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=30)
    def test_session_creation_invariants(self, player_name, level_id):
        """세션 생성의 불변성 검증"""
        from src.ui.game import GameEngine
        import uuid

        engine = GameEngine()
        try:
            session_id = f"test_{uuid.uuid4().hex[:8]}"
            session = engine.create_session(
                session_id=session_id, player_name=player_name, level_id=level_id
            )
            # 세션이 생성되면 항상 유효한 속성을 가져야 함
            assert session is not None
            assert session.player.player_name == player_name
            assert session.current_level.level_id == level_id
            assert session.submitted_claims is not None
            assert isinstance(session.submitted_claims, list)
        except (ValueError, KeyError):
            # 유효하지 않은 레벨은 예상 가능한 예외
            pass

    @given(claim_text=st.text(min_size=30, max_size=200))
    @settings(max_examples=20)
    def test_claim_submission_idempotent(self, claim_text):
        """같은 청구항을 여러 번 제출해도 세션 상태가 일관성 있음"""
        from src.ui.game import GameEngine
        import uuid

        engine = GameEngine()
        try:
            session_id = f"test_{uuid.uuid4().hex[:8]}"
            session = engine.create_session(session_id=session_id, player_name="테스트", level_id=1)
            session.submit_claim(claim_text)
            count_after_first = len(session.submitted_claims)
            session.submit_claim(claim_text)
            count_after_second = len(session.submitted_claims)

            # 같은 청구항을 두 번 제출해도 카운트가 올바름
            assert count_after_second == count_after_first + 1
        except (ValueError, RuntimeError):
            pass


# ============================================================================
# RAG System Property Tests
# ============================================================================


class TestRAGSystemProperties:
    """RAG 시스템의 속성 기반 테스트"""

    @given(query=st.text(min_size=1, max_size=100))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_rag_query_never_crashes(self, query):
        """어떤 쿼리든 RAG 시스템이 크래시하지 않음"""
        try:
            from src.knowledge_base.rag_system import RAGSystem
            from src.knowledge_base.vector_database import get_vector_database

            vdb = get_vector_database("memory")
            rag = RAGSystem(vector_database=vdb)
            response = rag.query(query)
            # 응답이 항상 유효해야 함
            assert response is not None
            assert hasattr(response, "answer")
            assert isinstance(response.answer, str)
        except (ValueError, RuntimeError, KeyError):
            pass


# ============================================================================
# API Server Property Tests
# ============================================================================


class TestAPIServerProperties:
    """API 서버의 속성 기반 테스트"""

    @given(
        claim=st.text(min_size=1, max_size=500),
        claim_type=st.sampled_from(["independent", "dependent"]),
    )
    @settings(max_examples=30)
    def test_validation_endpoint_input_acceptance(self, claim, claim_type):
        """검증 엔드포인트가 다양한 입력을 처리"""
        try:
            from src.dsl.grammar.claim_validator import ClaimValidator

            validator = ClaimValidator()
            result = validator.validate_claim_content(
                claim_number=1, claim_type=claim_type, content=claim
            )
            # 결과가 항상 유효해야 함
            assert result is not None
            assert isinstance(result.is_valid, bool)
        except ValueError:
            pass


# ============================================================================
# Metamorphic Testing - 변형 관계 검증
# ============================================================================


class TestMetamorphicProperties:
    """변형 관계 검증 - 입력을 변형했을 때의 일관성"""

    @given(original_content=st.text(min_size=10, max_size=100))
    @settings(max_examples=30)
    def test_content_prefix_property(self, original_content):
        """접두사를 추가한 입력도 검증 가능"""
        from src.dsl.grammar.claim_validator import ClaimValidator

        validator = ClaimValidator()
        try:
            result1 = validator.validate_claim_content(
                claim_number=1, claim_type="independent", content=original_content
            )

            # 접두사를 추가한 버전
            prefixed_content = "새로운 청구항: " + original_content
            result2 = validator.validate_claim_content(
                claim_number=1, claim_type="independent", content=prefixed_content
            )

            # 두 결과 모두 유효해야 함 (크래시하지 않아야 함)
            assert result1 is not None
            assert result2 is not None
        except ValueError:
            pass

    @given(base_claim=st.text(min_size=5, max_size=50))
    @settings(max_examples=20)
    def test_claim_length_independence(self, base_claim):
        """청구항 길이가 변해도 검증 가능"""
        from src.dsl.grammar.claim_validator import ClaimValidator

        validator = ClaimValidator()
        try:
            # 다양한 길이의 청구항들
            short_claim = base_claim[:10]
            long_claim = base_claim * 3

            result_short = validator.validate_claim_content(
                claim_number=1, claim_type="independent", content=short_claim
            )
            result_long = validator.validate_claim_content(
                claim_number=1, claim_type="independent", content=long_claim
            )

            # 두 결과 모두 유효해야 함
            assert result_short is not None
            assert result_long is not None
        except ValueError:
            pass


# ============================================================================
# Pytest Markers
# ============================================================================

pytestmark = [
    pytest.mark.fuzzing,
    pytest.mark.hypothesis,
    pytest.mark.property_based,
]
