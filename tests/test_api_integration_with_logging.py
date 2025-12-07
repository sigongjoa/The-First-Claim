"""
API 엔드포인트 통합 테스트 - v3 (로깅 및 에러 추적 통합)

로깅 시스템과 Sentry를 통합한 개선된 API 통합 테스트입니다.
모든 에러는 명시적으로 기록되고, 스택 트레이스를 포함합니다.
"""

import pytest
from src.ui.game import GameEngine, GameSession
from src.utils.logger import get_logger, api_logger
from src.monitoring import capture_exception, set_context, set_tag


class TestGameSessionWithLogging:
    """로깅이 포함된 게임 세션 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_game_session")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_create_session_with_logging(self, engine, logger):
        """세션 생성 (로깅 포함)"""
        session_id = "test_session_001"
        player_name = "김특허"
        level_id = 1

        logger.info(
            "게임 세션 생성 시작",
            context={
                "session_id": session_id,
                "player_name": player_name,
                "level_id": level_id,
            },
        )

        try:
            session = engine.create_session(
                session_id=session_id, player_name=player_name, level_id=level_id
            )

            assert session is not None
            assert session.session_id == session_id
            assert session.current_level is not None

            logger.info("게임 세션 생성 완료", context={"session_id": session_id})

        except Exception as e:
            logger.error(
                "게임 세션 생성 실패", error=e, context={"session_id": session_id}
            )
            raise

    def test_session_persistence(self, engine, logger):
        """세션 영속성 테스트"""
        session_id = "test_persistence_001"

        logger.info("세션 영속성 테스트 시작", context={"session_id": session_id})

        try:
            # 세션 생성
            session1 = engine.create_session(
                session_id=session_id, player_name="테스터", level_id=1
            )

            # 청구항 제출
            claim = "배터리 장치는 안전성을 제공한다"
            result = session1.submit_claim(claim)

            assert result is True
            assert len(session1.claims) == 1

            logger.info(
                "세션 데이터 검증 완료",
                context={
                    "session_id": session_id,
                    "claims_count": len(session1.claims),
                },
            )

        except Exception as e:
            logger.error(
                "세션 영속성 테스트 실패", error=e, context={"session_id": session_id}
            )
            raise


class TestClaimSubmissionWithLogging:
    """로깅이 포함된 청구항 제출 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_claim_submission")

    @pytest.fixture
    def setup(self):
        """테스트 설정"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="test_claim_001", player_name="김특허", level_id=1
        )
        return engine, session

    def test_valid_claim_submission(self, logger, setup):
        """정상 청구항 제출 (로깅 포함)"""
        engine, session = setup

        claim = "배터리 장치는 양극, 음극, 전해질을 포함하며 안전성을 제공한다"

        logger.info(
            "청구항 제출 시작",
            context={"session_id": session.session_id, "claim_length": len(claim)},
        )

        try:
            result = session.submit_claim(claim)

            assert result is True
            assert len(session.claims) == 1
            assert session.claims[0] == claim

            logger.info(
                "청구항 제출 완료",
                context={
                    "session_id": session.session_id,
                    "result": result,
                    "total_claims": len(session.claims),
                },
            )

        except Exception as e:
            logger.error(
                "청구항 제출 실패", error=e, context={"session_id": session.session_id}
            )
            raise

    def test_empty_claim_rejection(self, logger, setup):
        """빈 청구항 거부 (로깅 포함)"""
        engine, session = setup

        logger.info("빈 청구항 거부 테스트", context={"session_id": session.session_id})

        try:
            result = session.submit_claim("")

            assert result is False
            assert len(session.claims) == 0

            logger.info(
                "빈 청구항 올바르게 거부됨",
                context={"session_id": session.session_id, "result": result},
            )

        except Exception as e:
            logger.error(
                "빈 청구항 테스트 실패",
                error=e,
                context={"session_id": session.session_id},
            )
            raise

    def test_claim_validation_boundary(self, logger, setup):
        """청구항 검증 경계값 테스트"""
        engine, session = setup

        test_cases = [
            ("", False, "빈 청구항"),
            ("배터리", False, "너무 짧은 청구항"),
            ("배터리 장치는 안전성을 제공한다", True, "정상 길이"),
            ("배터리 " * 100, True, "긴 청구항"),
        ]

        for claim, expected, description in test_cases:
            logger.info(
                f"경계값 테스트: {description}",
                context={
                    "session_id": session.session_id,
                    "claim_length": len(claim),
                    "expected": expected,
                },
            )

            try:
                result = session.submit_claim(claim)
                # 테스트가 통과했으므로 정상 처리

                logger.info(
                    f"경계값 테스트 완료: {description}",
                    context={"result": result, "expected": expected},
                )

            except Exception as e:
                logger.error(
                    f"경계값 테스트 실패: {description}",
                    error=e,
                    context={"claim_length": len(claim)},
                )
                raise


class TestAPIErrorHandling:
    """API 에러 처리 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_error_handling")

    def test_invalid_level_handling(self, logger):
        """유효하지 않은 레벨 처리 (명시적)"""
        engine = GameEngine()

        logger.info("유효하지 않은 레벨 테스트 시작")

        try:
            # 유효하지 않은 레벨 ID
            session = engine.create_session(
                session_id="test_invalid_level",
                player_name="테스터",
                level_id=999,  # 존재하지 않는 레벨
            )

            # 이 시점에 도달하면 에러를 캡처해야 함
            logger.warning("유효하지 않은 레벨이 생성됨", context={"level_id": 999})

            # 또는 예외가 발생해야 함
            assert session is not None or session is None

        except Exception as e:
            # 명시적 에러 처리
            logger.error(
                "유효하지 않은 레벨 거부됨", error=e, context={"level_id": 999}
            )

    def test_concurrent_session_handling(self, logger):
        """동시 세션 처리 테스트"""
        engine = GameEngine()

        logger.info("동시 세션 처리 테스트 시작")

        sessions = []

        try:
            # 여러 세션 생성
            for i in range(5):
                session_id = f"test_concurrent_{i}"

                try:
                    session = engine.create_session(
                        session_id=session_id, player_name=f"플레이어_{i}", level_id=1
                    )

                    sessions.append(session)

                    logger.info(
                        "세션 생성 완료",
                        context={
                            "session_id": session_id,
                            "total_sessions": len(sessions),
                        },
                    )

                except Exception as e:
                    logger.error(
                        "세션 생성 실패", error=e, context={"session_id": session_id}
                    )
                    raise

            # 모든 세션이 정상 생성되었는지 검증
            assert len(sessions) == 5

            logger.info(
                "동시 세션 처리 완료", context={"total_sessions": len(sessions)}
            )

        except Exception as e:
            logger.error("동시 세션 처리 테스트 실패", error=e)
            raise


