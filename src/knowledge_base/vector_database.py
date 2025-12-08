"""
Vector Database Manager - 의미론적 검색을 위한 벡터 데이터베이스

이 모듈은 법률 조문과 판례를 벡터화하여 저장하고,
의미론적 검색(semantic search)을 수행합니다.
"""

from __future__ import annotations

import os
import json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Ollama API 기본 URL
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")


class VectorDbType(Enum):
    """벡터 데이터베이스 타입"""

    PINECONE = "pinecone"
    CHROMADB = "chromadb"
    MEMORY = "memory"  # 개발용 메모리 DB


@dataclass
class VectorSearchResult:
    """벡터 검색 결과"""

    statute_id: str
    statute_number: str
    title: str
    content: str
    source_type: str  # "civil_law" 또는 "patent_law"
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None

    def __repr__(self) -> str:
        return (
            f"VectorSearchResult(statute_number='{self.statute_number}', "
            f"similarity={self.similarity_score:.3f})"
        )


class EmbeddingManager:
    """Ollama를 사용한 로컬 임베딩 생성 (OpenAI 없이)"""

    def __init__(self, model: str = "nomic-embed-text"):
        """
        임베딩 매니저 초기화

        Args:
            model: Ollama 임베딩 모델
                - nomic-embed-text (권장, 빠르고 효율적)
                - mxbai-embed-large (더 나은 성능)
        """
        self.model = model
        self.ollama_url = OLLAMA_API_URL
        logger.info(f"Ollama 임베딩 매니저 초기화: {self.ollama_url}, 모델: {self.model}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_embedding(self, text: str) -> List[float]:
        """
        텍스트를 벡터로 변환 (Ollama 사용)

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (리스트)

        Raises:
            ValueError: API 호출 실패 시
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("텍스트가 비어있습니다")

            # Ollama API 호출
            response = requests.post(
                f"{self.ollama_url}/api/embed",
                json={"model": self.model, "input": text},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            if "embeddings" not in data or len(data["embeddings"]) == 0:
                raise ValueError("임베딩 응답이 비어있습니다")

            embedding = data["embeddings"][0]
            logger.info(f"임베딩 생성: 모델={self.model}, 차원={len(embedding)}")
            return embedding

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama 연결 실패: {e}. Ollama가 실행 중인지 확인하세요: {self.ollama_url}")
            raise ValueError(f"Ollama 서버에 연결할 수 없습니다: {self.ollama_url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API 오류: {e}")
            raise ValueError(f"임베딩 생성 실패: {str(e)}")
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise ValueError(f"임베딩 생성 중 오류 발생: {str(e)}")

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 배치로 벡터화 (Ollama 사용)

        Args:
            texts: 임베딩할 텍스트 목록

        Returns:
            임베딩 벡터 목록
        """
        try:
            # Ollama API 호출 (배치)
            response = requests.post(
                f"{self.ollama_url}/api/embed",
                json={"model": self.model, "input": texts},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            if "embeddings" not in data:
                raise ValueError("임베딩 응답이 비어있습니다")

            embeddings = data["embeddings"]
            logger.info(f"배치 임베딩 생성: {len(texts)}개 항목, 차원={len(embeddings[0]) if embeddings else 0}")
            return embeddings

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama 연결 실패: {e}")
            raise ValueError(f"Ollama 서버에 연결할 수 없습니다")
        except Exception as e:
            logger.error(f"배치 임베딩 실패: {e}")
            raise ValueError(f"배치 임베딩 생성 중 오류 발생: {str(e)}")


class MemoryVectorDatabase:
    """개발용 메모리 기반 벡터 데이터베이스"""

    def __init__(self):
        """메모리 벡터 DB 초기화"""
        self.vectors: Dict[str, Tuple[List[float], Dict]] = {}
        self.embedding_manager = EmbeddingManager()

    def add_statute(
        self,
        statute_id: str,
        statute_number: str,
        title: str,
        content: str,
        source_type: str = "civil_law",
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        조문을 벡터 DB에 추가

        Args:
            statute_id: 조문 ID
            statute_number: 조문 번호
            title: 제목
            content: 내용
            source_type: 출처 타입
            metadata: 메타데이터
        """
        # 조문 텍스트 조합
        text_to_embed = f"{statute_number} {title} {content}"

        # 임베딩 생성
        embedding = self.embedding_manager.get_embedding(text_to_embed)

        # 메타데이터 저장
        meta = {
            "statute_id": statute_id,
            "statute_number": statute_number,
            "title": title,
            "content": content,
            "source_type": source_type,
            **(metadata or {}),
        }

        self.vectors[statute_id] = (embedding, meta)
        logger.info(f"조문 추가: {statute_number}")

    def search(
        self, query: str, top_k: int = 5, source_type: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """
        의미론적 검색 수행

        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 결과 개수
            source_type: 출처 필터 (civil_law, patent_law, None)

        Returns:
            검색 결과 리스트
        """
        if not self.vectors:
            logger.warning("벡터 DB가 비어있습니다")
            return []

        # 쿼리 임베딩 생성
        query_embedding = self.embedding_manager.get_embedding(query)

        # 유사도 계산 (코사인 유사도)
        similarities = []
        for statute_id, (vector, metadata) in self.vectors.items():
            if source_type and metadata.get("source_type") != source_type:
                continue

            similarity = self._cosine_similarity(query_embedding, vector)
            similarities.append((statute_id, similarity, metadata))

        # 유사도 순으로 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 상위 k개 반환
        results = []
        for statute_id, similarity, metadata in similarities[:top_k]:
            result = VectorSearchResult(
                statute_id=statute_id,
                statute_number=metadata["statute_number"],
                title=metadata["title"],
                content=metadata["content"],
                source_type=metadata["source_type"],
                similarity_score=similarity,
                metadata=metadata,
            )
            results.append(result)

        logger.info(f"검색 완료: 쿼리='{query}', 결과={len(results)}개")
        return results

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        두 벡터의 코사인 유사도 계산

        Args:
            vec_a: 벡터 A
            vec_b: 벡터 B

        Returns:
            유사도 (0-1)
        """
        import math

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get_stats(self) -> Dict:
        """벡터 DB 통계 반환"""
        return {
            "total_vectors": len(self.vectors),
            "embedding_dimension": (
                len(next(iter(self.vectors.values()))[0]) if self.vectors else 0
            ),
        }


class VectorDatabaseManager:
    """벡터 데이터베이스 관리자 (팩토리 패턴)"""

    def __init__(self, db_type: VectorDbType = VectorDbType.MEMORY):
        """
        벡터 DB 매니저 초기화

        Args:
            db_type: 사용할 벡터 DB 타입
        """
        self.db_type = db_type

        if db_type == VectorDbType.MEMORY:
            self.db = MemoryVectorDatabase()
            logger.info("메모리 벡터 DB 초기화 완료")
        elif db_type == VectorDbType.CHROMADB:
            self._init_chromadb()
        elif db_type == VectorDbType.PINECONE:
            self._init_pinecone()
        else:
            raise ValueError(f"지원하지 않는 DB 타입: {db_type}")

    def _init_chromadb(self):
        """ChromaDB 초기화"""
        try:
            import chromadb

            self.db = chromadb.Client()
            logger.info("ChromaDB 초기화 완료")
        except ImportError:
            raise ImportError("chromadb를 설치해주세요: pip install chromadb")

    def _init_pinecone(self):
        """Pinecone 초기화"""
        try:
            from pinecone import Pinecone

            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY 환경 변수가 설정되지 않았습니다")

            self.db = Pinecone(api_key=api_key)
            logger.info("Pinecone 초기화 완료")
        except ImportError:
            raise ImportError(
                "pinecone-client를 설치해주세요: pip install pinecone-client"
            )

    def add_statute(self, **kwargs) -> None:
        """조문 추가 (DB 타입별 구현)"""
        if self.db_type == VectorDbType.MEMORY:
            self.db.add_statute(**kwargs)
        else:
            # Pinecone, ChromaDB 등 다른 구현
            pass

    def search(self, query: str, top_k: int = 5, **kwargs) -> List[VectorSearchResult]:
        """의미론적 검색 (DB 타입별 구현)"""
        if self.db_type == VectorDbType.MEMORY:
            return self.db.search(query, top_k, **kwargs)
        else:
            # Pinecone, ChromaDB 등 다른 구현
            return []

    def get_stats(self) -> Dict:
        """벡터 DB 통계"""
        if hasattr(self.db, "get_stats"):
            return self.db.get_stats()
        return {}


# 글로벌 벡터 DB 인스턴스 (싱글톤)
_vector_db_instance: Optional[VectorDatabaseManager] = None


def get_vector_database(
    db_type: VectorDbType = VectorDbType.MEMORY,
) -> VectorDatabaseManager:
    """
    벡터 데이터베이스 싱글톤 인스턴스 획득

    Args:
        db_type: 벡터 DB 타입

    Returns:
        VectorDatabaseManager 인스턴스
    """
    global _vector_db_instance
    if _vector_db_instance is None:
        _vector_db_instance = VectorDatabaseManager(db_type)
    return _vector_db_instance
