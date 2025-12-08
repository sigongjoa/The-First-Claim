"""
Hybrid Patent Evaluator - 하이브리드 평가 엔진 (규칙 + RAG + LLM)

세 단계 평가 시스템:
1. 규칙 기반: 빠른 필터링 (Jaccard 유사도)
2. RAG 기반: 의미론적 검색 (벡터 DB)
3. LLM 기반: 최종 판단 (Ollama)
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from src.config.evaluation_config import get_evaluation_config
from src.dsl.logic.evaluator import (
    NoveltyEvaluationResult,
    InventiveStepEvaluationResult,
    EvaluationLevel,
    PriorArt
)
from src.dsl.logic.claim_parser import ClaimComponentParser, ParsedClaim
from src.knowledge_base.rag_system import RAGSystem

logger = logging.getLogger(__name__)


@dataclass
class RAGSearchResult:
    """RAG 검색 결과"""
    content: str
    source: str
    similarity: float
    article_number: Optional[str] = None


@dataclass
class HybridNoveltyResult:
    """하이브리드 신규성 평가 결과"""
    is_novel: bool
    level: EvaluationLevel

    # 단계별 결과
    rule_based_score: float  # 규칙 기반 유사도
    rag_similarity: float  # RAG 의미론적 유사도
    llm_confidence: float  # LLM 신뢰도

    # 참고 정보
    matching_prior_art: List[str] = field(default_factory=list)
    rag_sources: List[RAGSearchResult] = field(default_factory=list)
    llm_reasoning: str = ""
    combined_reasoning: str = ""

    confidence_score: float = 0.0  # 최종 신뢰도 (0.0-1.0)

    def __str__(self) -> str:
        """사용자 친화적 표현"""
        status = "✅ 신규성 있음" if self.is_novel else "❌ 신규성 없음"
        return f"{status} (신뢰도: {self.confidence_score:.1%})"


@dataclass
class HybridInventiveStepResult:
    """하이브리드 진보성 평가 결과"""
    has_inventive_step: bool
    level: EvaluationLevel

    # 단계별 결과
    rule_based_score: float  # 규칙 기반 점수
    precedent_relevance: float  # 판례 관련성
    llm_judgment: float  # LLM 판단

    # 참고 정보
    analyzed_combinations: List[str] = field(default_factory=list)
    relevant_precedents: List[Dict] = field(default_factory=list)
    technical_difficulty: float = 0.0
    llm_reasoning: str = ""
    combined_reasoning: str = ""

    confidence_score: float = 0.0  # 최종 신뢰도

    def __str__(self) -> str:
        """사용자 친화적 표현"""
        status = "✅ 진보성 있음" if self.has_inventive_step else "❌ 진보성 없음"
        return f"{status} (신뢰도: {self.confidence_score:.1%})"


class HybridNoveltyEvaluator:
    """하이브리드 신규성 평가 엔진"""

    def __init__(self, rag_system: Optional[RAGSystem] = None):
        """
        하이브리드 신규성 평가기 초기화

        Args:
            rag_system: RAG 시스템 인스턴스
        """
        self.config = get_evaluation_config()
        self.rag_system = rag_system
        self.claim_parser = ClaimComponentParser()

    async def evaluate_novelty(
        self,
        claim_text: str,
        parsed_claim: Optional[ParsedClaim] = None
    ) -> HybridNoveltyResult:
        """
        청구항의 신규성을 하이브리드 방식으로 평가

        Args:
            claim_text: 청구항 텍스트
            parsed_claim: 파싱된 청구항 (선택사항)

        Returns:
            HybridNoveltyResult
        """
        # 청구항 파싱
        if parsed_claim is None:
            parsed_claim = self.claim_parser.parse_claim(claim_text)

        # 단계 1: 규칙 기반 평가 (빠른 필터링)
        rule_score = await self._stage1_rule_based_evaluation(parsed_claim)

        # 단계 2: RAG 기반 의미론적 검색
        rag_results = []
        rag_similarity = 0.0
        if self.config.enable_rag and self.rag_system:
            rag_results, rag_similarity = await self._stage2_rag_evaluation(claim_text)

        # 단계 3: LLM 최종 판단 (필요시)
        llm_confidence = 0.0
        llm_reasoning = ""
        if self.config.enable_llm and self.rag_system and (rule_score > 0.5 or rag_similarity > 0.5):
            llm_confidence, llm_reasoning = await self._stage3_llm_judgment(
                claim_text, rag_results
            )

        # 최종 점수 계산
        final_is_novel, final_confidence, combined_reasoning = self._combine_scores(
            rule_score, rag_similarity, llm_confidence, llm_reasoning
        )

        return HybridNoveltyResult(
            is_novel=final_is_novel,
            level=EvaluationLevel.PASS if final_is_novel else EvaluationLevel.FAIL,
            rule_based_score=rule_score,
            rag_similarity=rag_similarity,
            llm_confidence=llm_confidence,
            rag_sources=rag_results,
            llm_reasoning=llm_reasoning,
            combined_reasoning=combined_reasoning,
            confidence_score=final_confidence
        )

    async def _stage1_rule_based_evaluation(self, parsed_claim: ParsedClaim) -> float:
        """
        단계 1: 규칙 기반 평가 (빠른 유사도 검사)

        Args:
            parsed_claim: 파싱된 청구항

        Returns:
            유사도 점수 (0.0-1.0)
        """
        # 정규화된 특징 사용
        features = parsed_claim.normalized_features

        if not features:
            return 0.0

        # 기본적으로는 0.0 반환 (실제로는 선행기술 DB와 비교)
        # 본 구현에서는 RAG 시스템으로 대체
        logger.debug(f"Rule-based evaluation: {len(features)} features")
        return 0.3  # 기본값

    async def _stage2_rag_evaluation(
        self, claim_text: str
    ) -> Tuple[List[RAGSearchResult], float]:
        """
        단계 2: RAG 기반 의미론적 검색

        Args:
            claim_text: 청구항 텍스트

        Returns:
            (검색 결과 리스트, 최대 유사도)
        """
        if not self.rag_system:
            return [], 0.0

        try:
            # RAG에서 관련 자료 검색
            query = f"특허 선행기술: {claim_text}"
            search_results = await self.rag_system.retrieve_context(
                query=query,
                top_k=self.config.novelty.vector_search_top_k,
                filters={"category": "특허법"}
            )

            # 결과 변환
            rag_results = []
            max_similarity = 0.0

            for result in search_results:
                rag_result = RAGSearchResult(
                    content=result.get("content", ""),
                    source=result.get("source", ""),
                    similarity=result.get("similarity", 0.0),
                    article_number=result.get("article_number")
                )
                rag_results.append(rag_result)
                max_similarity = max(max_similarity, rag_result.similarity)

            logger.debug(f"RAG search returned {len(rag_results)} results, max similarity: {max_similarity:.2f}")
            return rag_results, max_similarity

        except Exception as e:
            logger.error(f"RAG evaluation failed: {e}")
            return [], 0.0

    async def _stage3_llm_judgment(
        self,
        claim_text: str,
        rag_results: List[RAGSearchResult]
    ) -> Tuple[float, str]:
        """
        단계 3: LLM 최종 판단

        Args:
            claim_text: 청구항 텍스트
            rag_results: RAG 검색 결과

        Returns:
            (신뢰도, 판단 이유)
        """
        if not self.rag_system:
            return 0.0, ""

        try:
            # RAG 결과를 문맥으로 사용
            context = "\n".join([
                f"[{r.article_number or r.source}] {r.content[:200]}"
                for r in rag_results[:self.config.novelty.vector_search_top_k]
            ])

            # LLM 프롬프트
            prompt = f"""다음 청구항의 신규성을 평가하세요.

