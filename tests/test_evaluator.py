"""
Patent Evaluator 테스트

신규성 및 진보성 평가 엔진을 테스트합니다.
"""

import pytest
from src.dsl.logic.evaluator import (
    PriorArt,
    NoveltyEvaluator,
    InventiveStepEvaluator,
    PatentabilityEvaluator,
    EvaluationLevel,
)


class TestPriorArt:
    """PriorArt 클래스 테스트"""

    def test_create_prior_art(self):
        """선행기술 생성"""
        prior_art = PriorArt(
            title="배터리 기술",
            disclosure_date="2020-01-01",
            technical_field="전기화학",
            key_features=["양극", "음극", "전해질"],
        )

        assert prior_art.title == "배터리 기술"
        assert prior_art.disclosure_date == "2020-01-01"

    def test_empty_title_fails(self):
        """빈 제목은 실패"""
        with pytest.raises(ValueError):
            PriorArt(
                title="",
                disclosure_date="2020-01-01",
                technical_field="전기화학",
            )

    def test_empty_technical_field_fails(self):
        """빈 기술분야는 실패"""
        with pytest.raises(ValueError):
            PriorArt(
                title="배터리 기술",
                disclosure_date="2020-01-01",
                technical_field="",
            )


class TestNoveltyEvaluator:
    """NoveltyEvaluator 클래스 테스트"""

    def test_evaluator_creation(self):
        """평가 엔진 생성"""
        evaluator = NoveltyEvaluator()

        assert evaluator is not None
        assert len(evaluator.prior_art_database) == 0

    def test_add_prior_art(self):
        """선행기술 추가"""
        evaluator = NoveltyEvaluator()

        prior_art = PriorArt(
            title="기존 배터리",
            disclosure_date="2020-01-01",
            technical_field="전기화학",
            key_features=["양극", "음극"],
        )

        evaluator.add_prior_art(prior_art)

        assert len(evaluator.prior_art_database) == 1

    def test_evaluate_novel_invention(self):
        """신규한 발명 평가"""
        evaluator = NoveltyEvaluator()

        prior_art = PriorArt(
            title="기존 배터리",
            disclosure_date="2020-01-01",
            technical_field="전기화학",
            key_features=["양극", "음극"],
        )

        evaluator.add_prior_art(prior_art)

        # 선행기술과 다른 특징
        result = evaluator.evaluate(["고에너지밀도", "빠른충전", "안전"])

        assert result.is_novel is True
        assert result.level == EvaluationLevel.PASS

    def test_evaluate_non_novel_invention(self):
        """신규성이 없는 발명 평가"""
        evaluator = NoveltyEvaluator()

        prior_art = PriorArt(
            title="기존 배터리",
            disclosure_date="2020-01-01",
            technical_field="전기화학",
            key_features=["양극", "음극", "전해질"],
        )

        evaluator.add_prior_art(prior_art)

        # 선행기술과 같은 특징
        result = evaluator.evaluate(["양극", "음극", "전해질"])

        assert result.is_novel is False
        assert result.level == EvaluationLevel.FAIL

    def test_evaluate_empty_features(self):
        """빈 특징 리스트 평가"""
        evaluator = NoveltyEvaluator()

        result = evaluator.evaluate([])

        assert result.is_novel is True

    def test_add_invalid_prior_art(self):
        """유효하지 않은 선행기술 추가"""
        evaluator = NoveltyEvaluator()

        with pytest.raises(TypeError):
            evaluator.add_prior_art("not a prior art")


class TestInventiveStepEvaluator:
    """InventiveStepEvaluator 클래스 테스트"""

    def test_evaluator_creation(self):
        """평가 엔진 생성"""
        evaluator = InventiveStepEvaluator()

        assert evaluator is not None
        assert len(evaluator.technical_field_complexity) > 0

    def test_evaluate_high_inventive_step(self):
        """높은 진보성 평가"""
        evaluator = InventiveStepEvaluator()

        result = evaluator.evaluate(
            invention_features=["특징1", "특징2", "특징3", "특징4", "특징5"],
            technical_field="소프트웨어",
            prior_art_count=3,
        )

        assert result.has_inventive_step is True

    def test_evaluate_low_inventive_step(self):
        """낮은 진보성 평가"""
        evaluator = InventiveStepEvaluator()

        result = evaluator.evaluate(
            invention_features=["특징1"],
            technical_field="기계",
            prior_art_count=0,
        )

        assert result.has_inventive_step is False or (
            result.has_inventive_step and result.level == EvaluationLevel.CONDITIONAL
        )

    def test_evaluate_conditional_inventive_step(self):
        """조건부 진보성 평가"""
        evaluator = InventiveStepEvaluator()

        result = evaluator.evaluate(
            invention_features=["특징1", "특징2", "특징3"],
            technical_field="전자기술",
            prior_art_count=1,
        )

        assert result.level in [
            EvaluationLevel.CONDITIONAL,
            EvaluationLevel.PASS,
        ]

    def test_evaluate_empty_features(self):
        """빈 특징 리스트 평가"""
        evaluator = InventiveStepEvaluator()

        result = evaluator.evaluate(
            invention_features=[],
            technical_field="전자기술",
        )

        assert result.has_inventive_step is False


