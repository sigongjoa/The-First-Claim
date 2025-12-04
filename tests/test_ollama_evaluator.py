"""
Ollama-Based Evaluator Tests - 실제 LLM 평가 테스트 (에러 숨김 없음)

Ollama 로컬 서버를 사용한 실제 청구항 평가 테스트
- pytest.skip() 없음: 실제 실패 메시지 표시
- try-except 없음: 에러 명시적 전파
"""

import pytest
from src.dsl.logic.ollama_evaluator import (
    OllamaClaimEvaluator,
    OllamaEvaluationResult,
)


class TestOllamaEvaluatorSetup:
    """Ollama 평가기 설정 테스트"""

    def test_evaluator_initialization(self):
        """평가기 초기화"""
        evaluator = OllamaClaimEvaluator()
        assert evaluator.base_url == "http://localhost:11434"
        assert evaluator.model == "qwen2:7b"

    def test_custom_model(self):
        """커스텀 모델 설정"""
        evaluator = OllamaClaimEvaluator(model="llama2:latest")
        assert evaluator.model == "llama2:latest"

    def test_ollama_availability(self):
        """Ollama 서버 사용 가능 여부 - 실패하면 명시적으로 실패"""
        evaluator = OllamaClaimEvaluator()
        # is_available()이 False를 반환하면 명시적으로 실패
        # pytest.skip() 없음 - 실제 상태를 보여줌
        is_available = evaluator.is_available()
        assert is_available, "❌ Ollama 서버가 실행 중이 아닙니다. http://localhost:11434 확인하세요."
        print(f"✅ Ollama 서버 사용 가능")


