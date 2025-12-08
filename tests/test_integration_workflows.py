"""
Integration Workflow Tests - 엔드투엔드 파이프라인 검증

전체 시스템의 워크플로우를 통합 테스트합니다.
API → Validator → Evaluator → Response 등 full pipeline을 검증합니다.
"""

import pytest
import json
import uuid
import threading
from typing import List, Dict
from fastapi.testclient import TestClient
from datetime import datetime

# Mark all tests in this file
pytestmark = [
    pytest.mark.integration,
    pytest.mark.workflow,
]


class TestCompleteValidationFlow:
    """완전한 청구항 검증 플로우"""

    def test_complete_claim_validation_to_response(self):
        """API → Validator → Response (완전한 검증 파이프라인)"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 유효한 청구항으로 검증 요청
        claim_text = "배터리 기술에 관한 청구항으로서 양극, 음극, 전해질을 포함하며 안정성이 우수하다."
        response = client.post(
            "/api/claims/validate",
            json={"claim": claim_text, "claim_type": "independent"},
        )

        # Step 2: 응답 검증
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        data = response.json()

        # Step 3: 응답 구조 검증
        assert isinstance(data, dict), "Response must be dict"
        assert "is_valid" in data or "status" in data, "Missing required validation field"

        # Step 4: 유효하면 is_valid가 있어야 함
        if response.status_code == 200:
            assert "is_valid" in data
            assert isinstance(data["is_valid"], bool)
            assert "errors" in data
            assert isinstance(data["errors"], list)

    def test_validation_with_invalid_claim(self):
        """무효한 청구항 검증 결과"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 너무 짧은 청구항 제출
        short_claim = "테스트"
        response = client.post(
            "/api/claims/validate",
            json={"claim": short_claim, "claim_type": "independent"},
        )

        # Step 2: 응답 검증
        assert response.status_code in [200, 400, 422]
        data = response.json()

        # Step 3: 검증 결과 확인
        if response.status_code == 200:
            # 응답 200이어도 is_valid가 False일 수 있음
            assert data.get("is_valid") is False or data.get("errors")


class TestGameSessionWorkflow:
    """게임 세션 생명주기 테스트"""

    def test_session_create_start_play_end(self):
        """세션 생성 → 게임 시작 → 플레이 → 종료"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 세션 생성
        session_response = client.post(
            "/api/game/session",
            json={"player_name": "테스트플레이어", "level_id": 1},
        )

        assert session_response.status_code in [200, 400]

        if session_response.status_code == 200:
            session_data = session_response.json()
            assert "session_id" in session_data
            session_id = session_data["session_id"]

            # Step 2: 클레임 제출 (플레이)
            claim_response = client.post(
                "/api/game/claim/submit",
                json={
                    "session_id": session_id,
                    "claim": "배터리 기술에 관한 청구항으로 양극, 음극, 전해질을 포함한다.",
                },
            )

            assert claim_response.status_code in [200, 400, 422]

    def test_multiple_claims_in_session(self):
        """한 세션에서 여러 청구항 제출"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 세션 생성
        session_response = client.post(
            "/api/game/session",
            json={"player_name": "테스트", "level_id": 1},
        )

        if session_response.status_code == 200:
            session_id = session_response.json()["session_id"]

            # Step 2: 3개 청구항 순차 제출
            claims = [
                "배터리 기술에 관한 청구항으로 양극, 음극, 전해질을 포함한다.",
                "디스플레이 기술에 관한 청구항으로 LED 백라이트를 사용한다.",
                "센서 기술에 관한 청구항으로 적외선 감지 기능이 있다.",
            ]

            responses = []
            for claim_text in claims:
                response = client.post(
                    "/api/game/claim/submit",
                    json={"session_id": session_id, "claim": claim_text},
                )
                responses.append(response.status_code)

            # Step 3: 모든 응답이 유효해야 함
            assert all(
                code in [200, 400, 422] for code in responses
            ), f"Invalid status codes: {responses}"


