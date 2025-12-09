"""
Patent Evaluator V2 - 실제 의미론적 분석 기반 평가 엔진

Sentence-BERT를 이용한 의미론적 유사도 계산으로 단순 Jaccard를 대체합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np


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
    full_text: str  # 전체 텍스트 (임베딩용)
    key_features: List[str] = field(default_factory=list)
    source: str = ""

    def __post_init__(self) -> None:
        """선행기술 검증"""
        if not self.title or not self.title.strip():
            raise ValueError("title은 비어있지 않아야 합니다")
        if not self.full_text or not self.full_text.strip():
            raise ValueError("full_text는 비어있지 않아야 합니다")


@dataclass
class NoveltyEvaluationResult:
    """신규성 평가 결과"""
    is_novel: bool
    level: EvaluationLevel
    matching_prior_art: List[str] = field(default_factory=list)
    similarity_scores: Dict[str, float] = field(default_factory=dict)  # 각 선행기술별 유사도
    max_similarity: float = 0.0
    reasoning: str = ""
    semantic_analysis: str = ""  # 의미론적 분석 결과

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현"""
        status = "✅ 신규성 있음" if self.is_novel else "❌ 신규성 없음"
        return f"{status} (최대 유사도: {self.max_similarity:.1%})"


@dataclass
class InventiveStepEvaluationResult:
    """진보성 평가 결과"""
    has_inventive_step: bool
    level: EvaluationLevel
    technical_difficulty: float = 0.0  # 0.0 ~ 1.0
    feature_complexity: float = 0.0  # 특징 복잡도
    reasoning: str = ""
    detailed_analysis: str = ""

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현"""
        status = "✅ 진보성 있음" if self.has_inventive_step else "❌ 진보성 없음"
        return f"{status} (기술난도: {self.technical_difficulty:.1%})"


class NoveltyEvaluatorV2:
    """신규성 평가 엔진 (Sentence-BERT 기반)"""

    def __init__(
        self,
        prior_art_database: Optional[List[PriorArt]] = None,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    ) -> None:
        """NoveltyEvaluatorV2 초기화

        Args:
            prior_art_database: 선행기술 데이터베이스
            model_name: 사용할 Sentence-BERT 모델명
        """
        self.prior_art_database: List[PriorArt] = (
            prior_art_database if prior_art_database else []
        )

        # Sentence-BERT 모델 로드
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            # 모델 다운로드 실패 시 대체
            print(f"⚠️  모델 로드 실패: {e}")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # 선행기술 임베딩 캐시
        self._prior_art_embeddings: Dict[str, np.ndarray] = {}
        self._encode_prior_arts()

    def _encode_prior_arts(self) -> None:
        """모든 선행기술 임베딩 생성"""
        for prior_art in self.prior_art_database:
            if prior_art.title not in self._prior_art_embeddings:
                embedding = self.model.encode(
                    prior_art.full_text,
                    convert_to_tensor=False
                )
                self._prior_art_embeddings[prior_art.title] = embedding

    def add_prior_art(self, prior_art: PriorArt) -> None:
        """선행기술 추가"""
        if not isinstance(prior_art, PriorArt):
            raise TypeError("prior_art은 PriorArt 타입이어야 합니다")
        self.prior_art_database.append(prior_art)

        # 임베딩 생성
        embedding = self.model.encode(prior_art.full_text, convert_to_tensor=False)
        self._prior_art_embeddings[prior_art.title] = embedding

    def evaluate(self, claim_text: str) -> NoveltyEvaluationResult:
        """청구항의 신규성 평가 (의미론적 분석)

        Args:
            claim_text: 청구항 전체 텍스트

        Returns:
            NoveltyEvaluationResult
        """
        if not claim_text or not claim_text.strip():
            return NoveltyEvaluationResult(
                is_novel=True,
                level=EvaluationLevel.PASS,
                reasoning="청구항 텍스트가 없어 평가할 수 없습니다",
            )

        # 청구항 임베딩
        claim_embedding = self.model.encode(claim_text, convert_to_tensor=False)

        matching_prior_art = []
        similarity_scores: Dict[str, float] = {}
        max_similarity = 0.0

        # 모든 선행기술과 비교 (코사인 유사도)
        for prior_art in self.prior_art_database:
            prior_embedding = self._prior_art_embeddings[prior_art.title]

            # 코사인 유사도 계산
            similarity = float(
                util.cos_sim(claim_embedding, prior_embedding)[0][0]
            )
            similarity_scores[prior_art.title] = similarity

            # 임계값(0.75) 이상이면 매칭
            if similarity > 0.75:
                matching_prior_art.append(prior_art.title)

            max_similarity = max(max_similarity, similarity)

        # 의미론적 분석
        semantic_analysis = self._analyze_similarity(
            claim_text, matching_prior_art, similarity_scores
        )

        # 결과 결정
        if matching_prior_art:
            return NoveltyEvaluationResult(
                is_novel=False,
                level=EvaluationLevel.FAIL,
                matching_prior_art=matching_prior_art,
                similarity_scores=similarity_scores,
                max_similarity=max_similarity,
                reasoning=f"다음 선행기술과 의미론적으로 유사합니다: "
                + ", ".join(matching_prior_art),
                semantic_analysis=semantic_analysis,
            )

        return NoveltyEvaluationResult(
            is_novel=True,
            level=EvaluationLevel.PASS,
            similarity_scores=similarity_scores,
            max_similarity=max_similarity,
            reasoning="기존 선행기술과 의미론적으로 다른 신규한 기술입니다",
            semantic_analysis=semantic_analysis,
        )

    def _analyze_similarity(
        self, claim_text: str, matching_arts: List[str], scores: Dict[str, float]
    ) -> str:
        """의미론적 유사도 분석

        Jaccard 유사도와 다르게, 동의어나 표현의 다양성을 이해함
        """
        if not matching_arts:
            return (
                "청구항이 기존 선행기술과 개념적으로 다릅니다. "
                "새로운 기술적 접근이 인정됩니다."
            )

        max_score = max(scores.values()) if scores else 0.0

        if max_score > 0.85:
            return (
                "청구항과 선행기술이 개념적으로 거의 동일합니다. "
                "구성요소, 기술적 효과, 문제 해결 방식이 본질적으로 같습니다."
            )
        elif max_score > 0.75:
            return (
                "청구항과 선행기술이 유사한 개념을 다루고 있습니다. "
                "동의어나 다른 표현을 사용했더라도 핵심 기술 사상이 겹칩니다."
            )
        else:
            return (
                "청구항이 선행기술의 일부 요소를 포함하지만, "
                "전체적인 기술 사상은 다릅니다."
            )


class InventiveStepEvaluatorV2:
    """진보성 평가 엔진 (개선판)"""

    def __init__(self) -> None:
        """InventiveStepEvaluatorV2 초기화"""
        # 기술 분야별 복잡도 (한국 특허청 기준)
        self.technical_field_complexity: Dict[str, float] = {
            "전자": 0.85,           # 높은 복잡도
            "통신": 0.85,
            "컴퓨터": 0.80,
            "소프트웨어": 0.75,
            "기계": 0.70,
            "화학": 0.90,           # 매우 높은 복잡도
            "의약": 0.92,
            "바이오": 0.90,
            "재료": 0.85,
            "디자인": 0.50,         # 낮은 복잡도
        }

    def evaluate(
        self,
        claim_text: str,
        technical_field: str,
        prior_art_count: int = 0,
    ) -> InventiveStepEvaluationResult:
        """청구항의 진보성 평가

        Args:
            claim_text: 청구항 전체 텍스트
            technical_field: 기술분야
            prior_art_count: 선행기술 개수

        Returns:
            InventiveStepEvaluationResult
        """
        if not claim_text or not claim_text.strip():
            return InventiveStepEvaluationResult(
                has_inventive_step=False,
                level=EvaluationLevel.FAIL,
                reasoning="청구항 텍스트가 없어 평가할 수 없습니다",
            )

        # 1. 기술 분야별 복잡도
        technical_difficulty = self.technical_field_complexity.get(
            technical_field, 0.5
        )

        # 2. 특징 복잡도 (청구항의 상세도)
        feature_complexity = self._calculate_feature_complexity(claim_text)

        # 3. 선행기술 거리 (얼마나 많은 선행기술이 있는가)
        prior_art_distance = min(1.0, (prior_art_count + 1) / 10)

        # 4. 최종 진보성 점수
        # 기술 분야 난도(40%) + 특징 복잡도(35%) + 선행기술 거리(25%)
        inventive_step_score = (
            technical_difficulty * 0.40
            + feature_complexity * 0.35
            + prior_art_distance * 0.25
        )

        # 결과 결정
        if inventive_step_score > 0.70:
            return InventiveStepEvaluationResult(
                has_inventive_step=True,
                level=EvaluationLevel.PASS,
                technical_difficulty=technical_difficulty,
                feature_complexity=feature_complexity,
                reasoning="충분한 기술적 진보성이 인정됩니다",
                detailed_analysis=self._generate_detailed_analysis(
                    technical_field, feature_complexity, prior_art_count
                ),
            )
        elif inventive_step_score > 0.50:
            return InventiveStepEvaluationResult(
                has_inventive_step=True,
                level=EvaluationLevel.CONDITIONAL,
                technical_difficulty=technical_difficulty,
                feature_complexity=feature_complexity,
                reasoning="조건부로 진보성이 인정될 수 있습니다",
                detailed_analysis=self._generate_detailed_analysis(
                    technical_field, feature_complexity, prior_art_count
                ),
            )

        return InventiveStepEvaluationResult(
            has_inventive_step=False,
            level=EvaluationLevel.FAIL,
            technical_difficulty=technical_difficulty,
            feature_complexity=feature_complexity,
            reasoning="선행기술로부터의 기술적 진보가 부족합니다",
            detailed_analysis=self._generate_detailed_analysis(
                technical_field, feature_complexity, prior_art_count
            ),
        )

    def _calculate_feature_complexity(self, claim_text: str) -> float:
        """청구항의 특징 복잡도 계산

        - 기술용어의 다양성
        - 구성요소의 개수
        - 상호작용 수준
        """
        # 기본 특징 추출
        technical_terms = [
            "장치", "방법", "시스템", "구조", "과정",
            "프로세스", "알고리즘", "모듈", "부품", "요소",
        ]

        feature_count = sum(1 for term in technical_terms if term in claim_text)

        # 청구항 길이도 복잡도에 영향 (짧으면 단순, 길면 복잡)
        length_score = min(1.0, len(claim_text) / 500)

        # 특징 개수 점수
        feature_score = min(1.0, feature_count / 8 * 0.6)

        # 복합도 (AND, OR, 함께 등의 관계표현)
        relationship_score = 0.3 if "및" in claim_text or "그리고" in claim_text else 0.1

        return (length_score * 0.4 + feature_score * 0.3 + relationship_score * 0.3)

    def _generate_detailed_analysis(
        self, technical_field: str, feature_complexity: float, prior_art_count: int
    ) -> str:
        """상세 분석 생성"""
        analysis = f"기술분야: {technical_field} | "
        analysis += f"특징복잡도: {feature_complexity:.1%} | "
        analysis += f"선행기술: {prior_art_count}건\n"

        if feature_complexity > 0.7:
            analysis += "- 청구항이 다양한 기술적 요소를 포함하고 있습니다.\n"

        if prior_art_count <= 2:
            analysis += "- 선행기술이 매우 적어 진보성 인정 가능성이 높습니다.\n"

        return analysis
