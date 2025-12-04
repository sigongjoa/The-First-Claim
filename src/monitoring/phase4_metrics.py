"""
Phase 4 Performance & Security Monitoring

성능 메트릭과 보안 이벤트를 Sentry로 전송합니다.
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps
import sentry_sdk
from src.utils.logger import get_logger


logger = get_logger("monitoring")


class PerformanceMetrics:
    """성능 메트릭 수집"""

    @staticmethod
    def record_operation_time(operation_name: str, elapsed_ms: float, tags: Optional[Dict] = None):
        """작업 시간 기록"""
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("operation", operation_name)

                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)

                # 성능 메트릭을 컨텍스트로 추가
                scope.set_context("performance", {
                    "operation": operation_name,
                    "duration_ms": elapsed_ms,
                    "timestamp": datetime.utcnow().isoformat()
                })

                # 느린 작업은 경고
                if operation_name == "session_creation" and elapsed_ms > 100:
                    sentry_sdk.capture_message(
                        f"Slow session creation: {elapsed_ms}ms",
                        level="warning"
                    )
                    logger.warning(
                        "느린 세션 생성",
                        context={"operation": operation_name, "elapsed_ms": elapsed_ms}
                    )

                elif operation_name == "claim_submission" and elapsed_ms > 80:
                    sentry_sdk.capture_message(
                        f"Slow claim submission: {elapsed_ms}ms",
                        level="warning"
                    )
                    logger.warning(
                        "느린 청구항 제출",
                        context={"operation": operation_name, "elapsed_ms": elapsed_ms}
                    )

                logger.info(
                    f"작업 완료: {operation_name}",
                    context={"operation": operation_name, "elapsed_ms": round(elapsed_ms, 2)}
                )

        except Exception as e:
            logger.error("성능 메트릭 기록 실패", error=e)
            raise

    @staticmethod
    def record_throughput(operation_name: str, count: int, duration_seconds: float,
                         tags: Optional[Dict] = None):
        """처리량 기록"""
        try:
            throughput = count / duration_seconds if duration_seconds > 0 else 0

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("operation", operation_name)
                scope.set_tag("metric_type", "throughput")

                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)

                scope.set_context("throughput", {
                    "operation": operation_name,
                    "count": count,
                    "duration_seconds": duration_seconds,
                    "ops_per_second": round(throughput, 2)
                })

                logger.info(
                    f"처리량: {operation_name}",
                    context={
                        "operation": operation_name,
                        "count": count,
                        "ops_per_sec": round(throughput, 2)
                    }
                )

        except Exception as e:
            logger.error("처리량 기록 실패", error=e)
            raise

    @staticmethod
    def record_memory_usage(operation_name: str, memory_mb: float,
                           tags: Optional[Dict] = None):
        """메모리 사용량 기록"""
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("operation", operation_name)
                scope.set_tag("metric_type", "memory")

                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)

                scope.set_context("memory", {
                    "operation": operation_name,
                    "memory_mb": round(memory_mb, 2)
                })

                # 과도한 메모리 사용은 경고
                if memory_mb > 100:
                    sentry_sdk.capture_message(
                        f"High memory usage in {operation_name}: {memory_mb}MB",
                        level="warning"
                    )
                    logger.warning(
                        f"높은 메모리 사용: {operation_name}",
                        context={"operation": operation_name, "memory_mb": round(memory_mb, 2)}
                    )
                else:
                    logger.info(
                        f"메모리 사용: {operation_name}",
                        context={"operation": operation_name, "memory_mb": round(memory_mb, 2)}
                    )

        except Exception as e:
            logger.error("메모리 사용량 기록 실패", error=e)
            raise


class SecurityMetrics:
    """보안 메트릭 수집"""

    @staticmethod
    def record_security_event(event_type: str, severity: str, details: Dict[str, Any]):
        """보안 이벤트 기록"""
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("event_type", event_type)
                scope.set_tag("severity", severity)

                scope.set_context("security_event", details)

                if severity == "critical":
                    sentry_sdk.capture_message(
                        f"Critical Security Event: {event_type}",
                        level="error"
                    )
                    logger.error(
                        f"보안 이벤트: {event_type}",
                        context={"severity": severity, "details": details}
                    )

                elif severity == "high":
                    sentry_sdk.capture_message(
                        f"High Severity Security Event: {event_type}",
                        level="warning"
                    )
                    logger.warning(
                        f"보안 이벤트: {event_type}",
                        context={"severity": severity, "details": details}
                    )

                else:
                    logger.info(
                        f"보안 이벤트: {event_type}",
                        context={"severity": severity, "details": details}
                    )

        except Exception as e:
            logger.error("보안 이벤트 기록 실패 - CRITICAL", error=e)
            raise

    @staticmethod
    def record_input_validation_failure(input_type: str, value: str, reason: str):
        """입력 검증 실패 기록"""
        SecurityMetrics.record_security_event(
            event_type="input_validation_failure",
            severity="high",
            details={
                "input_type": input_type,
                "value": value[:50] if value else "",  # 민감한 데이터 마스킹
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def record_unauthorized_access_attempt(session_id: str, action: str):
        """무단 접근 시도 기록"""
        SecurityMetrics.record_security_event(
            event_type="unauthorized_access_attempt",
            severity="critical",
            details={
                "session_id": session_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    @staticmethod
    def record_data_integrity_check(entity_type: str, entity_id: str, status: str):
        """데이터 무결성 검사 기록"""
        severity = "high" if status == "failed" else "info"
        SecurityMetrics.record_security_event(
            event_type="data_integrity_check",
            severity=severity,
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


def performance_metric(operation_name: str):
    """성능 메트릭 데코레이터"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # 추가 태그 정보 추출
                tags = {"function": func.__name__}
                if args:
                    tags["has_args"] = True
                if kwargs:
                    tags["has_kwargs"] = True

                PerformanceMetrics.record_operation_time(operation_name, elapsed_ms, tags)

                return result

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(
                    f"작업 실패: {operation_name}",
                    error=e,
                    context={"elapsed_ms": round(elapsed_ms, 2)}
                )
                raise

        return wrapper
    return decorator