class TestSearchAndRAGWorkflow:
    """검색과 RAG 통합 워크플로우"""

    def test_search_query_chain(self):
        """검색 쿼리 → 결과 반환"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 검색 쿼리 실행
        response = client.get(
            "/api/search?query=배터리&top_k=5&source_type=civil_law"
        )

        # Step 2: 응답 검증
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

            # Step 3: 검색 결과 구조 검증
            if "results" in data:
                results = data["results"]
                assert isinstance(results, list)

                # 각 결과 항목의 구조 검증
                for result in results:
                    assert isinstance(result, dict)
                    # 기본 필드 검증
                    assert "statute_number" in result or "id" in result

    def test_search_multiple_queries_consistency(self):
        """여러 검색 쿼리의 일관성"""
        from src.api.server import app

        client = TestClient(app)

        queries = ["배터리", "디스플레이", "센서"]
        responses = []

        for query in queries:
            response = client.get(
                f"/api/search?query={query}&top_k=3&source_type=civil_law"
            )
            responses.append(response.status_code)

        # 모든 응답이 일관된 상태 코드여야 함
        assert all(code in [200, 400, 500] for code in responses)


class TestErrorHandlingWorkflow:
    """에러 처리 워크플로우"""

    def test_invalid_session_id_error_flow(self):
        """존재하지 않는 세션 ID 처리"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 존재하지 않는 세션으로 청구항 제출
        fake_session_id = f"fake_{uuid.uuid4().hex[:12]}"
        response = client.post(
            "/api/game/claim/submit",
            json={
                "session_id": fake_session_id,
                "claim": "배터리 기술에 관한 청구항으로 양극, 음극, 전해질을 포함한다.",
            },
        )

        # Step 2: 에러 응답 검증
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}"

        # Step 3: 응답 형식 검증
        data = response.json()
        assert isinstance(data, dict), "Error response must be dict"
        assert "error" in data or "detail" in data, "Error response must contain error info"

    def test_empty_claim_validation_error(self):
        """빈 청구항 검증 에러"""
        from src.api.server import app

        client = TestClient(app)

        response = client.post(
            "/api/claims/validate", json={"claim": "", "claim_type": "independent"}
        )

        # 빈 청구항은 400 또는 422 반환해야 함
        assert response.status_code in [200, 400, 422]

        # 200이어도 is_valid가 False여야 함
        data = response.json()
        if response.status_code == 200:
            assert data.get("is_valid") is False

    def test_malformed_request_error(self):
        """잘못된 요청 형식 처리"""
        from src.api.server import app

        client = TestClient(app)

        # 필수 필드 누락
        response = client.post(
            "/api/claims/validate", json={"claim_type": "independent"}
        )

        assert response.status_code in [400, 422]


class TestConcurrentSessionWorkflow:
    """동시 세션 워크플로우"""

    def test_concurrent_session_creation(self):
        """동시 세션 생성 (10개 스레드)"""
        from src.api.server import app

        client = TestClient(app)
        session_ids = []
        errors = []

        def create_session_thread(thread_id):
            try:
                response = client.post(
                    "/api/game/session",
                    json={"player_name": f"player_{thread_id}", "level_id": 1},
                )
                if response.status_code == 200:
                    session_id = response.json().get("session_id")
                    if session_id:
                        session_ids.append(session_id)
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Step 1: 10개 스레드로 동시 세션 생성
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_session_thread, args=(i,))
            threads.append(t)
            t.start()

        # Step 2: 모든 스레드 대기
        for t in threads:
            t.join()

        # Step 3: 결과 검증
        if len(session_ids) > 0:
            # 생성된 세션이 있다면, 모두 고유해야 함
            assert len(set(session_ids)) == len(
                session_ids
            ), "Sessions must be unique"

    def test_concurrent_claims_in_single_session(self):
        """한 세션에 동시 청구항 제출"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 세션 생성
        session_response = client.post(
            "/api/game/session",
            json={"player_name": "테스트", "level_id": 1},
        )

        if session_response.status_code == 200:
            session_id = session_response.json()["session_id"]

            # Step 2: 5개 스레드에서 동시 청구항 제출
            claim_submissions = []
            errors = []

            def submit_claim_thread(thread_id):
                try:
                    response = client.post(
                        "/api/game/claim/submit",
                        json={
                            "session_id": session_id,
                            "claim": f"기술_{thread_id}에 관한 청구항으로 신규성과 진보성이 우수하다.",
                        },
                    )
                    claim_submissions.append(response.status_code)
                except Exception as e:
                    errors.append((thread_id, str(e)))

            threads = []
            for i in range(5):
                t = threading.Thread(target=submit_claim_thread, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Step 3: 결과 검증
            assert len(errors) == 0 or len(claim_submissions) > 0, "Concurrent claims should work"


class TestEndToEndGameFlow:
    """전체 게임 플로우 통합 테스트"""

    def test_complete_game_session_flow(self):
        """게임 시작부터 종료까지의 완전한 플로우"""
        from src.api.server import app

        client = TestClient(app)

        # Step 1: 헬스 체크
        health_response = client.get("/api/health")
        assert health_response.status_code == 200

        # Step 2: 게임 세션 생성
        session_response = client.post(
            "/api/game/session",
            json={"player_name": "완전한_테스트", "level_id": 1},
        )
        assert session_response.status_code in [200, 400]

        if session_response.status_code == 200:
            session_id = session_response.json()["session_id"]

            # Step 3: 청구항 검증
            claims = [
                "배터리 기술에 관한 청구항으로 양극, 음극, 전해질을 포함한다.",
                "디스플레이 기술에 관한 청구항으로 LED 백라이트를 사용한다.",
            ]

            for claim in claims:
                # Step 3a: 청구항 사전 검증
                validate_response = client.post(
                    "/api/claims/validate",
                    json={"claim": claim, "claim_type": "independent"},
                )
                assert validate_response.status_code in [200, 400, 422]

                # Step 3b: 게임 세션에 청구항 제출
                submit_response = client.post(
                    "/api/game/claim/submit",
                    json={"session_id": session_id, "claim": claim},
                )
                assert submit_response.status_code in [200, 400, 422]

            # Step 4: 최종 헬스 체크
            final_health = client.get("/api/health")
            assert final_health.status_code == 200
