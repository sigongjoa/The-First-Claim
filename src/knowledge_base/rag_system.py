"""
RAG (Retrieval-Augmented Generation) System - 의미론적 검색 기반 LLM 답변

이 모듈은 벡터 DB에서 관련 자료를 검색하고,
LLM이 검색된 컨텍스트를 기반으로 답변을 생성합니다.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

from .vector_database import (
    VectorDatabaseManager,
    VectorSearchResult,
    get_vector_database,
)
from ..dsl.logic.llm_evaluator import LLMClaimEvaluator

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """RAG 컨텍스트 (검색 결과)"""

    query: str
    search_results: List[VectorSearchResult]
    formatted_context: str

    def __repr__(self) -> str:
        return (
            f"RAGContext(query='{self.query[:50]}...', "
            f"results={len(self.search_results)})"
        )


@dataclass
class RAGResponse:
    """RAG 응답"""

    query: str
    answer: str
    context: RAGContext
    sources: List[str]
    confidence: float

    def __repr__(self) -> str:
        return (
            f"RAGResponse(confidence={self.confidence:.2f}, "
            f"sources={len(self.sources)})"
        )


class RAGSystem:
    """
    RAG (Retrieval-Augmented Generation) 시스템

    벡터 DB에서 관련 자료를 검색하고,
    LLM이 검색된 자료를 기반으로 더 정확한 답변을 생성합니다.
    """

    def __init__(
        self,
        vector_db: Optional[VectorDatabaseManager] = None,
        llm_evaluator: Optional[LLMClaimEvaluator] = None,
        search_k: int = 5,
    ):
        """
        RAG 시스템 초기화

        Args:
            vector_db: 벡터 데이터베이스 (None이면 기본값 사용)
            llm_evaluator: LLM 평가기 (None이면 기본값 사용)
            search_k: 검색 결과 상위 k개
        """
        self.vector_db = vector_db or get_vector_database()
        self.llm_evaluator = llm_evaluator or LLMClaimEvaluator()
        self.search_k = search_k

        logger.info(f"RAG 시스템 초기화 완료 (search_k={search_k})")

    def retrieve_context(
        self, query: str, source_type: Optional[str] = None
    ) -> RAGContext:
        """
        쿼리와 관련된 문서 검색

        Args:
            query: 검색 쿼리
            source_type: 출처 필터 (civil_law, patent_law, None)

        Returns:
            RAGContext (검색 결과 + 포맷된 컨텍스트)
        """
        logger.info(f"RAG 검색 시작: query='{query}'")

        # 벡터 DB에서 검색
        search_results = self.vector_db.search(
            query=query, top_k=self.search_k, source_type=source_type
        )

        # 컨텍스트 포맷팅
        formatted_context = self._format_context(search_results)

        context = RAGContext(
            query=query,
            search_results=search_results,
            formatted_context=formatted_context,
        )

        logger.info(f"RAG 검색 완료: {len(search_results)}개 결과")
        return context

    def generate_answer(self, query: str, context: RAGContext) -> RAGResponse:
        """
        검색된 컨텍스트를 기반으로 LLM이 답변 생성

        Args:
            query: 원본 쿼리
            context: RAG 컨텍스트

        Returns:
            RAGResponse (답변 + 소스)
        """
        logger.info(f"RAG 답변 생성: query='{query}'")

        # LLM 프롬프트 구성
        prompt = self._construct_prompt(query, context)

        # LLM으로 답변 생성
        try:
            llm_result = self.llm_evaluator.evaluate_claim(
                claim_number=0,
                claim_content=query,
                claim_type="independent",
                prior_claims=None,
            )
            answer = llm_result.overall_opinion
        except Exception as e:
            logger.warning(f"LLM 답변 생성 실패: {e}")
            answer = f"답변 생성 중 오류 발생했습니다. 검색된 자료를 참고하세요."

        # 소스 추출
        sources = [result.statute_number for result in context.search_results]

        # 신뢰도 계산 (검색 결과 유사도 평균)
        if context.search_results:
            avg_similarity = sum(
                r.similarity_score for r in context.search_results
            ) / len(context.search_results)
            confidence = min(avg_similarity, 1.0)
        else:
            confidence = 0.0

        response = RAGResponse(
            query=query,
            answer=answer,
            context=context,
            sources=sources,
            confidence=confidence,
        )

        logger.info(f"RAG 답변 생성 완료 (신뢰도={confidence:.2f})")
        return response

    def query(self, query: str, source_type: Optional[str] = None) -> RAGResponse:
        """
        RAG 쿼리 실행 (Retrieve + Generate)

        Args:
            query: 쿼리
            source_type: 출처 필터

        Returns:
            RAGResponse
        """
        # 1단계: 검색 (Retrieve)
        context = self.retrieve_context(query, source_type)

        # 2단계: 생성 (Generate)
        response = self.generate_answer(query, context)

        return response

    def _format_context(self, search_results: List[VectorSearchResult]) -> str:
        """
        검색 결과를 포맷팅된 컨텍스트로 변환

        Args:
            search_results: 검색 결과 목록

        Returns:
            포맷된 컨텍스트 문자열
        """
        if not search_results:
            return "관련 자료를 찾을 수 없습니다."

        formatted_lines = []
        formatted_lines.append("### 관련 법률 조문 및 자료\n")

        for i, result in enumerate(search_results, 1):
            formatted_lines.append(f"{i}. [{result.statute_number}] {result.title}")
            formatted_lines.append(f"   유사도: {result.similarity_score:.1%}")
            formatted_lines.append(f"   내용: {result.content[:200]}...")
            formatted_lines.append("")

        return "\n".join(formatted_lines)

    def _construct_prompt(self, query: str, context: RAGContext) -> str:
        """
        RAG 기반 LLM 프롬프트 구성

        Args:
            query: 쿼리
            context: RAG 컨텍스트

        Returns:
            프롬프트 문자열
        """
        prompt = f"""
다음은 법률 전문가로서 답변해야 할 질문입니다.

### 질문
{query}

### 관련 법률 자료
{context.formatted_context}

### 답변 지침
1. 위의 관련 자료를 바탕으로 답변하세요
2. 구체적인 조문 번호와 함께 설명하세요
3. 명확하고 논리적인 구조로 답변하세요
4. 법적 개념을 정확히 사용하세요

### 답변
"""
        return prompt

    def evaluate_claim_with_rag(self, claim: str) -> Dict:
        """
        청구항을 RAG 기반으로 평가

        Args:
            claim: 청구항

        Returns:
            평가 결과 딕셔너리
        """
        logger.info(f"RAG 기반 청구항 평가: {claim[:50]}...")

        # RAG로 답변 생성
        rag_response = self.query(claim, source_type="patent_law")

        result = {
            "claim": claim,
            "answer": rag_response.answer,
            "sources": rag_response.sources,
            "confidence": rag_response.confidence,
            "context": {
                "query_count": len(rag_response.context.search_results),
                "top_source": (
                    rag_response.context.search_results[0].statute_number
                    if rag_response.context.search_results
                    else None
                ),
            },
        }

        return result


# 글로벌 RAG 시스템 인스턴스
_rag_system_instance: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """
    RAG 시스템 싱글톤 인스턴스 획득

    Returns:
        RAGSystem 인스턴스
    """
    global _rag_system_instance
    if _rag_system_instance is None:
        _rag_system_instance = RAGSystem()
    return _rag_system_instance
