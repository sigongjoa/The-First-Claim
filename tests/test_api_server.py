"""
API Server Tests

FastAPI 서버의 모든 엔드포인트를 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api.server import app, _session_store

# ============================================================================
# TestClient 생성
# ============================================================================

client = TestClient(app)


# ============================================================================
# Health Check Tests
# ============================================================================


class TestHealthCheck:
    """헬스 체크 엔드포인트 테스트"""

    def test_health_check_success(self):
        """헬스 체크 성공"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "version" in data
        assert "components" in data
        assert data["components"]["validator"] == "ready"


# ============================================================================
# Claim Validation Tests
# ============================================================================


class TestClaimValidation:
    """청구항 검증 엔드포인트 테스트"""

    def test_validate_claim_valid(self):
        """유효한 청구항 검증"""
        response = client.post(
            "/api/claims/validate",
            json={
                "claim": "컴퓨터 프로그램을 저장한 컴퓨터 읽기 가능 매체",
                "claim_type": "independent",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "claim" in data
        assert "is_valid" in data
        assert "errors" in data
        assert "warnings" in data

    def test_validate_claim_empty(self):
        """빈 청구항"""
        response = client.post("/api/claims/validate", json={"claim": ""})

        assert response.status_code == 422  # Validation Error

    def test_validate_claim_too_long(self):
        """너무 긴 청구항"""
        long_claim = "a" * 1001

        response = client.post("/api/claims/validate", json={"claim": long_claim})

        assert response.status_code == 422


# ============================================================================
# Claim Evaluation Tests
# ============================================================================


class TestClaimEvaluation:
    """청구항 평가 엔드포인트 테스트"""

    @patch("src.api.server.OllamaClaimEvaluator")
    def test_evaluate_claim_without_rag(self, mock_evaluator_class):
        """RAG 없이 평가"""
        mock_evaluator = Mock()
        mock_result = Mock()
        mock_result.overall_opinion = "테스트 답변"
        mock_result.estimated_approval_probability = 0.8
        mock_result.relevant_articles = ["제197조"]
        mock_evaluator.evaluate_claim.return_value = mock_result
        mock_evaluator_class.return_value = mock_evaluator

        response = client.post(
            "/api/claims/evaluate",
            json={
                "claim": "20년 동안 점유하면 소유권을 취득할 수 있는가?",
                "use_rag": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "claim" in data
        assert "evaluation" in data
        assert "sources" in data

    def test_evaluate_claim_empty(self):
        """빈 청구항 평가"""
        response = client.post("/api/claims/evaluate", json={"claim": ""})

        assert response.status_code == 422


# ============================================================================
# Search Tests
# ============================================================================


class TestSemanticSearch:
    """의미론적 검색 엔드포인트 테스트"""

    @patch("src.api.server.get_vector_database")
    def test_search_success(self, mock_get_vdb):
        """검색 성공"""
        mock_vdb = Mock()
        mock_vdb.search.return_value = [
            Mock(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년 동안...",
                source_type="civil_law",
                similarity_score=0.95,
            )
        ]
        mock_get_vdb.return_value = mock_vdb

        response = client.get(
            "/api/search",
            params={"query": "취득시효", "top_k": 5, "source_type": "civil_law"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "취득시효"
        assert "results" in data
        assert data["total_results"] == 1

    def test_search_missing_query(self):
        """쿼리 누락"""
        response = client.get("/api/search")

        assert response.status_code == 422

    def test_search_invalid_top_k(self):
        """유효하지 않은 top_k"""
        response = client.get("/api/search", params={"query": "테스트", "top_k": 100})

        assert response.status_code == 422


# ============================================================================
# Game Session Tests
# ============================================================================


class TestGameSession:
    """게임 세션 엔드포인트 테스트"""

    @patch("src.api.server.GameEngine")
    def test_create_session_success(self, mock_engine_class):
        """세션 생성 성공"""
        mock_engine = Mock()
        mock_session = Mock()
        mock_session.player = Mock()
        mock_engine.create_session.return_value = mock_session
        mock_engine_class.return_value = mock_engine

        response = client.post(
            "/api/game/session", json={"player_name": "변리사 준비생", "level_id": 1}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["player_name"] == "변리사 준비생"
        assert data["level_id"] == 1
        assert "session_id" in data
        assert data["status"] == "created"

        # 세션이 저장되었는지 확인
        assert _session_store.exists(data["session_id"])

    def test_create_session_invalid_level(self):
        """유효하지 않은 레벨"""
        response = client.post(
            "/api/game/session", json={"player_name": "테스트", "level_id": 10}
        )

        assert response.status_code == 422

    def test_create_session_missing_name(self):
        """플레이어 이름 누락"""
        response = client.post("/api/game/session", json={"level_id": 1})

        assert response.status_code == 422


# ============================================================================
# Claim Submission Tests
# ============================================================================


class TestClaimSubmission:
    """청구항 제출 엔드포인트 테스트"""

    @patch("src.api.server.GameEngine")
    def test_submit_claim_success(self, mock_engine_class):
        """청구항 제출 성공"""
        # 먼저 세션 생성
        mock_engine = Mock()
        mock_session = Mock()
        mock_session.submit_claim.return_value = True
        mock_session.submitted_claims = ["첫 번째 청구항"]
        mock_engine.create_session.return_value = mock_session
        mock_engine_class.return_value = mock_engine

        # 세션 생성
        response = client.post(
            "/api/game/session", json={"player_name": "테스트", "level_id": 1}
        )
        session_id = response.json()["session_id"]

        # 청구항 제출 (mock 재설정)
        session_data = _session_store.get(session_id)
        session_data["session"].submit_claim = Mock(return_value=True)
        session_data["session"].submitted_claims = ["청구항"]
        _session_store.update(session_id, session_data)

        response = client.post(
            "/api/game/claim/submit",
            json={
                "session_id": session_id,
                "claim": "컴퓨터 프로그램을 저장한 컴퓨터 읽기 가능 매체",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session_id
        assert data["is_valid"] == True

    def test_submit_claim_invalid_session(self):
        """유효하지 않은 세션"""
        response = client.post(
            "/api/game/claim/submit",
            json={"session_id": "invalid_session", "claim": "컴퓨터 프로그램을 저장한 컴퓨터 읽기 가능 매체입니다"},
        )

        assert response.status_code == 404

    def test_submit_claim_too_short(self):
        """너무 짧은 청구항"""
        # 먼저 세션 생성
        with patch("src.api.server.GameEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_session = Mock()
            mock_engine.create_session.return_value = mock_session
            mock_engine_class.return_value = mock_engine

            response = client.post(
                "/api/game/session", json={"player_name": "테스트", "level_id": 1}
            )
            session_id = response.json()["session_id"]

            # 너무 짧은 청구항 제출
            response = client.post(
                "/api/game/claim/submit",
                json={"session_id": session_id, "claim": "짧음"},
            )

            assert response.status_code == 422


# ============================================================================
# Stats Tests
# ============================================================================


class TestStats:
    """통계 엔드포인트 테스트"""

    @patch("src.api.server.get_vector_database")
    def test_get_stats_success(self, mock_get_vdb):
        """통계 조회 성공"""
        mock_vdb = Mock()
        mock_vdb.get_stats.return_value = {
            "total_vectors": 824,
            "embedding_dimension": 1536,
        }
        mock_get_vdb.return_value = mock_vdb

        response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.json()

        assert "vector_db" in data
        assert "active_sessions" in data
        assert "system" in data


# ============================================================================
# Integration Tests
# ============================================================================


class TestAPIIntegration:
    """API 통합 테스트"""

    def test_full_flow(self):
        """전체 플로우 테스트"""
        # 1. 헬스 체크
        response = client.get("/api/health")
        assert response.status_code == 200

        # 2. 청구항 검증
        response = client.post(
            "/api/claims/validate", json={"claim": "컴퓨터 프로그램을 저장한 매체"}
        )
        assert response.status_code == 200

        # 3. 검색 (mock 필요)
        with patch("src.api.server.get_vector_database") as mock_get_vdb:
            mock_vdb = Mock()
            mock_vdb.search.return_value = []
            mock_get_vdb.return_value = mock_vdb

            response = client.get("/api/search", params={"query": "취득시효"})
            assert response.status_code == 200


# ============================================================================
# Pytest Markers
# ============================================================================

pytestmark = [
    pytest.mark.integration,
    pytest.mark.api,
]


# ============================================================================
# Cleanup
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup():
    """각 테스트 후 세션 정리"""
    yield
    # 세션 스토어 비우기 (모든 세션 삭제)
    try:
        for session_id in list(_session_store.list_all()):
            _session_store.delete(session_id)
    except Exception:
        pass
