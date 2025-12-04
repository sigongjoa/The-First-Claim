"""
Game Engine 테스트

게임 엔진의 모든 컴포넌트를 테스트합니다.
"""

import pytest
import time
from src.ui.game import (
    GameEngine,
    GameInterface,
    GameLevel,
    GameSession,
    PlayerProgress,
    Difficulty,
    GameStatus,
)


class TestGameLevel:
    """게임 레벨 테스트"""

    def test_create_level(self):
        """레벨 생성"""
        level = GameLevel(
            level_id=1,
            title="기본 레벨",
            description="쉬운 레벨",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )

        assert level.level_id == 1
        assert level.title == "기본 레벨"
        assert level.difficulty == Difficulty.EASY

    def test_invalid_level_id(self):
        """유효하지 않은 레벨 ID"""
        with pytest.raises(ValueError):
            GameLevel(
                level_id=0,
                title="레벨",
                description="설명",
                difficulty=Difficulty.EASY,
                target_claims=1,
            )


class TestPlayerProgress:
    """플레이어 진행 상황 테스트"""

    def test_create_player(self):
        """플레이어 생성"""
        player = PlayerProgress(player_name="테스트 플레이어")

        assert player.player_name == "테스트 플레이어"
        assert player.current_level == 1
        assert player.total_score == 0

    def test_add_score(self):
        """점수 추가"""
        player = PlayerProgress(player_name="테스트 플레이어")
        player.add_score(100)

        assert player.total_score == 100


class TestGameSession:
    """게임 세션 테스트"""

    def test_create_session(self):
        """세션 생성"""
        player = PlayerProgress(player_name="테스트 플레이어")
        level = GameLevel(
            level_id=1,
            title="레벨",
            description="설명",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )
        session = GameSession(
            session_id="test_session",
            player=player,
            current_level=level,
        )

        assert session.session_id == "test_session"
        assert session.status == GameStatus.IDLE

    def test_start_game(self):
        """게임 시작"""
        player = PlayerProgress(player_name="테스트 플레이어")
        level = GameLevel(
            level_id=1,
            title="레벨",
            description="설명",
            difficulty=Difficulty.EASY,
            target_claims=1,
        )
        session = GameSession(
            session_id="test_session",
            player=player,
            current_level=level,
        )

        start_time = time.time()
        session.start_game(start_time)

        assert session.status == GameStatus.IN_PROGRESS
        assert session.start_time == start_time


class TestGameEngine:
    """게임 엔진 테스트"""

    def test_engine_creation(self):
        """게임 엔진 생성"""
        engine = GameEngine()

        assert engine is not None
        assert len(engine.levels) > 0
        assert len(engine.sessions) == 0

    def test_get_level(self):
        """레벨 조회"""
        engine = GameEngine()
        level = engine.get_level(1)

        assert level is not None
        assert level.level_id == 1

    def test_create_session(self):
        """세션 생성"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="test_session",
            player_name="테스트 플레이어",
            level_id=1,
        )

        assert session is not None
        assert session.session_id == "test_session"
        assert session.player.player_name == "테스트 플레이어"


class TestGameInterface:
    """게임 사용자 인터페이스 테스트"""

    def test_interface_creation(self):
        """게임 인터페이스 생성"""
        interface = GameInterface()

        assert interface is not None
        assert interface.engine is not None

    def test_display_welcome(self):
        """환영 메시지"""
        interface = GameInterface()
        message = interface.display_welcome()

        assert "청구항" in message
        assert "환영" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
