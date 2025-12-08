"""
PROJECT: OVERRIDE - FastAPI 서버

주요 기능:
- 청구항 검증 API
- 청구항 평가 API
- 의미론적 검색 API
- 게임 세션 API
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging
import threading
import uuid

from ..dsl.grammar.claim_validator import ClaimValidator
from ..dsl.logic.ollama_evaluator import OllamaClaimEvaluator
from ..knowledge_base.rag_system import get_rag_system
from ..knowledge_base.vector_database import get_vector_database, VectorSearchResult
from ..ui.game import GameEngine, PlayerProgress
from ..utils.exceptions import (
    GameEngineException,
    SessionNotFoundException,
    ClaimValidationException,
    EvaluationTimeoutException,
    PersistenceException,
)
from ..storage.session_store import InMemorySessionStore

# ============================================================================
# 로깅 설정
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI 앱 생성
# ============================================================================

app = FastAPI(
    title="PROJECT: OVERRIDE API",
    description="변리사 시험 준비 법률 엔진 API",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic 모델 정의
# ============================================================================


class ClaimValidationRequest(BaseModel):
    """청구항 검증 요청"""

    claim: str = Field(..., min_length=1, max_length=1000)
    claim_type: Optional[str] = "independent"  # independent or dependent


class ClaimValidationResponse(BaseModel):
    """청구항 검증 응답"""

    claim: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]


class ClaimEvaluationRequest(BaseModel):
    """청구항 평가 요청"""

    claim: str = Field(..., min_length=1, max_length=1000)
    use_rag: bool = True  # RAG 사용 여부


class ClaimEvaluationResponse(BaseModel):
    """청구항 평가 응답"""

    claim: str
    evaluation: Dict
    sources: List[str]
    confidence: float


class SearchRequest(BaseModel):
    """검색 요청"""

    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)
    source_type: Optional[str] = None  # civil_law, patent_law, None


class SearchResult(BaseModel):
    """검색 결과"""

    statute_id: str
    statute_number: str
    title: str
    content: str
    source_type: str
    similarity_score: float


class SearchResponse(BaseModel):
    """검색 응답"""

    query: str
    results: List[SearchResult]
    total_results: int


class GameSessionRequest(BaseModel):
    """게임 세션 생성 요청"""

    player_name: str = Field(..., min_length=1, max_length=100)
    level_id: int = Field(..., ge=1, le=3)


class GameSessionResponse(BaseModel):
    """게임 세션 응답"""

    session_id: str
    player_name: str
    level_id: int
    status: str


class ClaimSubmissionRequest(BaseModel):
    """청구항 제출 요청"""

    session_id: str
    claim: str = Field(..., min_length=20, max_length=1000)


class ClaimSubmissionResponse(BaseModel):
    """청구항 제출 응답"""

    session_id: str
    claim_number: int
    is_valid: bool
    feedback: str


class HealthCheckResponse(BaseModel):
    """헬스 체크 응답"""

    status: str
    version: str
    components: Dict[str, str]


# ============================================================================
# 헬스 체크 엔드포인트
# ============================================================================


@app.get("/api/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    시스템 헬스 체크

    Returns:
        HealthCheckResponse: 시스템 상태
    """
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        components={
            "validator": "ready",
            "evaluator": "ready",
            "vector_db": "ready",
            "rag": "ready",
            "game_engine": "ready",
        },
    )


# ============================================================================
# 청구항 검증 엔드포인트
# ============================================================================