class TestOllamaEvaluationResult:
    """Ollama 평가 결과 테스트"""

    def test_create_result(self):
        """결과 생성"""
        result = OllamaEvaluationResult(
            claim_number=1,
            claim_content="배터리는 양극, 음극을 포함한다",
            is_approvable=True,
            clarity_score=0.85,
            antecedent_basis_score=0.80,
            unity_score=0.75,
            definiteness_score=0.80,
            novelty_score=0.70,
            inventive_step_score=0.65,
        )

        assert result.claim_number == 1
        assert result.is_approvable is True

    def test_overall_score_calculation(self):
        """종합 점수 계산"""
        result = OllamaEvaluationResult(
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
        assert score == 1.0


class TestOllamaClaimEvaluation:
    """Ollama를 사용한 실제 청구항 평가 테스트 - 에러 숨김 없음"""

    @pytest.fixture
    def evaluator(self):
        """평가기 초기화 - Ollama 서버 필수 (skip 없음)"""
        evaluator = OllamaClaimEvaluator()
        # is_available()이 False면 명시적 AssertionError (skip 아님)
        assert evaluator.is_available(), (
            "❌ Ollama 서버 연결 실패\n"
            "다음을 확인하세요:\n"
            "1. Ollama 서버 실행 중: ollama serve\n"
            "2. 주소 확인: http://localhost:11434\n"
            "3. 모델 설치 확인: ollama pull qwen2:7b"
        )
        return evaluator

    def test_single_claim_evaluation(self, evaluator):
        """단일 청구항 평가 - 실제 LLM 호출"""
        result = evaluator.evaluate_claim(
            claim_number=1,
            claim_content="배터리 장치는 양극, 음극, 전해질을 포함하는 에너지 저장 장치이다",
            claim_type="independent",
        )

        assert result.claim_number == 1
        assert isinstance(result.clarity_score, float)
        assert 0.0 <= result.clarity_score <= 1.0
        assert isinstance(result.is_approvable, bool)

        print(f"\n📝 청구항 1 평가:")
        print(f"   상태: {'✅ 등록 가능' if result.is_approvable else '❌ 등록 불가'}")
        print(f"   종합 점수: {result.get_overall_score():.2f}/1.0")
        print(f"   의견: {result.overall_opinion}")

    def test_multiple_claims_evaluation(self, evaluator):
        """다중 청구항 평가"""
        claims = {
            1: ("independent", "배터리 장치는 양극, 음극, 전해질을 포함한다"),
            2: ("dependent", "제1항의 배터리에서 양극은 리튬 산화물로 이루어진다"),
        }

        results = evaluator.evaluate_claims(claims)

        assert len(results) == 2
        assert results[0].claim_number == 1
        assert results[1].claim_number == 2
        assert results[1].clarity_score <= 1.0

        print(f"\n📝 다중 청구항 평가:")
        for result in results:
            print(f"   청구항 {result.claim_number}: {result.get_overall_score():.2f}/1.0")

    def test_edge_case_very_short_claim(self, evaluator):
        """엣지 케이스: 매우 짧은 청구항"""
        result = evaluator.evaluate_claim(
            claim_number=1,
            claim_content="배터리",
            claim_type="independent",
        )

        assert result.is_approvable is not None
        print(f"\n⚠️  짧은 청구항 평가: {result.get_overall_score():.2f}/1.0")

    def test_edge_case_ambiguous_claim(self, evaluator):
        """엣지 케이스: 모호한 표현이 있는 청구항"""
        result = evaluator.evaluate_claim(
            claim_number=1,
            claim_content="배터리 장치는 여러 요소 등을 포함할 수 있다",
            claim_type="independent",
        )

        assert result is not None
        print(f"\n⚠️  모호한 청구항 평가: {result.get_overall_score():.2f}/1.0")

    def test_dependent_claim_evaluation(self, evaluator):
        """엣지 케이스: 종속항 평가"""
        result = evaluator.evaluate_claim(
            claim_number=2,
            claim_content="제1항의 배터리에서 양극은 리튬 함유 산화물로 이루어진다",
            claim_type="dependent",
            prior_claims=["배터리 장치는 양극, 음극, 전해질을 포함한다"],
        )

        assert result.claim_number == 2
        assert isinstance(result.antecedent_basis_score, float)
        print(f"\n📝 종속항 평가: {result.get_overall_score():.2f}/1.0")

    def test_prompt_building(self, evaluator):
        """프롬프트 생성 테스트"""
        prompt = evaluator._build_evaluation_prompt(
            claim_number=1,
            claim_content="배터리는 양극과 음극을 포함한다",
            claim_type="independent",
            prior_claims=None,
        )

        assert "청구항 번호: 1" in prompt
        assert "독립항" in prompt
        assert "제42조" in prompt
        print(f"\n📋 프롬프트 길이: {len(prompt)} 글자")


class TestOllamaEdgeCases:
    """Ollama 평가의 엣지 케이스 테스트 - skip 없음"""

    @pytest.fixture
    def evaluator(self):
        """평가기 초기화 - 실패하면 명시적으로 AssertionError"""
        evaluator = OllamaClaimEvaluator()
        assert evaluator.is_available(), (
            "❌ Ollama 서버 연결 실패\n"
            "다음을 확인하세요:\n"
            "1. Ollama 서버 실행 중: ollama serve\n"
            "2. 주소 확인: http://localhost:11434\n"
            "3. 모델 설치 확인: ollama pull qwen2:7b"
        )
        return evaluator

    def test_very_long_claim(self, evaluator):
        """엣지 케이스: 매우 긴 청구항"""
        long_claim = "배터리 장치는 " + "양극, " * 50 + "음극과 전해질을 포함한다"

        result = evaluator.evaluate_claim(
            claim_number=1,
            claim_content=long_claim,
            claim_type="independent",
        )

        assert result is not None
        assert isinstance(result.clarity_score, float)
        print(f"\n📏 매우 긴 청구항 평가: {result.get_overall_score():.2f}/1.0")

    def test_claim_with_special_characters(self, evaluator):
        """엣지 케이스: 특수 문자 포함"""
        claim = "배터리 장치는 양극, 음극, 전해질을 포함한다. (예: Li-ion)"

        result = evaluator.evaluate_claim(
            claim_number=1,
            claim_content=claim,
            claim_type="independent",
        )

        assert result is not None
        print(f"\n🔤 특수 문자 포함 평가: {result.get_overall_score():.2f}/1.0")

    def test_circular_dependent_claim(self, evaluator):
        """엣지 케이스: 순환 참조"""
        result = evaluator.evaluate_claim(
            claim_number=3,
            claim_content="제2항의 배터리에서 제1항의 양극은",
            claim_type="dependent",
            prior_claims=[
                "배터리 장치는 양극, 음극을 포함한다",
                "제1항의 배터리에서 양극은 리튬 산화물이다",
            ],
        )

        assert result is not None
        print(f"\n🔄 복잡한 종속 관계 평가: {result.get_overall_score():.2f}/1.0")


class TestOllamaUseCase:
    """Ollama 평가의 실제 사용 사례 테스트 - skip 없음"""

    @pytest.fixture
    def evaluator(self):
        """평가기 초기화"""
        evaluator = OllamaClaimEvaluator()
        assert evaluator.is_available(), (
            "❌ Ollama 서버 연결 실패\n"
            "다음을 확인하세요:\n"
            "1. Ollama 서버 실행 중: ollama serve\n"
            "2. 주소 확인: http://localhost:11434\n"
            "3. 모델 설치 확인: ollama pull qwen2:7b"
        )
        return evaluator

    def test_use_case_battery_patent(self, evaluator):
        """사용 사례: 배터리 특허 청구항"""
        battery_claims = {
            1: ("independent",
                "고성능 리튬 배터리 장치는 양극 단자, 음극 단자, 전해질, "
                "분리막을 포함하고, 상기 양극은 리튬코발트산화물로 이루어진다"),
            2: ("dependent",
                "제1항의 배터리 장치에서 음극은 흑연 재료로 이루어진다"),
            3: ("dependent",
                "제1항의 배터리 장치에서 전해질은 유기용매에 용해된 리튬염이다"),
        }

        results = evaluator.evaluate_claims(battery_claims)

        assert len(results) == 3
        print(f"\n🔋 배터리 특허 청구항 평가 결과:")
        for result in results:
            print(f"   청구항 {result.claim_number}: "
                  f"{'✅' if result.is_approvable else '❌'} "
                  f"({result.get_overall_score():.2f}/1.0)")

    def test_use_case_method_patent(self, evaluator):
        """사용 사례: 방법 특허 청구항"""
        method_claim = (
            "배터리 제조 방법은 다음 단계를 포함한다: "
            "1) 양극 재료 준비, 2) 음극 재료 준비, "
            "3) 전해질 제조, 4) 배터리 조립"
        )

        result = evaluator.evaluate_claim(
            claim_number=1,
            claim_content=method_claim,
            claim_type="independent",
        )

        assert result is not None
        print(f"\n🛠️  방법 특허 청구항 평가: {result.get_overall_score():.2f}/1.0")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
