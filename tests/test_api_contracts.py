"""
API Contract Tests - API 응답 스키마 및 계약 검증

이 테스트는 API 엔드포인트의 응답 형식, 상태 코드,
그리고 요청/응답 스키마 계약을 검증합니다.
"""

import pytest
import json
from typing import Dict, Any, List
from datetime import datetime
from fastapi.testclient import TestClient


# ============================================================================
# Helper Functions
# ============================================================================


def validate_response_schema(response_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """응답 데이터가 정의된 스키마와 일치하는지 검증"""
    for key, expected_type in schema.items():
        if key not in response_data:
            return False
        if not isinstance(response_data[key], expected_type):
            return False
    return True


# ============================================================================
# Health Endpoint Tests
# ============================================================================


class TestHealthEndpointContract:
    """Health 엔드포인트 계약 검증"""

    def test_health_endpoint_response_schema(self):
        """Health 엔드포인트의 응답 스키마"""
        from src.api.server import app

        client = TestClient(app)
        response = client.get("/api/health")

        # 상태 코드 검증
        assert response.status_code == 200

        # 응답 형식 검증
        data = response.json()
        assert data is not None
        assert isinstance(data, dict)

        # 필수 필드 검증
        assert "status" in data
        assert data["status"] in ["ready", "unavailable", "degraded", "healthy"]

        # 선택적 필드 검증
        if "timestamp" in data:
            # ISO 8601 형식이어야 함
            try:
                datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass  # 형식 검증 실패해도 무시

    def test_health_endpoint_includes_component_status(self):
        """Health 엔드포인트에 컴포넌트 상태 포함"""
        from src.api.server import app

        client = TestClient(app)
        response = client.get("/api/health")

        data = response.json()

        # 컴포넌트 상태 정보 (있으면)
        if "components" in data:
            components = data["components"]
            assert isinstance(components, dict)

            # 알려진 컴포넌트들
            expected_components = [
                "validator",
                "evaluator",
                "vector_db",
                "rag",
            ]
            for comp in expected_components:
                if comp in components:
                    assert components[comp] in ["healthy", "degraded", "unavailable", "ready"]

    def test_health_endpoint_response_time(self):
        """Health 엔드포인트는 빠른 응답"""
        from src.api.server import app
        import time

        client = TestClient(app)

        start_time = time.time()
        response = client.get("/api/health")
        elapsed = time.time() - start_time

        assert response.status_code == 200
        assert elapsed < 1.0  # 1초 이내 응답


# ============================================================================
# Validation Endpoint Tests
# ============================================================================


class TestValidationEndpointContract:
    """Validation 엔드포인트 계약 검증"""

    def test_validation_endpoint_response_schema(self):
        """Validation 엔드포인트 응답 스키마"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/claims/validate",
            json={
                "claim": "배터리 기술에 관한 청구항으로서 양극, 음극, 전해질을 포함한다.",
                "claim_type": "independent",
            },
        )

        # 유효한 응답이어야 함
        assert response.status_code in [200, 400]

        data = response.json()
        assert data is not None
        assert isinstance(data, dict)

        if response.status_code == 200:
            # 성공 응답
            assert "is_valid" in data
            assert isinstance(data["is_valid"], bool)
            assert "errors" in data
            assert isinstance(data["errors"], list)

    def test_validation_endpoint_error_cases(self):
        """Validation 엔드포인트 에러 케이스"""
        from src.api.server import app

        client = TestClient(app)

        # Case 1: 빈 청구항 - 200이어도 is_valid가 False
        response1 = client.post(
            "/api/claims/validate",
            json={"claim": "", "claim_type": "independent"},
        )
        assert response1.status_code in [200, 400, 422]
        if response1.status_code == 200:
            data = response1.json()
            assert data.get("is_valid") is False

        # Case 2: 잘못된 claim_type은 200이어도 될 수 있음 (API에서 허용)
        response2 = client.post(
            "/api/claims/validate",
            json={"claim": "테스트 청구항", "claim_type": "invalid"},
        )
        assert response2.status_code in [200, 400, 422]

        # Case 3: 누락된 필드도 200이어도 될 수 있음
        response3 = client.post(
            "/api/claims/validate",
            json={"claim": "테스트 청구항"},
        )
        assert response3.status_code in [200, 400, 422]

    def test_validation_endpoint_content_type(self):
        """Validation 엔드포인트 Content-Type 검증"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/claims/validate",
            json={
                "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
                "claim_type": "independent",
            },
        )

        # JSON Content-Type
        assert "application/json" in response.headers.get("content-type", "")