@app.post(
    "/api/claims/validate", response_model=ClaimValidationResponse, tags=["Claims"]
)
async def validate_claim(request: ClaimValidationRequest):
    """
    청구항 문법 검증

    Args:
        request: 검증 요청

    Returns:
        ClaimValidationResponse: 검증 결과

    Examples:
        POST /api/claims/validate
        {
            "claim": "컴퓨터 프로그램을 저장한 컴퓨터 읽기 가능 매체",
            "claim_type": "independent"
        }
    """
    try:
        validator = ClaimValidator()
        claim_type = request.claim_type or "independent"
        result = validator.validate_claim_content(
            claim_number=1, claim_type=claim_type, content=request.claim
        )

        return ClaimValidationResponse(
            claim=request.claim,
            is_valid=result.is_valid,
            errors=[str(e) for e in result.errors],
            warnings=[str(w) for w in result.warnings],
            info=[str(i) for i in result.info],
        )

    except Exception as e:
        logger.error(f"청구항 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# 청구항 평가 엔드포인트
# ============================================================================


@app.post(
    "/api/claims/evaluate", response_model=ClaimEvaluationResponse, tags=["Claims"]
)
async def evaluate_claim(request: ClaimEvaluationRequest):
    """
    청구항 평가 (신규성, 진보성, LLM 평가)

    Args:
        request: 평가 요청

    Returns:
        ClaimEvaluationResponse: 평가 결과

    Examples:
        POST /api/claims/evaluate
        {
            "claim": "20년 동안 타인의 토지를 점유하면 소유권을 취득할 수 있는가?",
            "use_rag": true
        }
    """
    try:
        sources = []
        evaluation = {}

        if request.use_rag:
            # RAG 기반 평가
            rag = get_rag_system()
            rag_response = rag.query(request.claim)
            evaluation = {
                "answer": rag_response.answer,
                "confidence": rag_response.confidence,
            }
            sources = rag_response.sources
        else:
            # LLM 기반 평가 (Ollama)
            evaluator = OllamaClaimEvaluator()
            result = evaluator.evaluate_claim(
                claim_number=1,
                claim_content=request.claim,
                claim_type="independent",
                prior_claims=None,
            )
            evaluation = {
                "answer": result.overall_opinion,
                "confidence": result.estimated_approval_probability,
            }
            sources = result.relevant_articles

        return ClaimEvaluationResponse(
            claim=request.claim,
            evaluation=evaluation,
            sources=sources,
            confidence=evaluation.get("confidence", 0.0),
        )

    except Exception as e:
        logger.error(f"청구항 평가 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# 의미론적 검색 엔드포인트
# ============================================================================


@app.get("/api/search", response_model=SearchResponse, tags=["Search"])
async def semantic_search(
    query: str = Query(..., min_length=1, max_length=500),
    top_k: int = Query(5, ge=1, le=20),
    source_type: Optional[str] = Query(None),
):
    """
    의미론적 검색

    Args:
        query: 검색 쿼리
        top_k: 반환할 상위 결과 개수
        source_type: 출처 필터 (civil_law, patent_law)

    Returns:
        SearchResponse: 검색 결과

    Examples:
        GET /api/search?query=취득시효&top_k=5&source_type=civil_law
    """
    try:
        vector_db = get_vector_database()
        results = vector_db.search(query=query, top_k=top_k, source_type=source_type)

        return SearchResponse(
            query=query,
            results=[
                SearchResult(
                    statute_id=r.statute_id,
                    statute_number=r.statute_number,
                    title=r.title,
                    content=r.content[:200],  # 요약
                    source_type=r.source_type,
                    similarity_score=r.similarity_score,
                )
                for r in results
            ],
            total_results=len(results),
        )

    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# 게임 세션 엔드포인트
# ============================================================================

# 세션 저장소 (프로덕션에서는 DB 사용)
# 스레드 안전 세션 저장소
_session_store = InMemorySessionStore()


@app.post("/api/game/session", response_model=GameSessionResponse, tags=["Game"])
async def create_game_session(request: GameSessionRequest):
    """
    게임 세션 생성

    Args:
        request: 세션 생성 요청

    Returns:
        GameSessionResponse: 세션 정보

    Examples:
        POST /api/game/session
        {
            "player_name": "변리사 준비생",
            "level_id": 1
        }
    """
    try:
        engine = GameEngine()

        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = engine.create_session(
            session_id=session_id,
            player_name=request.player_name,
            level_id=request.level_id,
        )

        # 세션 저장 (스레드 안전)
        _session_store.create(
            session_id,
            {
                "player_name": request.player_name,
                "level_id": request.level_id,
                "session": session,
            },
        )

        return GameSessionResponse(
            session_id=session_id,
            player_name=request.player_name,
            level_id=request.level_id,
            status="created",
        )

    except PersistenceException as e:
        logger.error(f"게임 세션 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        logger.error(f"게임 세션 생성 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/api/game/claim/submit", response_model=ClaimSubmissionResponse, tags=["Game"]
)
async def submit_claim(request: ClaimSubmissionRequest):
    """
    게임 세션에 청구항 제출

    Args:
        request: 제출 요청

    Returns:
        ClaimSubmissionResponse: 제출 결과

    Examples:
        POST /api/game/claim/submit
        {
            "session_id": "session_abc123",
            "claim": "청구항 내용..."
        }
    """
    try:
        # 세션 조회 (스레드 안전)
        session_data = _session_store.get(request.session_id)
        if session_data is None:
            raise SessionNotFoundException(request.session_id)

        session = session_data["session"]

        # 청구항 제출
        success = session.submit_claim(request.claim)

        if not success:
            feedback = "청구항 길이가 부적절합니다 (30-1000자)"
        else:
            feedback = f"청구항 {len(session.submitted_claims)}개 제출됨"

        # 세션 업데이트 (스레드 안전)
        _session_store.update(request.session_id, {"session": session})

        return ClaimSubmissionResponse(
            session_id=request.session_id,
            claim_number=len(session.submitted_claims),
            is_valid=success,
            feedback=feedback,
        )

    except SessionNotFoundException as e:
        logger.error(f"세션을 찾을 수 없습니다: {e}")
        raise HTTPException(status_code=404, detail=str(e.message))
    except Exception as e:
        logger.error(f"청구항 제출 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# 통계 엔드포인트
# ============================================================================


@app.get("/api/stats", tags=["Stats"])
async def get_stats():
    """
    시스템 통계

    Returns:
        시스템 통계 정보
    """
    try:
        vector_db = get_vector_database()
        stats = vector_db.get_stats()

        return {
            "vector_db": stats,
            "active_sessions": _session_store.count(),
            "system": "ready",
        }

    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("PROJECT: OVERRIDE API 서버 시작")
    logger.info("=" * 60)
    logger.info("📍 URL: http://localhost:8000")
    logger.info("📚 API 문서: http://localhost:8000/docs")
    logger.info("=" * 60)

    uvicorn.run(
        "src.api.server:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
