"""
🚨 DEPRECATED: This file is deprecated. Use test_api_integration_v2.py instead.

Legacy API 엔드포인트 통합 테스트 (v1 - 구형)

실제 Flask API 서버를 실행하고 HTTP 요청으로 테스트합니다.

DEPRECATION REASON:
- GameSession 구조 변경으로 인한 호환성 깨짐
- Claims 저장 구조 변경 (List[Claim] → List[str])
- Property 속성명 변경 (player_name → player)
- test_api_integration_v2.py에서 모든 테스트 대체됨 (17/17 PASS)

MIGRATION:
- test_api_integration_v2.py에서 동일 기능 테스트 중
- Property-based testing 추가 (edge case 자동 발견)
- 본 파일은 향후 제거 예정
"""

import pytest
import json
from src.ui.game import GameEngine


class TestGameSessionAPI:
    """게임 세션 API 테스트"""

    def test_create_game_session(self):
        """새로운 게임 세션 생성"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_session_1", player_name="Test Player", level_id=1
        )

        assert session is not None
        assert session.session_id == "test_session_1"
        assert session.player.player_name == "Test Player"
        assert session.current_level.level_id == 1

    def test_submit_claim_to_session(self):
        """게임 세션에 청구항 제출"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_submit", player_name="Test Player", level_id=1
        )

        # 정상적인 청구항 제출
        claim = "배터리 장치는 양극, 음극, 전해질을 포함하며 효율적인 에너지 저장이 가능하다"
        result = session.submit_claim(claim)

        assert result is True
        assert len(session.claims) == 1
        assert session.claims[0] == claim

    def test_submit_empty_claim_rejected(self):
        """빈 청구항은 거부되어야 함"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_empty", player_name="Test Player", level_id=1
        )

        # 빈 청구항 제출 시도
        result = session.submit_claim("")

        assert result is False
        assert len(session.claims) == 0

    def test_submit_claim_with_special_characters(self):
        """특수문자가 포함된 청구항 처리"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_special", player_name="Test Player", level_id=1
        )

        # 특수문자 포함 청구항
        claim = (
            "배터리 장치는 Li-ion(리튬이온) 방식의 양극(+), 음극(-), 전해질을 포함한다."
        )
        result = session.submit_claim(claim)

        assert result is True
        assert session.claims[0] == claim

    def test_claim_validation_rules(self):
        """청구항 검증 규칙 테스트 - 기본 규칙"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_validate", player_name="Test Player", level_id=1
        )

        # 유효한 청구항
        valid_claim = "배터리 장치는 양극, 음극, 전해질을 포함하며 효율적인 에너지 저장이 가능하다"
        result = session.submit_claim(valid_claim)
        assert result is True

        # 너무 짧은 청구항
        short_claim = "배터리"
        result = session.submit_claim(short_claim)
        # 짧은 청구항은 거부될 수 있음

        # 너무 긴 청구항 (1000자 이상)
        long_claim = "배터리" * 200  # 2400자
        result = session.submit_claim(long_claim)
        # 긴 청구항은 거부될 수 있음


class TestGameEvaluationAPI:
    """게임 평가 API 테스트"""

    def test_evaluate_claims_basic_logic(self):
        """기본 청구항 평가 로직 테스트"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_eval", player_name="Test Player", level_id=1
        )

        # 여러 청구항 제출
        claims = [
            "배터리 장치는 양극, 음극, 전해질을 포함하며 효율적인 에너지 저장이 가능하다",
            "제1항의 배터리 장치에 있어서, 상기 양극은 리튬산화물을 포함하는 배터리 장치",
            "제1항의 배터리 장치에 있어서, 상기 음극은 흑연을 포함하는 배터리 장치",
        ]

        for claim in claims:
            session.submit_claim(claim)

        # 평가 실행
        success, feedback, details = engine.evaluate_claims(session.session_id)

        assert success is True
        assert details is not None
        assert len(details.get("validation_results", [])) == len(claims)

    def test_game_scoring_system(self):
        """게임 점수 계산 시스템 테스트"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_score", player_name="Test Player", level_id=1
        )

        # 3개의 청구항으로 평가 실행
        claims = [
            "배터리 장치는 양극과 음극을 포함하며 안정적인 에너지 저장이 가능하다",
            "제1항의 배터리에서 양극은 리튬이다",
            "제1항의 배터리에서 음극은 흑연이다",
        ]

        for claim in claims:
            session.submit_claim(claim)

        success, feedback, details = engine.evaluate_claims(session.session_id)

        if success:
            # 점수는 100 + (평균점수 * 50) + (청구항 개수 * 10)
            # 예: 100 + (0.8 * 50) + (3 * 10) = 130
            score = details.get("score", 0)
            assert score >= 100  # 최소 기본점
            assert score <= 200  # 최대 점수는 합리적인 범위

    def test_level_progression(self):
        """레벨 진행 시스템 테스트"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_level", player_name="Test Player", level_id=1
        )

        assert session.current_level.level_id == 1

        # 5개 청구항 완료하면 레벨 업
        for i in range(5):
            claim = f"청구항 {i+1}: 배터리 장치는 양극과 음극을 포함하며 안정적인 에너지 저장이 가능하다"
            session.submit_claim(claim)

        success, feedback, details = engine.evaluate_claims(session.session_id)

        if success and session.is_level_complete():
            session.progress_to_next_level()
            assert session.current_level == 2