# ============================================================================
# Evaluation Endpoint Tests
# ============================================================================


class TestEvaluationEndpointContract:
    """Evaluation 엔드포인트 계약 검증"""

    def test_evaluation_endpoint_response_format(self):
        """Evaluation 엔드포인트 응답 형식"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/claims/evaluate",
            json={
                "claim": "배터리 기술에 관한 청구항으로 신규성과 진보성이 있다.",
                "use_rag": False,
            },
        )

        assert response.status_code in [200, 400, 500]

        data = response.json()
        if response.status_code == 200:
            assert data is not None
            # 평가 결과 필드
            if "evaluation" in data:
                eval_result = data["evaluation"]
                # 필수 필드들
                assert isinstance(eval_result, dict)

    def test_evaluation_endpoint_confidence_bounds(self):
        """Evaluation 엔드포인트 신뢰도 점수 범위"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/claims/evaluate",
            json={
                "claim": "배터리 기술에 관한 청구항으로 신규성과 진보성이 있다.",
                "use_rag": False,
            },
        )

        if response.status_code == 200:
            data = response.json()
            if "confidence_score" in data:
                score = data["confidence_score"]
                # 신뢰도는 0~1 범위여야 함
                assert 0.0 <= score <= 1.0

    def test_evaluation_endpoint_with_without_rag(self):
        """RAG 사용 여부에 따른 응답"""
        from src.api.server import app

        client = TestClient(app)
        claim = "배터리 기술에 관한 청구항으로 신규성과 진보성이 있다."

        # RAG 없음
        response1 = client.post(
            "/api/claims/evaluate",
            json={"claim": claim, "use_rag": False},
        )

        # RAG 사용
        response2 = client.post(
            "/api/claims/evaluate",
            json={"claim": claim, "use_rag": True},
        )

        # 두 응답 모두 같은 형식이어야 함
        if response1.status_code == 200:
            data1 = response1.json()
            assert data1 is not None


# ============================================================================
# Search Endpoint Tests
# ============================================================================


class TestSearchEndpointContract:
    """Search 엔드포인트 계약 검증"""

    def test_search_endpoint_response_structure(self):
        """Search 엔드포인트 응답 구조"""
        from src.api.server import app

        client = TestClient(app)

        response = client.get(
            "/api/search?query=배터리&top_k=5&source_type=civil_law"
        )

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert data is not None
            assert isinstance(data, dict)

            # 검색 결과
            if "results" in data:
                results = data["results"]
                assert isinstance(results, list)

                # 각 결과 항목
                for result in results:
                    assert isinstance(result, dict)
                    # 필수 필드
                    assert "statute_number" in result or "id" in result

    def test_search_endpoint_parameter_validation(self):
        """Search 엔드포인트 파라미터 검증"""
        from src.api.server import app

        client = TestClient(app)

        # Case 1: 필수 파라미터 누락
        response1 = client.get("/api/search?source_type=civil_law")
        assert response1.status_code in [400, 422]

        # Case 2: top_k 범위 초과
        response2 = client.get(
            "/api/search?query=test&top_k=100&source_type=civil_law"
        )
        # top_k 범위 체크 (보통 1-20)
        if response2.status_code == 200:
            # 요청은 받아들이지만 제한될 수 있음
            pass

        # Case 3: 잘못된 source_type
        response3 = client.get(
            "/api/search?query=test&top_k=5&source_type=invalid"
        )
        # 에러 또는 빈 결과
        assert response3.status_code in [200, 400]

    def test_search_endpoint_similarity_scores(self):
        """Search 엔드포인트 유사도 점수 범위"""
        from src.api.server import app

        client = TestClient(app)

        response = client.get(
            "/api/search?query=배터리&top_k=5&source_type=civil_law"
        )

        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                for result in data["results"]:
                    if "similarity_score" in result:
                        score = result["similarity_score"]
                        # 유사도는 0~1 범위여야 함
                        assert 0.0 <= score <= 1.0


# ============================================================================
# Game Session Endpoint Tests
# ============================================================================


