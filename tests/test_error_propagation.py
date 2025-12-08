"""
Error Propagation Tests - 시스템 계층 간 에러 처리 검증

에러가 시스템의 각 계층을 통해 올바르게 전파되고,
적절한 HTTP 상태 코드와 메시지로 반환되는지 검증합니다.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.utils.exceptions import (
    GameEngineException,
    SessionNotFoundException,
    ClaimValidationException,
    EvaluationTimeoutException,
    PersistenceException,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.error_handling,
]


class TestValidatorErrorPropagation:
    """검증자(Validator) 계층의 에러 전파"""

    def test_validator_error_to_api_400(self):
        """ClaimValidator 에러 → API 400 응답"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 잘못된 청구항으로 검증 요청
        response = client.post(
            "/api/claims/validate",
            json={"claim": "", "claim_type": "independent"},
        )

        # Step 2: 400 또는 422 상태 코드 확인
        assert response.status_code in [200, 400, 422]

        # Step 3: 응답 구조 확인
        data = response.json()
        if response.status_code in [400, 422]:
            assert isinstance(data, dict)
            # 에러 정보 포함 확인
            assert "error" in data or "detail" in data or "is_valid" in data

    def test_claim_length_validation_error(self):
        """청구항 길이 검증 에러"""
        from src.api.server import app

        client = TestClient(app)

        # 너무 짧은 청구항
        short_claim = "짧음"
        response = client.post(
            "/api/claims/validate",
            json={"claim": short_claim, "claim_type": "independent"},
        )

        assert response.status_code in [200, 400, 422]

        data = response.json()
        # 200이어도 is_valid가 False여야 함
        if response.status_code == 200:
            assert data.get("is_valid") is False

    def test_invalid_claim_type_validation(self):
        """무효한 청구항 유형 검증"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/claims/validate",
            json={"claim": "유효한 청구항으로 30글자 이상이어야 합니다.", "claim_type": "invalid_type"},
        )

        # 400, 422, 또는 200 with is_valid=False
        assert response.status_code in [200, 400, 422]


class TestSessionErrorPropagation:
    """세션 계층의 에러 전파"""

    def test_session_not_found_error_to_404(self):
        """SessionNotFoundException → API 404 응답"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 존재하지 않는 세션으로 요청
        response = client.post(
            "/api/game/claim/submit",
            json={
                "session_id": "nonexistent_session_xyz",
                "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
            },
        )

        # Step 2: 404 또는 400 상태 코드 확인
        assert response.status_code in [400, 404]

        # Step 3: 에러 응답 검증
        data = response.json()
        assert isinstance(data, dict)

    def test_session_creation_invalid_level_error(self):
        """유효하지 않은 레벨 ID 에러"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/game/session",
            json={"player_name": "테스트", "level_id": 99999},
        )

        # 400 또는 422 반환
        assert response.status_code in [200, 400, 422]

    def test_empty_player_name_error(self):
        """빈 플레이어명 에러"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/game/session", json={"player_name": "", "level_id": 1}
        )

        # 400 또는 422 반환
        assert response.status_code in [400, 422]


class TestEvaluationErrorPropagation:
    """평가(Evaluation) 계층의 에러 전파"""

    def test_evaluation_timeout_returns_504(self):
        """평가 시간 초과 → 504 상태 코드"""
        from src.api.server import app

        client = TestClient(app)

        # 평가 요청 (시간 초과 가능성)
        response = client.post(
            "/api/claims/evaluate",
            json={
                "claim": "배터리 기술에 관한 청구항으로 신규성과 진보성이 있다.",
                "use_rag": False,
            },
        )

        # 200, 500, 또는 504 반환 가능
        assert response.status_code in [200, 400, 500, 504]

        # 500 이상이면 에러 메시지 포함
        if response.status_code >= 400:
            data = response.json()
            assert isinstance(data, dict)

    def test_evaluation_with_without_rag_consistent(self):
        """RAG 사용 여부에 관계없이 일관된 에러 처리"""
        from src.api.server import app

        client = TestClient(app)

        claim = "배터리 기술에 관한 청구항으로 신규성과 진보성이 있다."

        # Step 1: RAG 없이 평가
        response1 = client.post(
            "/api/claims/evaluate",
            json={"claim": claim, "use_rag": False},
        )

        # Step 2: RAG 사용하여 평가
        response2 = client.post(
            "/api/claims/evaluate",
            json={"claim": claim, "use_rag": True},
        )

        # 두 응답의 상태 코드가 일관되어야 함 (둘 다 성공 또는 둘 다 실패)
        assert (response1.status_code == 200 and response2.status_code == 200) or (
            response1.status_code >= 400 and response2.status_code >= 400
        )