【청구항】
{claim_text}

【관련 선행기술 및 법률 조문】
{context if context else "관련 자료 없음"}

【판단 기준】
1. 동일한 기술구성이 존재하는가?
2. 기술적 특징이 명확히 구별되는가?
3. 선행기술과의 차이점은 무엇인가?

【응답 형식】
다음과 같이 JSON으로 응답하세요:
{{
    "is_novel": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "판단 이유",
    "key_differences": ["차이점1", "차이점2"]
}}
"""

            response = await self.rag_system.generate_answer(prompt)

            # 응답 파싱
            if isinstance(response, str):
                try:
                    result = json.loads(response)
                    confidence = result.get("confidence", 0.5)
                    reasoning = result.get("reasoning", "")
                    return confidence, reasoning
                except json.JSONDecodeError:
                    return 0.5, response

            return 0.5, str(response)

        except Exception as e:
            logger.error(f"LLM judgment failed: {e}")
            return 0.0, f"LLM 판단 실패: {str(e)}"

    def _combine_scores(
        self,
        rule_score: float,
        rag_similarity: float,
        llm_confidence: float,
        llm_reasoning: str
    ) -> Tuple[bool, float, str]:
        """
        세 가지 점수를 결합하여 최종 판단

        Args:
            rule_score: 규칙 기반 점수
            rag_similarity: RAG 의미론적 유사도
            llm_confidence: LLM 신뢰도
            llm_reasoning: LLM 이유

        Returns:
            (신규성 여부, 최종 신뢰도, 종합 이유)
        """
        # 가중치 적용
        rule_weight = 0.3 if self.config.enable_rule_based else 0.0
        rag_weight = 0.4 if self.config.enable_rag else 0.0
        llm_weight = 0.3 if self.config.enable_llm else 1.0

        # 정규화
        total_weight = rule_weight + rag_weight + llm_weight
        if total_weight > 0:
            rule_weight /= total_weight
            rag_weight /= total_weight
            llm_weight /= total_weight

        # 최종 점수 계산
        final_score = (
            rule_weight * rule_score +
            rag_weight * rag_similarity +
            llm_weight * llm_confidence
        )

        # 신규성 판단
        is_novel = final_score < self.config.novelty.min_similarity_threshold

        # 종합 이유
        combined_reasoning = f"규칙:{rule_score:.1%}, RAG:{rag_similarity:.1%}, LLM:{llm_confidence:.1%} → 최종: {final_score:.1%}"
        if llm_reasoning:
            combined_reasoning += f"\nLLM 판단: {llm_reasoning}"

        return is_novel, final_score, combined_reasoning


class HybridInventiveStepEvaluator:
    """하이브리드 진보성 평가 엔진"""

    def __init__(self, rag_system: Optional[RAGSystem] = None):
        """
        하이브리드 진보성 평가기 초기화

        Args:
            rag_system: RAG 시스템 인스턴스
        """
        self.config = get_evaluation_config()
        self.rag_system = rag_system

    async def evaluate_inventive_step(
        self,
        claim_text: str,
        technical_field: str
    ) -> HybridInventiveStepResult:
        """
        청구항의 진보성을 하이브리드 방식으로 평가

        Args:
            claim_text: 청구항 텍스트
            technical_field: 기술분야

        Returns:
            HybridInventiveStepResult
        """
        # 단계 1: 규칙 기반 평가
        rule_score = await self._stage1_rule_based_evaluation(technical_field)

        # 단계 2: 판례 검색 (RAG)
        precedents = []
        precedent_score = 0.0
        if self.config.enable_rag and self.rag_system:
            precedents, precedent_score = await self._stage2_precedent_search(claim_text)

        # 단계 3: LLM 최종 판단
        llm_judgment = 0.0
        llm_reasoning = ""
        if self.config.enable_llm and self.rag_system:
            llm_judgment, llm_reasoning = await self._stage3_llm_judgment(
                claim_text, precedents
            )

        # 최종 점수 계산
        has_inventive_step, confidence, combined_reasoning = self._combine_scores(
            rule_score, precedent_score, llm_judgment, llm_reasoning
        )

        return HybridInventiveStepResult(
            has_inventive_step=has_inventive_step,
            level=EvaluationLevel.PASS if has_inventive_step else EvaluationLevel.FAIL,
            rule_based_score=rule_score,
            precedent_relevance=precedent_score,
            llm_judgment=llm_judgment,
            relevant_precedents=precedents,
            llm_reasoning=llm_reasoning,
            combined_reasoning=combined_reasoning,
            confidence_score=confidence
        )

    async def _stage1_rule_based_evaluation(self, technical_field: str) -> float:
        """규칙 기반 진보성 평가"""
        complexity = self.config.inventive_step.technical_complexity.get(technical_field, 0.5)
        return min(1.0, complexity * 0.7 + 0.3)

    async def _stage2_precedent_search(
        self, claim_text: str
    ) -> Tuple[List[Dict], float]:
        """판례 데이터베이스 검색"""
        if not self.rag_system:
            return [], 0.0

        try:
            query = f"진보성 판단 기준: {claim_text}"
            results = await self.rag_system.retrieve_context(
                query=query,
                top_k=self.config.inventive_step.precedent_search_top_k,
                filters={"category": "판례"}
            )

            max_relevance = max([r.get("similarity", 0.0) for r in results], default=0.0)
            return results, max_relevance

        except Exception as e:
            logger.error(f"Precedent search failed: {e}")
            return [], 0.0

    async def _stage3_llm_judgment(
        self,
        claim_text: str,
        precedents: List[Dict]
    ) -> Tuple[float, str]:
        """LLM 진보성 최종 판단"""
        if not self.rag_system:
            return 0.0, ""

        try:
            # 판례 문맥 구성
            context = "\n".join([
                f"[{p.get('case_number', '미확인')}] {p.get('summary', '')[:200]}"
                for p in precedents[:3]
            ])

            prompt = f"""다음 청구항의 진보성을 평가하세요.

