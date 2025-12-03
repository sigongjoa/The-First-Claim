"""
Game Interface 테스트

청구항 작성 게임 인터페이스를 테스트합니다.
"""

import pytest
from src.ui.game import (
    GameLevel,
    PlayerProgress,
    GameSession,
    GameEngine,
    GameInterface,
    Difficulty,
    GameStatus,
)


class TestGameLevel:
    """GameLevel 클래스 테스트"""

    def test_create_level(self):
        """게임 레벨 생성"""
        level = GameLevel(
            level_id=1,
            title="기본 청구항",
            description="간단한 청구항",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        assert level.level_id == 1
        assert level.title == "기본 청구항"
        assert level.difficulty == Difficulty.EASY

    def test_invalid_level_id(self):
        """유효하지 않은 레벨 ID"""
        with pytest.raises(ValueError):
            GameLevel(
                level_id=0,
                title="기본 청구항",
                description="간단한 청구항",
                difficulty=Difficulty.EASY,
                target_claims=1,
            )

    def test_empty_title_fails(self):
        """빈 제목은 실패"""
        with pytest.raises(ValueError):
            GameLevel(
                level_id=1,
                title="",
                description="간단한 청구항",
                difficulty=Difficulty.EASY,
                target_claims=1,
            )

    def test_invalid_target_claims(self):
        """유효하지 않은 target_claims"""
        with pytest.raises(ValueError):
            GameLevel(
                level_id=1,
                title="기본 청구항",
                description="간단한 청구항",
                difficulty=Difficulty.EASY,
                target_claims=0,
            )


class TestPlayerProgress:
    """PlayerProgress 클래스 테스트"""

    def test_create_player(self):
        """플레이어 생성"""
        player = PlayerProgress(player_name="김철학")

        assert player.player_name == "김철학"
        assert player.current_level == 1
        assert player.total_score == 0

    def test_add_score(self):
        """점수 추가"""
        player = PlayerProgress(player_name="김철학")

        player.add_score(100)
        assert player.total_score == 100

        player.add_score(50)
        assert player.total_score == 150

    def test_negative_score_fails(self):
        """음수 점수 추가 실패"""
        player = PlayerProgress(player_name="김철학")

        with pytest.raises(ValueError):
            player.add_score(-100)

    def test_complete_level(self):
        """레벨 완료"""
        player = PlayerProgress(player_name="김철학")

        player.complete_level(1)
        assert 1 in player.completed_levels

        player.complete_level(2)
        assert 2 in player.completed_levels

    def test_empty_player_name_fails(self):
        """빈 플레이어 이름은 실패"""
        with pytest.raises(ValueError):
            PlayerProgress(player_name="")


class TestGameSession:
    """GameSession 클래스 테스트"""

    def test_create_session(self):
        """게임 세션 생성"""
        player = PlayerProgress(player_name="김철학")
        level = GameLevel(
            level_id=1,
            title="기본",
            description="기본",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        session = GameSession(
            session_id="session_001",
            player=player,
            current_level=level,
        )

        assert session.session_id == "session_001"
        assert session.status == GameStatus.IDLE

    def test_start_game(self):
        """게임 시작"""
        player = PlayerProgress(player_name="김철학")
        level = GameLevel(
            level_id=1,
            title="기본",
            description="기본",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        session = GameSession(
            session_id="session_001",
            player=player,
            current_level=level,
        )

        session.start_game(start_time=1000.0)

        assert session.status == GameStatus.IN_PROGRESS
        assert session.start_time == 1000.0

    def test_submit_claim(self):
        """청구항 제출"""
        player = PlayerProgress(player_name="김철학")
        level = GameLevel(
            level_id=1,
            title="기본",
            description="기본",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        session = GameSession(
            session_id="session_001",
            player=player,
            current_level=level,
        )

        claim = "배터리 장치는 양극, 음극, 전해질을 포함한다"
        session.submit_claim(claim)

        assert len(session.submitted_claims) == 1
        assert session.submitted_claims[0] == claim

    def test_submit_empty_claim_fails(self):
        """빈 청구항 제출 실패"""
        player = PlayerProgress(player_name="김철학")
        level = GameLevel(
            level_id=1,
            title="기본",
            description="기본",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        session = GameSession(
            session_id="session_001",
            player=player,
            current_level=level,
        )

        with pytest.raises(ValueError):
            session.submit_claim("")

    def test_complete_game(self):
        """게임 종료"""
        player = PlayerProgress(player_name="김철학")
        level = GameLevel(
            level_id=1,
            title="기본",
            description="기본",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        session = GameSession(
            session_id="session_001",
            player=player,
            current_level=level,
        )

        session.complete_game(end_time=2000.0, success=True)

        assert session.status == GameStatus.COMPLETED
        assert session.end_time == 2000.0


class TestGameEngine:
    """GameEngine 클래스 테스트"""

    def test_engine_creation(self):
        """게임 엔진 생성"""
        engine = GameEngine()

        assert len(engine.levels) > 0
        assert len(engine.sessions) == 0

    def test_get_level(self):
        """레벨 조회"""
        engine = GameEngine()

        level = engine.get_level(1)

        assert level is not None
        assert level.level_id == 1

    def test_get_nonexistent_level(self):
        """존재하지 않는 레벨 조회"""
        engine = GameEngine()

        level = engine.get_level(999)

        assert level is None

    def test_create_session(self):
        """세션 생성"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="session_001",
            player_name="김철학",
            level_id=1,
        )

        assert session is not None
        assert session.player.player_name == "김철학"
        assert session.current_level.level_id == 1

    def test_get_session(self):
        """세션 조회"""
        engine = GameEngine()

        engine.create_session(
            session_id="session_001",
            player_name="김철학",
            level_id=1,
        )

        session = engine.get_session("session_001")

        assert session is not None

    def test_evaluate_claims_success(self):
        """청구항 평가 - 성공"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="session_001",
            player_name="김철학",
            level_id=1,
        )

        session.submit_claim("배터리 장치는 양극, 음극, 전해질을 포함한다")

        success, feedback, details = engine.evaluate_claims("session_001")

        assert success is True

    def test_evaluate_claims_insufficient(self):
        """청구항 평가 - 부족"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="session_001",
            player_name="김철학",
            level_id=2,  # 3개 필요
        )

        session.submit_claim("배터리 장치는 양극, 음극, 전해질을 포함한다")

        success, feedback, details = engine.evaluate_claims("session_001")

        assert success is False


class TestGameInterface:
    """GameInterface 클래스 테스트"""

    def test_interface_creation(self):
        """게임 인터페이스 생성"""
        interface = GameInterface()

        assert interface.engine is not None

    def test_display_welcome(self):
        """환영 메시지 표시"""
        interface = GameInterface()

        message = interface.display_welcome()

        assert "환영합니다" in message
        assert "청구항 작성 게임" in message

    def test_display_level_info(self):
        """레벨 정보 표시"""
        interface = GameInterface()

        level = interface.engine.get_level(1)
        message = interface.display_level_info(level)

        assert "설명" in message
        assert "청구항" in message

    def test_display_progress(self):
        """플레이어 진행 상황 표시"""
        interface = GameInterface()

        player = PlayerProgress(player_name="김철학")
        message = interface.display_progress(player)

        assert "김철학" in message
        assert "진행 상황" in message

    def test_display_result_success(self):
        """성공 결과 표시"""
        interface = GameInterface()

        message = interface.display_result(
            success=True,
            feedback=["✅ 청구항 1: 올바른 형식입니다"],
            details={"total_submitted": 1, "required": 1},
        )

        assert "축하합니다" in message
        assert "통과" in message


class TestGameScenarios:
    """실제 게임 시나리오"""

    def test_complete_game_session(self):
        """완전한 게임 세션"""
        engine = GameEngine()
        interface = GameInterface()

        # 1. 세션 생성
        session = engine.create_session(
            session_id="game_001",
            player_name="김철학",
            level_id=1,
        )

        assert session is not None

        # 2. 게임 시작
        session.start_game(start_time=1000.0)
        assert session.status == GameStatus.IN_PROGRESS

        # 3. 청구항 제출
        session.submit_claim("배터리 장치는 양극, 음극, 전해질을 포함한다")

        # 4. 평가
        success, feedback, details = engine.evaluate_claims("game_001")

        # 5. 게임 종료
        session.complete_game(end_time=2000.0, success=success)

        assert session.status == GameStatus.COMPLETED
        assert success is True

    def test_multi_level_progression(self):
        """다중 레벨 진행"""
        engine = GameEngine()

        # 레벨 1
        session1 = engine.create_session(
            session_id="game_001",
            player_name="김철학",
            level_id=1,
        )

        session1.submit_claim("배터리 장치는 양극, 음극, 전해질을 포함한다")
        success1, _, _ = engine.evaluate_claims("game_001")

        assert success1 is True

        # 레벨 2
        session2 = engine.create_session(
            session_id="game_002",
            player_name="김철학",
            level_id=2,
        )

        session2.submit_claim("배터리 장치는 양극, 음극, 전해질을 포함한다")
        session2.submit_claim("제1항의 배터리에서 양극은 리튬 함유 물질로 이루어진다")
        session2.submit_claim("제1항의 배터리에서 음극은 흑연으로 이루어진다")

        success2, _, _ = engine.evaluate_claims("game_002")

        assert success2 is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