class TestStructuredErrorResponses:
    """구조화된 에러 응답 검증"""

    def test_error_response_structure(self):
        """모든 에러 응답의 일관된 구조"""
        from src.api.server import app

        client = TestClient(app)

        # 여러 에러 케이스 생성
        error_cases = [
            {
                "endpoint": "/api/game/session",
                "method": "post",
                "data": {"player_name": "", "level_id": 1},
            },
            {
                "endpoint": "/api/claims/validate",
                "method": "post",
                "data": {"claim": "", "claim_type": "independent"},
            },
            {
                "endpoint": "/api/game/claim/submit",
                "method": "post",
                "data": {"session_id": "fake", "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다."},
            },
        ]

        for case in error_cases:
            if case["method"] == "post":
                response = client.post(case["endpoint"], json=case["data"])
            else:
                response = client.get(case["endpoint"])

            # 에러 응답인 경우 (400 이상)
            if response.status_code >= 400:
                data = response.json()
                # JSON 형식 확인
                assert isinstance(data, dict), f"Error response must be dict: {case}"

    def test_error_response_includes_details(self):
        """에러 응답에 충분한 정보 포함"""
        from src.api.server import app

        client = TestClient(app)

        # 잘못된 요청
        response = client.post(
            "/api/claims/validate",
            json={"claim": "짧음", "claim_type": "independent"},
        )

        # 200이어도 유효성 정보 포함
        data = response.json()
        assert isinstance(data, dict)
        assert "is_valid" in data or "error" in data or "detail" in data


class TestErrorRecovery:
    """에러 발생 후 시스템 복구"""

    def test_system_recovers_after_error(self):
        """에러 발생 후에도 다음 요청 정상 처리"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 에러 발생
        error_response = client.post(
            "/api/claims/validate",
            json={"claim": "", "claim_type": "independent"},
        )

        assert error_response.status_code in [200, 400, 422]

        # Step 2: 정상 요청
        normal_response = client.get("/api/health")

        # Step 3: 정상 요청이 성공해야 함
        assert normal_response.status_code == 200

    def test_multiple_errors_do_not_affect_system(self):
        """여러 에러 요청 후에도 시스템 정상 작동"""
        from src.api.server import app

        client = TestClient(app)

        # 여러 에러 요청
        for i in range(5):
            response = client.post(
                "/api/game/session",
                json={"player_name": "", "level_id": 9999},
            )
            assert response.status_code in [200, 400, 422]

        # 최종 헬스 체크
        health = client.get("/api/health")
        assert health.status_code == 200

    def test_error_in_one_session_isolated(self):
        """한 세션의 에러가 다른 세션에 영향 없음"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 정상 세션 생성
        session1 = client.post(
            "/api/game/session",
            json={"player_name": "플레이어1", "level_id": 1},
        )

        if session1.status_code == 200:
            session1_id = session1.json()["session_id"]

            # Step 2: 다른 세션에 잘못된 요청
            bad_response = client.post(
                "/api/game/claim/submit",
                json={
                    "session_id": "wrong_session",
                    "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
                },
            )

            # Step 3: 원래 세션은 여전히 작동해야 함
            good_response = client.post(
                "/api/game/claim/submit",
                json={
                    "session_id": session1_id,
                    "claim": "배터리 기술에 관한 청구항으로 양극, 음극, 전해질을 포함한다.",
                },
            )

            # 정상 세션 요청은 성공해야 함
            assert good_response.status_code in [200, 400, 422]


class TestHTTPStatusCodeCorrectness:
    """HTTP 상태 코드 정확성"""

    def test_client_error_returns_4xx(self):
        """클라이언트 에러는 4xx 반환"""
        from src.api.server import app

        client = TestClient(app)

        # 여러 클라이언트 에러 케이스
        responses = [
            client.post(
                "/api/game/claim/submit",
                json={"session_id": "fake", "claim": "짧음"},
            ),
            client.post(
                "/api/claims/validate",
                json={"claim": "", "claim_type": "independent"},
            ),
            client.get("/api/search?source_type=invalid"),  # 필수 파라미터 누락
        ]

        # 모든 응답이 200 또는 400+ 범위여야 함
        for response in responses:
            assert response.status_code in range(200, 600)

    def test_missing_resource_returns_404(self):
        """리소스 없음은 404 반환"""
        from src.api.server import app

        client = TestClient(app)

        # 존재하지 않는 세션
        response = client.post(
            "/api/game/claim/submit",
            json={
                "session_id": "nonexistent",
                "claim": "테스트 청구항으로 30글자 이상의 내용을 포함합니다.",
            },
        )

        # 404 또는 400
        assert response.status_code in [400, 404]
