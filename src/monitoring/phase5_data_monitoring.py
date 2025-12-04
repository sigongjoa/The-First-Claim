"""
Phase 5 Data Integrity Monitoring

데이터 무결성 이상을 감지하고 Sentry로 보고합니다.
"""

import sentry_sdk
from typing import Any, Dict, Optional, List
from datetime import datetime
from src.utils.logger import get_logger


logger = get_logger("monitoring_data")


class DataIntegrityMonitor:
    """데이터 무결성 모니터"""

    @staticmethod
    def verify_session_state(session: Any, expected_claims_count: Optional[int] = None) -> bool:
        """세션 상태 검증"""
        try:
            # 기본 검증
            assert session is not None
            assert hasattr(session, 'session_id')
            assert hasattr(session, 'player')
            assert hasattr(session, 'status')
            assert hasattr(session, 'submitted_claims')
            assert hasattr(session, 'feedback')

            # 타입 검증
            assert isinstance(session.session_id, str)
            assert isinstance(session.submitted_claims, list)
            assert isinstance(session.feedback, list)

            # 선택적 클레임 카운트 검증
            if expected_claims_count is not None:
                if len(session.submitted_claims) != expected_claims_count:
                    raise AssertionError(
                        f"청구항 수 불일치: 예상 {expected_claims_count}, "
                        f"실제 {len(session.submitted_claims)}"
                    )

            logger.info(
                "세션 상태 검증 통과",
                context={
                    "session_id": session.session_id,
                    "claims_count": len(session.submitted_claims)
                }
            )

            return True

        except AssertionError as e:
            logger.error(
                "세션 상태 검증 실패",
                error=e,
                context={
                    "session_id": getattr(session, 'session_id', 'unknown'),
                    "error_message": str(e)[:100]
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("data_integrity", "session_state")
                scope.set_tag("severity", "high")
                scope.set_context("session", {
                    "session_id": getattr(session, 'session_id', 'unknown'),
                    "claims_count": len(getattr(session, 'submitted_claims', []))
                })
                sentry_sdk.capture_exception(e)

            raise ValueError(f"Session state verification failed: {e}") from e

    @staticmethod
    def verify_player_progress(player: Any) -> bool:
        """플레이어 진행상황 검증"""
        try:
            # 기본 검증
            assert player is not None
            assert hasattr(player, 'player_name')
            assert hasattr(player, 'total_score')
            assert hasattr(player, 'completed_levels')

            # 타입 검증
            assert isinstance(player.player_name, str)
            assert isinstance(player.total_score, int)
            assert isinstance(player.completed_levels, list)

            # 값 검증
            assert player.total_score >= 0, "점수는 음수가 될 수 없음"
            assert all(isinstance(l, int) for l in player.completed_levels), \
                "완료된 레벨은 정수여야 함"

            # 중복 검증
            if len(player.completed_levels) != len(set(player.completed_levels)):
                raise AssertionError("완료된 레벨에 중복이 있음")

            logger.info(
                "플레이어 진행상황 검증 통과",
                context={
                    "player_name": player.player_name,
                    "total_score": player.total_score,
                    "completed_levels": len(player.completed_levels)
                }
            )

            return True

        except AssertionError as e:
            logger.error(
                "플레이어 진행상황 검증 실패",
                error=e,
                context={
                    "player_name": getattr(player, 'player_name', 'unknown'),
                    "error_message": str(e)[:100]
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("data_integrity", "player_progress")
                scope.set_tag("severity", "high")
                scope.set_context("player", {
                    "player_name": getattr(player, 'player_name', 'unknown'),
                    "total_score": getattr(player, 'total_score', 0)
                })
                sentry_sdk.capture_exception(e)

            raise ValueError(f"Player progress verification failed: {e}") from e

    @staticmethod
    def verify_claim_consistency(session: Any) -> bool:
        """청구항 일관성 검증"""
        try:
            claims = session.submitted_claims

            # 빈 리스트는 유효함
            if len(claims) == 0:
                return True

            # 타입 검증
            assert all(isinstance(c, str) for c in claims), "모든 청구항은 문자열이어야 함"

            # 길이 검증 (30-1000자)
            for i, claim in enumerate(claims):
                assert 30 <= len(claim) <= 1000, \
                    f"청구항 {i}: 길이 {len(claim)} (30-1000자여야 함)"

            logger.info(
                "청구항 일관성 검증 통과",
                context={
                    "session_id": session.session_id,
                    "claims_count": len(claims)
                }
            )

            return True

        except AssertionError as e:
            logger.error(
                "청구항 일관성 검증 실패",
                error=e,
                context={
                    "session_id": session.session_id,
                    "claims_count": len(session.submitted_claims),
                    "error_message": str(e)[:100]
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("data_integrity", "claim_consistency")
                scope.set_tag("severity", "high")
                scope.set_context("claims", {
                    "session_id": session.session_id,
                    "count": len(session.submitted_claims)
                })
                sentry_sdk.capture_exception(e)

            raise ValueError(f"Claim consistency verification failed: {e}") from e

    @staticmethod
    def verify_session_isolation(sessions: Dict[str, Any]) -> bool:
        """세션 간 데이터 격리 검증"""
        try:
            session_ids = set()
            claims_per_session = {}

            for session_id, session in sessions.items():
                # ID 중복 검증
                assert session_id not in session_ids, f"중복된 세션 ID: {session_id}"
                session_ids.add(session_id)

                # 세션 ID 일치 검증
                assert session.session_id == session_id, \
                    f"세션 ID 불일치: 실제 {session.session_id}, 키 {session_id}"

                # 청구항 목록 저장
                claims_per_session[session_id] = set(
                    id(c) for c in session.submitted_claims
                )

            # 세션 간 데이터 누수 검증
            all_claim_ids = set()
            for session_id, claim_ids in claims_per_session.items():
                overlapping = all_claim_ids.intersection(claim_ids)
                assert len(overlapping) == 0, \
                    f"세션 {session_id}의 청구항이 다른 세션과 겹침"
                all_claim_ids.update(claim_ids)

            logger.info(
                "세션 격리 검증 통과",
                context={
                    "total_sessions": len(sessions),
                    "isolation_verified": True
                }
            )

            return True

        except AssertionError as e:
            logger.error(
                "세션 격리 검증 실패 - CRITICAL DATA ISOLATION BREACH",
                error=e,
                context={
                    "total_sessions": len(sessions),
                    "error_message": str(e)[:100]
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("data_integrity", "session_isolation")
                scope.set_tag("severity", "critical")
                scope.set_context("sessions", {
                    "total_count": len(sessions)
                })
                sentry_sdk.capture_exception(e)

            raise ValueError(f"CRITICAL: Session isolation verification failed: {e}") from e


class DataIntegrityAlert:
    """데이터 무결성 경고"""

    # 경고 임계값
    CRITICAL_SCORE = -1  # 음수 점수
    CRITICAL_CLAIM_LENGTH = 1001  # 1000자 초과
    WARNING_DUPLICATE_COMPLETION = True  # 중복 완료

    @staticmethod
    def check_score_integrity(player: Any) -> bool:
        """점수 무결성 확인"""
        if player.total_score < 0:
            logger.critical(
                "중대한 데이터 무결성 문제: 음수 점수",
                context={
                    "player_name": player.player_name,
                    "total_score": player.total_score
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("alert_type", "critical_score")
                scope.set_tag("severity", "critical")
                sentry_sdk.capture_message(
                    f"Negative score detected: {player.total_score}",
                    level="critical"
                )

            return False

        return True

    @staticmethod
    def check_claim_length_integrity(claim: str) -> bool:
        """청구항 길이 무결성 확인"""
        claim_length = len(claim)

        if claim_length > DataIntegrityAlert.CRITICAL_CLAIM_LENGTH:
            logger.critical(
                "중대한 데이터 무결성 문제: 청구항 길이 초과",
                context={
                    "claim_length": claim_length,
                    "max_length": 1000
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("alert_type", "claim_length")
                scope.set_tag("severity", "critical")
                sentry_sdk.capture_message(
                    f"Claim length exceeded: {claim_length}",
                    level="critical"
                )

            return False

        return True

    @staticmethod
    def check_level_integrity(completed_levels: List[int]) -> bool:
        """레벨 완료 목록 무결성 확인"""
        if len(completed_levels) != len(set(completed_levels)):
            duplicates = len(completed_levels) - len(set(completed_levels))
            logger.warning(
                "경고: 레벨 완료 목록에 중복",
                context={
                    "total_count": len(completed_levels),
                    "unique_count": len(set(completed_levels)),
                    "duplicates": duplicates
                }
            )

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("alert_type", "duplicate_level")
                scope.set_tag("severity", "warning")
                sentry_sdk.capture_message(
                    f"Duplicate level completions detected",
                    level="warning"
                )

            return False

        return True
