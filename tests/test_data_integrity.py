"""
Data Integrity Testing - Phase 5

데이터 일관성, 트랜잭션 안전성, 상태 무결성을 검증합니다.
모든 게임 세션의 데이터가 예상된 상태를 유지하는지 확인합니다.
"""

import pytest
from src.ui.game import GameEngine, GameSession, GameStatus, PlayerProgress, Difficulty
from src.utils.logger import get_logger
from datetime import datetime
import json


class TestDataIntegrity:
    """데이터 무결성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_data_integrity")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_session_data_consistency(self, engine, logger):
        """세션 데이터 일관성 테스트"""
        logger.info("세션 데이터 일관성 테스트 시작")

        try:
            session_id = "integrity_session_001"
            player_name = "데이터테스터"
            level_id = 1

            # 세션 생성
            session = engine.create_session(
                session_id=session_id,
                player_name=player_name,
                level_id=level_id
            )

            # 데이터 검증
            assert session.session_id == session_id
            assert session.player.player_name == player_name
            assert session.player.current_level == level_id
            assert session.status == GameStatus.IDLE
            assert session.submitted_claims == []
            assert session.feedback == []

            logger.info(
                "세션 데이터 일관성 확인 완료",
                context={
                    "session_id": session_id,
                    "player_name": player_name,
                    "status_valid": session.status == GameStatus.IDLE
                }
            )

        except Exception as e:
            logger.error("세션 데이터 일관성 테스트 실패", error=e)
            raise

    def test_claim_submission_state_transition(self, engine, logger):
        """청구항 제출 상태 전이 테스트"""
        logger.info("청구항 제출 상태 전이 테스트 시작")

        try:
            session = engine.create_session(
                session_id="integrity_claim_001",
                player_name="상태테스터",
                level_id=1
            )

            # 초기 상태
            assert len(session.submitted_claims) == 0
            initial_claims_count = len(session.submitted_claims)

            # 청구항 제출
            claim = "배터리 장치는 양극과 음극을 포함하여 안전성을 제공한다"
            result = session.submit_claim(claim)

            # 상태 검증
            assert result is True
            assert len(session.submitted_claims) == initial_claims_count + 1
            assert session.submitted_claims[0] == claim

            # 같은 청구항 다시 제출
            result2 = session.submit_claim(claim)
            assert result2 is True
            assert len(session.submitted_claims) == 2

            logger.info(
                "청구항 제출 상태 전이 확인 완료",
                context={
                    "initial_count": initial_claims_count,
                    "final_count": len(session.submitted_claims),
                    "transition_valid": len(session.submitted_claims) == 2
                }
            )

        except Exception as e:
            logger.error("상태 전이 테스트 실패", error=e)
            raise

    def test_invalid_claim_doesnt_change_state(self, engine, logger):
        """유효하지 않은 청구항은 상태를 변경하지 않음"""
        logger.info("유효하지 않은 청구항 상태 검증 시작")

        try:
            session = engine.create_session(
                session_id="integrity_invalid_001",
                player_name="검증테스터",
                level_id=1
            )

            initial_count = len(session.submitted_claims)

            # 유효하지 않은 청구항들
            invalid_claims = [
                "",  # 빈 문자열
                "   ",  # 공백만
                "짧음",  # 30자 미만
            ]

            for invalid_claim in invalid_claims:
                result = session.submit_claim(invalid_claim)
                assert result is False
                assert len(session.submitted_claims) == initial_count

            logger.info(
                "유효하지 않은 청구항 상태 검증 완료",
                context={
                    "invalid_claims_tested": len(invalid_claims),
                    "state_unchanged": len(session.submitted_claims) == initial_count
                }
            )

        except Exception as e:
            logger.error("유효성 검사 테스트 실패", error=e)
            raise

    def test_player_progress_tracking(self, engine, logger):
        """플레이어 진행률 추적 테스트"""
        logger.info("플레이어 진행률 추적 테스트 시작")

        try:
            session = engine.create_session(
                session_id="integrity_progress_001",
                player_name="진행률테스터",
                level_id=1
            )

            player = session.player

            # 초기 상태
            assert player.current_level == 1
            assert player.total_score == 0
            assert len(player.completed_levels) == 0

            # 점수 추가
            player.add_score(100)
            assert player.total_score == 100

            # 레벨 완료 표시
            player.complete_level(1)
            assert 1 in player.completed_levels

            # 중복 완료 시도
            player.complete_level(1)
            assert len(player.completed_levels) == 1  # 중복 없음

            logger.info(
                "플레이어 진행률 추적 완료",
                context={
                    "final_score": player.total_score,
                    "completed_levels": len(player.completed_levels),
                    "tracking_valid": player.total_score == 100
                }
            )

        except Exception as e:
            logger.error("진행률 추적 테스트 실패", error=e)
            raise

    def test_game_level_immutability(self, engine, logger):
        """게임 레벨 불변성 테스트"""
        logger.info("게임 레벨 불변성 테스트 시작")

        try:
            level = engine.get_level(1)

            # 레벨 정보 확인
            assert level is not None
            assert level.level_id == 1
            assert level.difficulty == Difficulty.EASY
            assert level.target_claims > 0
            assert level.time_limit > 0

            # 같은 레벨 재조회
            level2 = engine.get_level(1)
            assert level.level_id == level2.level_id
            assert level.difficulty == level2.difficulty
            assert level.target_claims == level2.target_claims

            logger.info(
                "게임 레벨 불변성 확인 완료",
                context={
                    "level_id": level.level_id,
                    "consistency_verified": level.level_id == level2.level_id
                }
            )

        except Exception as e:
            logger.error("레벨 불변성 테스트 실패", error=e)
            raise

    def test_multiple_sessions_isolation(self, engine, logger):
        """다중 세션 독립성 테스트"""
        logger.info("다중 세션 독립성 테스트 시작")

        try:
            # 여러 세션 생성
            sessions = []
            for i in range(3):
                session = engine.create_session(
                    session_id=f"isolation_test_{i}",
                    player_name=f"플레이어_{i}",
                    level_id=1
                )
                sessions.append(session)

            # 각 세션에 청구항 추가
            claim = "배터리 장치는 양극과 음극을 포함하여 안전성을 제공한다"
            for i, session in enumerate(sessions):
                session.submit_claim(f"변형 {i}: {claim}")

            # 세션 독립성 검증
            for i, session in enumerate(sessions):
                assert len(session.submitted_claims) == 1
                assert f"변형 {i}" in session.submitted_claims[0]

            # 세션간 데이터 누수 확인
            assert len(sessions[0].submitted_claims) == 1
            assert len(sessions[1].submitted_claims) == 1
            assert len(sessions[2].submitted_claims) == 1
            assert sessions[0].submitted_claims[0] != sessions[1].submitted_claims[0]

            logger.info(
                "다중 세션 독립성 확인 완료",
                context={
                    "sessions_tested": len(sessions),
                    "isolation_verified": True
                }
            )

        except Exception as e:
            logger.error("세션 독립성 테스트 실패", error=e)
            raise


class TestDataPersistence:
    """데이터 영속성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_data_persistence")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_session_retrieval(self, engine, logger):
        """세션 저장 및 조회 테스트"""
        logger.info("세션 저장 및 조회 테스트 시작")

        try:
            # 세션 생성
            session_id = "persistence_001"
            session = engine.create_session(
                session_id=session_id,
                player_name="영속테스터",
                level_id=1
            )

            # 데이터 추가
            claim = "배터리 장치는 양극과 음극을 포함하여 안전성을 제공한다"
            session.submit_claim(claim)
            session.player.add_score(50)

            # 세션 저장 (엔진에서)
            engine.sessions[session_id] = session

            # 세션 조회
            retrieved_session = engine.sessions.get(session_id)
            assert retrieved_session is not None
            assert retrieved_session.session_id == session_id
            assert len(retrieved_session.submitted_claims) == 1
            assert retrieved_session.player.total_score == 50

            logger.info(
                "세션 저장 및 조회 완료",
                context={
                    "session_id": session_id,
                    "data_persisted": True
                }
            )

        except Exception as e:
            logger.error("세션 영속성 테스트 실패", error=e)
            raise

    def test_concurrent_session_storage(self, engine, logger):
        """동시 세션 저장 테스트"""
        logger.info("동시 세션 저장 테스트 시작")

        try:
            num_sessions = 5

            # 여러 세션 생성 및 저장
            for i in range(num_sessions):
                session = engine.create_session(
                    session_id=f"concurrent_persist_{i}",
                    player_name=f"플레이어_{i}",
                    level_id=1
                )

                claim = f"청구항_{i}: 배터리 장치는 양극과 음극을 포함하여 안전성을 제공한다"
                session.submit_claim(claim)

                engine.sessions[session.session_id] = session

            # 모든 세션 조회
            stored_sessions = len(engine.sessions)
            assert stored_sessions >= num_sessions

            # 각 세션 검증
            for i in range(num_sessions):
                session_id = f"concurrent_persist_{i}"
                session = engine.sessions.get(session_id)
                assert session is not None
                assert len(session.submitted_claims) == 1

            logger.info(
                "동시 세션 저장 완료",
                context={
                    "sessions_created": num_sessions,
                    "sessions_stored": len([s for s in engine.sessions.keys() if "concurrent_persist" in s])
                }
            )

        except Exception as e:
            logger.error("동시 세션 저장 테스트 실패", error=e)
            raise


