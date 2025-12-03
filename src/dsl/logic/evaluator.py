"""
Patent Evaluator - 특허 신규성 및 진보성 평가 엔진

발명의 신규성과 진보성을 평가합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class EvaluationLevel(Enum):
    """평가 레벨"""

    PASS = "pass"  # 통과
    CONDITIONAL = "conditional"  # 조건부
    FAIL = "fail"  # 미통과


@dataclass
class PriorArt:
    """선행기술"""

    title: str
    disclosure_date: str  # YYYY-MM-DD
    technical_field: str
    key_features: List[str] = field(default_factory=list)
    source: str = ""

    def __post_init__(self) -> None:
        """선행기술 검증"""
        if not self.title or not self.title.strip():
            raise ValueError("title은 비어있지 않아야 합니다")
        if not self.disclosure_date or not self.disclosure_date.strip():
            raise ValueError("disclosure_date는 비어있지 않아야 합니다")
        if not self.technical_field or not self.technical_field.strip():
            raise ValueError("technical_field는 비어있지 않아야 합니다")


@dataclass
class NoveltyEvaluationResult:
    """신규성 평가 결과"""

    is_novel: bool
    level: EvaluationLevel
    matching_prior_art: List[str] = field(default_factory=list)
    similarity_score: float = 0.0  # 0.0 ~ 1.0
    reasoning: str = ""

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현"""
        status = "✅ 신규성 있음" if self.is_novel else "❌ 신규성 없음"
        return f"{status} (유사도: {self.similarity_score:.1%})"