class TestPatentabilityEvaluator:
    """PatentabilityEvaluator 클래스 테스트"""

    def test_evaluator_creation(self):
        """평가 엔진 생성"""
        evaluator = PatentabilityEvaluator()

        assert evaluator is not None
        assert evaluator.novelty_evaluator is not None
        assert evaluator.inventive_step_evaluator is not None

    def test_evaluate_patentable_invention(self):
        """특허 가능한 발명 평가"""
        evaluator = PatentabilityEvaluator()

        novelty_result, inventive_step_result, opinion = evaluator.evaluate(
            invention_features=["특징1", "특징2", "특징3", "특징4"],
            technical_field="소프트웨어",
            prior_art_count=2,
        )

        assert novelty_result.is_novel is True
        assert inventive_step_result.has_inventive_step is True
        assert "✅" in opinion

    def test_evaluate_non_patentable_invention(self):
        """특허 불가능한 발명 평가"""
        evaluator = PatentabilityEvaluator()

        # 선행기술 추가
        prior_art = PriorArt(
            title="기존 기술",
            disclosure_date="2020-01-01",
            technical_field="전자기술",
            key_features=["특징1", "특징2"],
        )

        evaluator.novelty_evaluator.add_prior_art(prior_art)

        novelty_result, inventive_step_result, opinion = evaluator.evaluate(
            invention_features=["특징1", "특징2"],
            technical_field="전자기술",
            prior_art_count=1,
        )

        assert novelty_result.is_novel is False
        assert "❌" in opinion

    def test_evaluate_novelty_but_no_inventive_step(self):
        """신규성은 있지만 진보성이 없는 발명"""
        evaluator = PatentabilityEvaluator()

        novelty_result, inventive_step_result, opinion = evaluator.evaluate(
            invention_features=["특징1"],
            technical_field="기계",
            prior_art_count=0,
        )

        assert "⚠️" in opinion or "❌" in opinion


class TestPatentEvaluationScenarios:
    """실제 특허 평가 시나리오"""

    def test_battery_invention_evaluation(self):
        """배터리 발명 평가"""
        evaluator = PatentabilityEvaluator()

        # 기존 배터리 기술 추가
        prior_art1 = PriorArt(
            title="리튬이온 배터리",
            disclosure_date="2010-01-01",
            technical_field="전기화학",
            key_features=["양극", "음극", "전해질"],
        )

        prior_art2 = PriorArt(
            title="고에너지밀도 배터리",
            disclosure_date="2015-01-01",
            technical_field="전기화학",
            key_features=["양극", "음극", "전해질", "높은에너지밀도"],
        )

        evaluator.novelty_evaluator.add_prior_art(prior_art1)
        evaluator.novelty_evaluator.add_prior_art(prior_art2)

        # 신규한 배터리 기술 평가
        novelty, inventive_step, opinion = evaluator.evaluate(
            invention_features=[
                "양극",
                "음극",
                "전해질",
                "높은에너지밀도",
                "빠른충전",
                "안전",
            ],
            technical_field="전기화학",
            prior_art_count=2,
        )

        assert novelty.is_novel is True
        print(f"신규성: {novelty}")
        print(f"진보성: {inventive_step}")
        print(f"의견: {opinion}")

    def test_software_invention_evaluation(self):
        """소프트웨어 발명 평가"""
        evaluator = PatentabilityEvaluator()

        novelty, inventive_step, opinion = evaluator.evaluate(
            invention_features=[
                "머신러닝",
                "자연어처리",
                "신경망",
                "최적화알고리즘",
            ],
            technical_field="소프트웨어",
            prior_art_count=3,
        )

        assert novelty.is_novel is True
        assert inventive_step.has_inventive_step is True
        print(f"신규성: {novelty}")
        print(f"진보성: {inventive_step}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