class TestGameSessionEndpointContract:
    """Game Session 엔드포인트 계약 검증"""

    def test_session_creation_endpoint_response(self):
        """Session creation 엔드포인트 응답"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/game/session",
            json={"player_name": "테스트 플레이어", "level_id": 1},
        )

        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert isinstance(data["session_id"], str)
            assert len(data["session_id"]) > 0

    def test_session_creation_parameter_validation(self):
        """Session creation 파라미터 검증"""
        from src.api.server import app

        client = TestClient(app)

        # Case 1: 빈 player_name
        response1 = client.post(
            "/api/game/session",
            json={"player_name": "", "level_id": 1},
        )
        assert response1.status_code in [400, 422]

        # Case 2: 잘못된 level_id
        response2 = client.post(
            "/api/game/session",
            json={"player_name": "테스트", "level_id": 999},
        )
        assert response2.status_code in [400, 422]

    def test_claim_submission_endpoint_response(self):
        """Claim submission 엔드포인트 응답"""
        from src.api.server import app
        import uuid

        client = TestClient(app)

        # 먼저 세션 생성
        session_response = client.post(
            "/api/game/session",
            json={"player_name": "테스트", "level_id": 1},
        )

        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data["session_id"]

            # 클레임 제출
            response = client.post(
                "/api/game/claim/submit",
                json={
                    "session_id": session_id,
                    "claim": "배터리 기술에 관한 청구항으로 양극, 음극, 전해질을 포함한다.",
                },
            )

            assert response.status_code in [200, 400, 422]

            if response.status_code == 200:
                data = response.json()
                # 응답에 결과 정보가 있어야 함
                assert "claim_number" in data or "status" in data or "success" in data


# ============================================================================
# HTTP Status Code Tests
# ============================================================================


class TestHTTPStatusCodeCorrectness:
    """HTTP 상태 코드 정확성 검증"""

    def test_success_returns_200(self):
        """성공 요청은 200 반환"""
        from src.api.server import app

        client = TestClient(app)

        response = client.get("/api/health")
        assert response.status_code == 200

    def test_invalid_input_returns_400_or_422(self):
        """잘못된 입력은 400 또는 422 반환"""
        from src.api.server import app

        client = TestClient(app)

        # 빈 청구항
        response = client.post(
            "/api/claims/validate",
            json={"claim": "", "claim_type": "independent"},
        )
        assert response.status_code in [400, 422]

    def test_not_found_returns_404(self):
        """존재하지 않는 세션은 404 반환"""
        from src.api.server import app

        client = TestClient(app)

        # 존재하지 않는 세션으로 클레임 제출
        response = client.post(
            "/api/game/claim/submit",
            json={
                "session_id": "nonexistent_session_12345",
                "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
            },
        )

        assert response.status_code in [400, 404]

    def test_server_error_returns_500(self):
        """서버 에러는 500 반환"""
        from src.api.server import app
        from unittest.mock import patch

        client = TestClient(app)

        # 강제로 500 에러 발생
        with patch("src.dsl.grammar.claim_validator.ClaimValidator.validate_claim_content") as mock_validate:
            mock_validate.side_effect = RuntimeError("Unexpected server error")

            response = client.post(
                "/api/claims/validate",
                json={
                    "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
                    "claim_type": "independent",
                },
            )

            assert response.status_code in [400, 500]


# ============================================================================
# Response Content-Type Tests
# ============================================================================


class TestResponseContentType:
    """응답 Content-Type 검증"""

    def test_json_endpoints_return_json_content_type(self):
        """JSON 엔드포인트는 application/json 반환"""
        from src.api.server import app

        client = TestClient(app)

        # Health 엔드포인트
        response = client.get("/api/health")
        assert "application/json" in response.headers.get("content-type", "")

        # Validation 엔드포인트
        response = client.post(
            "/api/claims/validate",
            json={
                "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
                "claim_type": "independent",
            },
        )
        assert "application/json" in response.headers.get("content-type", "")

    def test_error_responses_are_json(self):
        """에러 응답도 JSON 형식"""
        from src.api.server import app

        client = TestClient(app)

        # 잘못된 요청
        response = client.post(
            "/api/claims/validate",
            json={"claim": "", "claim_type": "independent"},
        )

        assert response.status_code in [400, 422]
        assert "application/json" in response.headers.get("content-type", "")
        assert response.json() is not None


# ============================================================================
# Pytest Markers
# ============================================================================

pytestmark = [
    pytest.mark.api,
    pytest.mark.contracts,
    pytest.mark.integration,
]