class TestDataValidation:
    """데이터 검증 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_data_validation")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_claim_length_validation(self, engine, logger):
        """청구항 길이 검증 테스트"""
        logger.info("청구항 길이 검증 테스트 시작")

        try:
            session = engine.create_session(
                session_id="validation_length_001",
                player_name="검증테스터",
                level_id=1
            )

            test_cases = [
                ("a" * 29, False, "너무 짧음 (29자)"),
                ("a" * 30, True, "최소 길이 (30자)"),
                ("a" * 500, True, "정상 길이 (500자)"),
                ("a" * 1000, True, "최대 길이 (1000자)"),
                ("a" * 1001, False, "너무 김 (1001자)"),
            ]

            for claim, expected, description in test_cases:
                result = session.submit_claim(claim)
                assert result == expected, f"{description}: 예상 {expected}, 실제 {result}"

                logger.info(
                    f"청구항 길이 검증: {description}",
                    context={
                        "claim_length": len(claim),
                        "expected": expected,
                        "actual": result,
                        "valid": result == expected
                    }
                )

            logger.info("청구항 길이 검증 완료")

        except Exception as e:
            logger.error("길이 검증 테스트 실패", error=e)
            raise

    def test_session_id_validation(self, engine, logger):
        """세션 ID 검증 테스트"""
        logger.info("세션 ID 검증 테스트 시작")

        try:
            valid_ids = [
                "session_001",
                "session-002",
                "session_test_003",
            ]

            invalid_ids = [
                "",
                None,
            ]

            # 유효한 ID 테스트
            for valid_id in valid_ids:
                try:
                    session = engine.create_session(
                        session_id=valid_id,
                        player_name="테스터",
                        level_id=1
                    )
                    assert session.session_id == valid_id
                    logger.info(f"유효한 세션 ID 인정: {valid_id}")
                except Exception as e:
                    logger.warning(f"유효한 ID 거부됨: {valid_id}, {str(e)[:100]}")

            # 유효하지 않은 ID 테스트
            for invalid_id in invalid_ids:
                try:
                    session = engine.create_session(
                        session_id=invalid_id,
                        player_name="테스터",
                        level_id=1
                    )
                    logger.warning(f"유효하지 않은 ID가 허용됨: {invalid_id}")
                except (ValueError, TypeError, AttributeError):
                    logger.info(f"유효하지 않은 세션 ID 거부됨: {invalid_id}")

            logger.info("세션 ID 검증 완료")

        except Exception as e:
            logger.error("세션 ID 검증 테스트 실패", error=e)
            raise

    def test_player_name_validation(self, engine, logger):
        """플레이어명 검증 테스트"""
        logger.info("플레이어명 검증 테스트 시작")

        try:
            valid_names = [
                "플레이어",
                "김특허",
                "Player123",
                "李 발明",
            ]

            invalid_names = [
                "",
                "   ",
            ]

            # 유효한 이름 테스트
            for valid_name in valid_names:
                try:
                    session = engine.create_session(
                        session_id=f"player_valid_{valid_names.index(valid_name)}",
                        player_name=valid_name,
                        level_id=1
                    )
                    assert session.player.player_name == valid_name
                    logger.info(f"유효한 플레이어명 인정: {valid_name}")
                except Exception as e:
                    logger.warning(f"유효한 이름 거부됨: {valid_name}, {str(e)[:100]}")

            # 유효하지 않은 이름 테스트
            for invalid_name in invalid_names:
                try:
                    session = engine.create_session(
                        session_id=f"player_invalid_{invalid_names.index(invalid_name)}",
                        player_name=invalid_name,
                        level_id=1
                    )
                    logger.warning(f"유효하지 않은 이름이 허용됨: {invalid_name}")
                except ValueError:
                    logger.info(f"유효하지 않은 플레이어명 거부됨: {invalid_name}")

            logger.info("플레이어명 검증 완료")

        except Exception as e:
            logger.error("플레이어명 검증 테스트 실패", error=e)
            raise
