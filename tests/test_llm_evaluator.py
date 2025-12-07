"""
LLM Evaluator Tests - LLM 기반 평가 엔진 테스트

Claude API를 이용한 청구항 평가 테스트
"""

import pytest
from src.dsl.logic.llm_evaluator import (
    LLMEvaluationResult,
    KoreanPatentLawContext,
    EvaluationCritera,
)


class TestEvaluationCritera:
    """평가 기준 테스트"""

    def test_clarity_criteria(self):
        """명확성 기준"""
        assert EvaluationCritera.CLARITY.value == "명확성"

    def test_antecedent_basis_criteria(self):
        """선행기술 기준"""
        assert EvaluationCritera.ANTECEDENT_BASIS.value == "선행기술"

    def test_novelty_criteria(self):
        """신규성 기준"""
        assert EvaluationCritera.NOVELTY.value == "신규성"


class TestKoreanPatentLawContext:
    """한국 특허법 컨텍스트 테스트"""

    def test_articles_exist(self):
        """특허법 조항 존재"""
        assert len(KoreanPatentLawContext.ARTICLES) > 0

    def test_key_article_42(self):
        """제42조 명확성"""
        assert "제42조" in KoreanPatentLawContext.ARTICLES
        assert "명확" in KoreanPatentLawContext.ARTICLES["제42조"]

    def test_key_article_32(self):
        """제32조 신규성"""
        assert "제32조" in KoreanPatentLawContext.ARTICLES

    def test_examination_guidelines(self):
        """심사기준 존재"""
        assert len(KoreanPatentLawContext.EXAMINATION_GUIDELINES) > 0

    def test_get_law_context(self):
        """법적 컨텍스트 생성"""
        context = KoreanPatentLawContext.get_law_context()
        assert "특허법" in context
        assert "제42조" in context


class TestLLMEvaluationResult:
    """LLM 평가 결과 테스트"""

    def test_create_result(self):
        """결과 생성"""
        result = LLMEvaluationResult(
            claim_number=1,
            claim_content="배터리는 양극, 음극, 전해질을 포함한다",
            is_approvable=True,
            clarity_score=0.9,
            antecedent_basis_score=0.85,
            unity_score=0.8,
            definiteness_score=0.9,
            novelty_score=0.75,
            inventive_step_score=0.7,
            overall_opinion="등록 가능합니다",
            estimated_approval_probability=0.85,
        )

        assert result.claim_number == 1
        assert result.is_approvable is True
        assert result.clarity_score == 0.9

    def test_result_validation_clarity_score(self):
        """명확성 점수 검증"""
        with pytest.raises(ValueError):
            LLMEvaluationResult(
                claim_number=1,
                claim_content="테스트",
                is_approvable=True,
                clarity_score=1.5,  # 범위 초과
                antecedent_basis_score=0.8,
                unity_score=0.8,
                definiteness_score=0.8,
                novelty_score=0.8,
                inventive_step_score=0.8,
            )

    def test_result_validation_probability(self):
        """승인 확률 검증"""
        with pytest.raises(ValueError):
            LLMEvaluationResult(
                claim_number=1,
                claim_content="테스트",
                is_approvable=True,
                clarity_score=0.8,
                antecedent_basis_score=0.8,
                unity_score=0.8,
                definiteness_score=0.8,
                novelty_score=0.8,
                inventive_step_score=0.8,
                estimated_approval_probability=1.5,  # 범위 초과
            )

    def test_get_overall_score(self):
        """종합 점수 계산"""
        result = LLMEvaluationResult(
            claim_number=1,
            claim_content="테스트",
            is_approvable=True,
            clarity_score=1.0,
            antecedent_basis_score=1.0,
            unity_score=1.0,
            definiteness_score=1.0,
            novelty_score=1.0,
            inventive_step_score=1.0,
        )

        score = result.get_overall_score()
        assert score == 1.0  # 모든 점수가 1.0이면 종합 점수도 1.0

    def test_result_with_strengths_and_weaknesses(self):
        """강점과 약점 포함"""
        result = LLMEvaluationResult(
            claim_number=1,
            claim_content="테스트",
            is_approvable=False,
            clarity_score=0.5,
            antecedent_basis_score=0.6,
            unity_score=0.7,
            definiteness_score=0.8,
            novelty_score=0.4,
            inventive_step_score=0.3,
            strengths=["명확한 정의"],
            weaknesses=["신규성 부족", "진보성 부족"],
            improvements=["선행기술 조사", "명확성 개선"],
        )

        assert len(result.strengths) == 1
        assert len(result.weaknesses) == 2
        assert len(result.improvements) == 2

    def test_result_string_representation(self):
        """문자열 표현"""
        result = LLMEvaluationResult(
            claim_number=1,
            claim_content="테스트",
            is_approvable=True,
            clarity_score=0.8,
            antecedent_basis_score=0.8,
            unity_score=0.8,
            definiteness_score=0.8,
            novelty_score=0.8,
            inventive_step_score=0.8,
            estimated_approval_probability=0.8,
        )

        result_str = str(result)
        assert "청구항 1" in result_str
        assert "등록 가능" in result_str
        assert "80.0%" in result_str


class TestLLMEvaluatorIntegration:
    """LLM 평가기 통합 테스트"""

    def test_llm_evaluator_import(self):
        """LLM 평가기 임포트"""
        try:
            from src.dsl.logic.llm_evaluator import LLMClaimEvaluator

            assert LLMClaimEvaluator is not None
        except ImportError:
            pytest.skip("anthropic 패키지가 설치되지 않음")

    def test_get_llm_evaluator_function(self):
        """LLM 평가기 팩토리 함수"""
        try:
            from src.dsl.logic.llm_evaluator import get_llm_evaluator

            assert callable(get_llm_evaluator)
        except ImportError:
            pytest.skip("anthropic 패키지가 설치되지 않음")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