def security_check(check_type: str):
    """보안 검사 데코레이터"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # 검사 통과
                logger.info(
                    f"보안 검사 통과: {check_type}",
                    context={"check_type": check_type}
                )

                return result

            except Exception as e:
                logger.error(
                    f"보안 검사 실패: {check_type}",
                    error=e,
                    context={"check_type": check_type}
                )

                SecurityMetrics.record_security_event(
                    event_type=f"security_check_failed_{check_type}",
                    severity="high",
                    details={
                        "check_type": check_type,
                        "error": str(e)[:100]
                    }
                )
                raise

        return wrapper
    return decorator


class AlertThresholds:
    """경고 임계값 정의"""

    # 성능 임계값 (밀리초)
    SLOW_SESSION_CREATION = 100
    SLOW_CLAIM_SUBMISSION = 80
    SLOW_RESPONSE = 200

    # 메모리 임계값 (MB)
    HIGH_MEMORY_USAGE = 100
    CRITICAL_MEMORY_USAGE = 500

    # 보안 임계값
    MAX_FAILED_VALIDATIONS = 5
    MAX_CONCURRENT_SESSIONS = 1000

    @staticmethod
    def check_performance_alert(operation_name: str, elapsed_ms: float) -> bool:
        """성능 경고 확인"""
        thresholds = {
            "session_creation": AlertThresholds.SLOW_SESSION_CREATION,
            "claim_submission": AlertThresholds.SLOW_CLAIM_SUBMISSION,
        }

        threshold = thresholds.get(operation_name, AlertThresholds.SLOW_RESPONSE)

        if elapsed_ms > threshold:
            logger.warning(
                f"성능 경고: {operation_name}",
                context={
                    "operation": operation_name,
                    "elapsed_ms": round(elapsed_ms, 2),
                    "threshold_ms": threshold
                }
            )
            return True

        return False

    @staticmethod
    def check_memory_alert(memory_mb: float) -> bool:
        """메모리 경고 확인"""
        if memory_mb > AlertThresholds.CRITICAL_MEMORY_USAGE:
            logger.critical(
                "중대한 메모리 경고",
                context={"memory_mb": round(memory_mb, 2)}
            )
            return True

        elif memory_mb > AlertThresholds.HIGH_MEMORY_USAGE:
            logger.warning(
                "높은 메모리 경고",
                context={"memory_mb": round(memory_mb, 2)}
            )
            return True

        return False