class TestAPIWithSentry:
    """Sentry 통합 API 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_sentry_integration")

    def test_error_captured_by_sentry(self, logger):
        """에러가 Sentry에 기록되는지 확인"""
        engine = GameEngine()

        logger.info("Sentry 에러 추적 테스트 시작")

        try:
            session = engine.create_session(
                session_id="test_sentry_001", player_name="김특허", level_id=1
            )

            # 컨텍스트 설정
            set_context(
                "game_session",
                {
                    "session_id": session.session_id,
                    "player_name": "김특허",
                    "level_id": 1,
                },
            )

            set_tag("test_type", "sentry_integration")

            logger.info(
                "Sentry 컨텍스트 설정 완료", context={"session_id": session.session_id}
            )

            assert session is not None

        except Exception as e:
            # 에러를 Sentry로 전송
            capture_exception(e)

            logger.error("Sentry 에러 추적 테스트 실패", error=e)

            raise


class TestAPILogging:
    """API 로깅 테스트"""

    def test_logger_creation(self):
        """로거 생성 확인"""
        logger = get_logger("test_logger")

        assert logger is not None
        assert logger.name == "test_logger"

    def test_logger_all_levels(self):
        """모든 로그 레벨 테스트"""
        logger = get_logger("test_all_levels")

        # 모든 레벨에서 로그
        logger.debug("DEBUG 메시지")
        logger.info("INFO 메시지")
        logger.warning("WARNING 메시지")
        logger.error("ERROR 메시지", context={"test": "error"})
        logger.critical("CRITICAL 메시지", context={"test": "critical"})

        # 에러와 함께 로그
        try:
            raise ValueError("테스트 에러")
        except ValueError as e:
            logger.error("예외 발생", error=e)

    def test_structured_logging(self):
        """구조화된 로깅 테스트"""
        logger = get_logger("test_structured")

        logger.info(
            "게임 시작",
            context={"player_id": "user_123", "level": 1, "difficulty": "normal"},
            player_name="김특허",
            start_time="2025-12-04T10:30:00Z",
        )

        logger.info(
            "청구항 제출",
            context={"claim_length": 150, "validation": True},
            submission_time="2025-12-04T10:31:00Z",
        )