@dataclass
class InventiveStepEvaluationResult:
    """진보성 평가 결과"""

    has_inventive_step: bool
    level: EvaluationLevel
    analyzed_combinations: List[str] = field(default_factory=list)
    technical_difficulty: float = 0.0  # 0.0 ~ 1.0
    reasoning: str = ""

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현"""
        status = "✅ 진보성 있음" if self.has_inventive_step else "❌ 진보성 없음"
        return f"{status} (기술난도: {self.technical_difficulty:.1%})"


class NoveltyEvaluator:
    """신규성 평가 엔진"""

    def __init__(self, prior_art_database: Optional[List[PriorArt]] = None) -> None:
        """NoveltyEvaluator 초기화

        Args:
            prior_art_database: 선행기술 데이터베이스
        """
        self.prior_art_database: List[PriorArt] = (
            prior_art_database if prior_art_database else []
        )

    def add_prior_art(self, prior_art: PriorArt) -> None:
        """선행기술 추가"""
        if not isinstance(prior_art, PriorArt):
            raise TypeError("prior_art은 PriorArt 타입이어야 합니다")
        self.prior_art_database.append(prior_art)

    def evaluate(self, invention_features: List[str]) -> NoveltyEvaluationResult:
        """발명의 신규성 평가

        Args:
            invention_features: 발명의 기술적 특징들

        Returns:
            NoveltyEvaluationResult
        """
        if not invention_features:
            return NoveltyEvaluationResult(
                is_novel=True,
                level=EvaluationLevel.PASS,
                reasoning="기술적 특징이 없어 평가할 수 없습니다",
            )

        matching_prior_art = []
        max_similarity = 0.0

        # 선행기술과 비교
        for prior_art in self.prior_art_database:
            similarity = self._calculate_similarity(
                invention_features, prior_art.key_features
            )

            if similarity > 0.7:  # 70% 이상 유사하면 매칭
                matching_prior_art.append(prior_art.title)

            max_similarity = max(max_similarity, similarity)

        # 결과 결정
        if matching_prior_art:
            return NoveltyEvaluationResult(
                is_novel=False,
                level=EvaluationLevel.FAIL,
                matching_prior_art=matching_prior_art,
                similarity_score=max_similarity,
                reasoning=f"다음 선행기술과 {max_similarity:.1%} 유사합니다: "
                + ", ".join(matching_prior_art),
            )

        return NoveltyEvaluationResult(
            is_novel=True,
            level=EvaluationLevel.PASS,
            similarity_score=max_similarity,
            reasoning="기존 선행기술과 다른 신규한 기술입니다",
        )

    @staticmethod
    def _calculate_similarity(features1: List[str], features2: List[str]) -> float:
        """두 특징 세트 간의 유사도 계산

        Args:
            features1: 첫 번째 특징 리스트
            features2: 두 번째 특징 리스트

        Returns:
            유사도 (0.0 ~ 1.0)
        """
        if not features1 or not features2:
            return 0.0

        set1 = set(features1)
        set2 = set(features2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union


class InventiveStepEvaluator:
    """진보성 평가 엔진"""

    def __init__(self) -> None:
        """InventiveStepEvaluator 초기화"""
        self.technical_field_complexity: Dict[str, float] = {
            "전기화학": 0.7,
            "전자기술": 0.8,
            "기계": 0.5,
            "화학": 0.8,
            "소프트웨어": 0.9,
            "생명공학": 0.9,
        }

    def evaluate(
        self,
        invention_features: List[str],
        technical_field: str,
        prior_art_count: int = 0,
    ) -> InventiveStepEvaluationResult:
        """발명의 진보성 평가

        Args:
            invention_features: 발명의 기술적 특징들
            technical_field: 기술분야
            prior_art_count: 선행기술 개수

        Returns:
            InventiveStepEvaluationResult
        """
        if not invention_features:
            return InventiveStepEvaluationResult(
                has_inventive_step=False,
                level=EvaluationLevel.FAIL,
                reasoning="기술적 특징이 없어 평가할 수 없습니다",
            )

        # 기술 난도 계산
        technical_difficulty = self.technical_field_complexity.get(technical_field, 0.5)

        # 특징의 개수와 복잡도 고려
        feature_complexity = min(1.0, len(invention_features) / 10 * 0.3)
        technical_difficulty += feature_complexity

        # 선행기술과의 거리 계산
        prior_art_distance = min(1.0, (prior_art_count + 1) / 10)

        # 최종 진보성 점수
        inventive_step_score = technical_difficulty * 0.6 + prior_art_distance * 0.4

        # 결과 결정
        if inventive_step_score > 0.6:
            return InventiveStepEvaluationResult(
                has_inventive_step=True,
                level=EvaluationLevel.PASS,
                technical_difficulty=inventive_step_score,
                reasoning="충분한 기술적 진보성이 인정됩니다",
            )
        elif inventive_step_score > 0.4:
            return InventiveStepEvaluationResult(
                has_inventive_step=True,
                level=EvaluationLevel.CONDITIONAL,
                technical_difficulty=inventive_step_score,
                reasoning="조건부로 진보성이 인정될 수 있습니다",
            )

        return InventiveStepEvaluationResult(
            has_inventive_step=False,
            level=EvaluationLevel.FAIL,
            technical_difficulty=inventive_step_score,
            reasoning="선행기술로부터의 기술적 진보가 부족합니다",
        )


class PatentabilityEvaluator:
    """특허성 종합 평가 엔진"""

    def __init__(
        self,
        novelty_evaluator: Optional[NoveltyEvaluator] = None,
        inventive_step_evaluator: Optional[InventiveStepEvaluator] = None,
    ) -> None:
        """PatentabilityEvaluator 초기화"""
        self.novelty_evaluator = novelty_evaluator or NoveltyEvaluator()
        self.inventive_step_evaluator = (
            inventive_step_evaluator or InventiveStepEvaluator()
        )

    def evaluate(
        self,
        invention_features: List[str],
        technical_field: str,
        prior_art_count: int = 0,
    ) -> Tuple[
        NoveltyEvaluationResult,
        InventiveStepEvaluationResult,
        str,
    ]:
        """발명의 특허성 종합 평가

        Args:
            invention_features: 발명의 기술적 특징들
            technical_field: 기술분야
            prior_art_count: 선행기술 개수

        Returns:
            (신규성 평가, 진보성 평가, 종합 의견)
        """
        novelty_result = self.novelty_evaluator.evaluate(invention_features)
        inventive_step_result = self.inventive_step_evaluator.evaluate(
            invention_features, technical_field, prior_art_count
        )

        # 종합 의견 생성
        overall_opinion = self._generate_overall_opinion(
            novelty_result, inventive_step_result
        )

        return novelty_result, inventive_step_result, overall_opinion

    @staticmethod
    def _generate_overall_opinion(
        novelty_result: NoveltyEvaluationResult,
        inventive_step_result: InventiveStepEvaluationResult,
    ) -> str:
        """종합 의견 생성"""
        if novelty_result.is_novel and inventive_step_result.has_inventive_step:
            return "✅ 특허 등록 가능성 높음 (신규성 O, 진보성 O)"
        elif novelty_result.is_novel and not inventive_step_result.has_inventive_step:
            return "⚠️  재검토 필요 (신규성 O, 진보성 X)"
        elif not novelty_result.is_novel:
            return "❌ 특허 등록 불가능 (신규성 부재)"
        else:
            return "⚠️  조건부 검토 필요"