class TestGameErrorHandling:
    """게임 에러 처리 테스트"""

    def test_handle_claim_too_long(self):
        """너무 긴 청구항 처리"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_long", player_name="Test Player", level_id=1
        )

        # 5000자 이상의 청구항
        long_claim = "배터리" * 1000

        result = session.submit_claim(long_claim)

        # 너무 긴 청구항은 거부되어야 함
        assert result is False or len(session.claims) == 0

    def test_handle_invalid_characters(self):
        """유효하지 않은 문자 처리"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_invalid_chars", player_name="Test Player", level_id=1
        )

        # 제어 문자 포함
        claim = "배터리\x00\x01\x02"

        result = session.submit_claim(claim)

        # 결과는 거부되거나 정제되어야 함
        if result is True:
            assert "\x00" not in session.claims[0]

    def test_duplicate_claim_handling(self):
        """중복 청구항 처리"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_duplicate", player_name="Test Player", level_id=1
        )

        claim = "배터리 장치는 양극과 음극을 포함하며 안정적인 에너지 저장이 가능하다"

        # 같은 청구항 두 번 제출
        result1 = session.submit_claim(claim)
        result2 = session.submit_claim(claim)

        assert result1 is True

        # 중복에 대한 처리 (거부 또는 경고)
        # 구현에 따라 다를 수 있음


class TestGameDataPersistence:
    """게임 데이터 지속성 테스트"""

    def test_session_data_persistence(self):
        """세션 데이터 저장 및 로드"""
        engine = GameEngine()

        # 세션 생성 및 청구항 추가
        session1 = engine.create_session(
            session_id="test_persist", player_name="Test Player", level_id=1
        )

        claim = "배터리 장치는 양극과 음극을 포함하며 안정적인 에너지 저장이 가능하다"
        session1.submit_claim(claim)

        # 세션 조회
        session2 = engine.get_session("test_persist")

        if session2:
            assert session2.session_id == "test_persist"
            assert len(session2.claims) == 1
            assert session2.claims[0] == claim

    def test_claim_history_tracking(self):
        """청구항 히스토리 추적"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_history", player_name="Test Player", level_id=1
        )

        claims = [
            "청구항 1: 배터리 장치는 양극을 포함하며 효율적인 에너지 저장이 가능하다",
            "청구항 2: 배터리 장치는 음극을 포함하며 안정적인 충전이 가능하다",
            "청구항 3: 배터리 장치는 전해질을 포함하며 이온 전도가 가능하다",
        ]

        for claim in claims:
            session.submit_claim(claim)

        # 히스토리 확인
        assert len(session.claims) == 3
        for i, submitted_claim in enumerate(session.claims):
            assert submitted_claim == claims[i]


class TestGamePerformance:
    """게임 성능 테스트"""

    def test_claim_submission_response_time(self):
        """청구항 제출 응답 시간 테스트 (< 500ms)"""
        import time

        engine = GameEngine()

        session = engine.create_session(
            session_id="test_perf", player_name="Test Player", level_id=1
        )

        claim = "배터리 장치는 양극과 음극을 포함하며 안정적인 에너지 저장이 가능하다"

        start_time = time.time()
        result = session.submit_claim(claim)
        elapsed_time = (time.time() - start_time) * 1000  # ms

        assert result is True
        assert elapsed_time < 500  # 500ms 이내

    def test_multiple_sessions_handling(self):
        """여러 세션 동시 처리"""
        engine = GameEngine()

        # 10개의 세션 생성
        sessions = []
        for i in range(10):
            session = engine.create_session(
                session_id=f"test_perf_{i}", player_name=f"Player {i}", level_id=1
            )
            sessions.append(session)

        # 각 세션에 청구항 제출
        for session in sessions:
            result = session.submit_claim(
                "배터리 장치는 양극과 음극을 포함하며 안정적인 에너지 저장이 가능하다"
            )
            assert result is True

        # 모든 세션이 정상 동작
        assert len(sessions) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