【청구항】
{claim_text}

【관련 판례】
{context if context else "관련 판례 없음"}

【판단 기준】
1. 선행기술로부터의 기술적 진보가 있는가?
2. 통상의 기술자가 쉽게 도출할 수 있는가?
3. 예측 불가능한 기술 효과가 있는가?

【응답 형식】
{{
    "has_inventive_step": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "판단 이유"
}}
"""

            response = await self.rag_system.generate_answer(prompt)

            if isinstance(response, str):
                try:
                    result = json.loads(response)
                    confidence = result.get("confidence", 0.5)
                    reasoning = result.get("reasoning", "")
                    return confidence, reasoning
                except json.JSONDecodeError:
                    return 0.5, response

            return 0.5, str(response)

        except Exception as e:
            logger.error(f"LLM judgment failed: {e}")
            return 0.0, f"LLM 판단 실패: {str(e)}"

    def _combine_scores(
        self,
        rule_score: float,
        precedent_score: float,
        llm_judgment: float,
        llm_reasoning: str
    ) -> Tuple[bool, float, str]:
        """세 가지 점수를 결합하여 최종 판단"""
        rule_weight = 0.4 if self.config.enable_rule_based else 0.0
        precedent_weight = 0.3 if self.config.enable_rag else 0.0
        llm_weight = 0.3 if self.config.enable_llm else 1.0

        total_weight = rule_weight + precedent_weight + llm_weight
        if total_weight > 0:
            rule_weight /= total_weight
            precedent_weight /= total_weight
            llm_weight /= total_weight

        final_score = (
            rule_weight * rule_score +
            precedent_weight * precedent_score +
            llm_weight * llm_judgment
        )

        has_inventive_step = final_score > 0.6

        combined_reasoning = f"규칙:{rule_score:.1%}, 판례:{precedent_score:.1%}, LLM:{llm_judgment:.1%} → 최종: {final_score:.1%}"
        if llm_reasoning:
            combined_reasoning += f"\nLLM 판단: {llm_reasoning}"

        return has_inventive_step, final_score, combined_reasoning
