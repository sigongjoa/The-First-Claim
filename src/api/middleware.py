"""
API Middleware - 요청 추적 미들웨어

모든 API 요청을 추적하고, 요청 ID(correlation ID)를 추가합니다.
응답 시간을 측정하고 메트릭으로 기록합니다.
"""

import uuid
import time
import logging
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """요청 추적 미들웨어

    모든 요청에 correlation ID를 할당하고,
    요청 시간을 측정하며, 메트릭을 기록합니다.
    """

    def __init__(self, app: ASGIApp):
        """미들웨어 초기화

        Args:
            app: ASGI 애플리케이션
        """
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """요청 처리 및 추적

        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어/핸들러 호출

        Returns:
            HTTP 응답 (correlation ID 포함)
        """
        # Step 1: Request ID 생성
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Step 2: 시작 시간 기록
        start_time = time.time()

        # Step 3: 요청 로깅
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
            }
        )

        try:
            # Step 4: 다음 핸들러 호출
            response = await call_next(request)

            # Step 5: 응답 시간 계산
            duration = time.time() - start_time

            # Step 6: 메트릭 업데이트
            self._track_metrics(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )

            # Step 7: Response에 Request ID 추가
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            # Step 8: 응답 로깅
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} -> {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                }
            )

            return response

        except Exception as e:
            # Step 9: 예외 처리
            duration = time.time() - start_time

            # 메트릭 업데이트 (500 에러)
            self._track_metrics(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=duration
            )

            # 예외 로깅
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} -> ERROR",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": duration,
                    "error": str(e),
                }
            )

            # 예외 재발생
            raise

    def _track_metrics(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float
    ) -> None:
        """메트릭 추적

        Args:
            method: HTTP 메서드
            path: 요청 경로
            status_code: HTTP 상태 코드
            duration: 요청 처리 시간 (초)
        """
        try:
            from ..monitoring.observability_metrics import track_request

            track_request(
                method=method,
                endpoint=path,
                status_code=status_code,
                duration=duration
            )
        except ImportError:
            # 메트릭 모듈이 없으면 무시
            pass
        except Exception as e:
            logger.warning(f"Failed to track metrics: {e}")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """상관관계 ID 미들웨어

    X-Trace-ID 헤더를 통해 분산 추적을 지원합니다.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """상관관계 ID 추적

        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어/핸들러 호출

        Returns:
            HTTP 응답
        """
        # 기존 trace ID 사용 또는 새로 생성
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """로깅 미들웨어

    구조화된 로깅을 제공합니다.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """로깅 처리

        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어/핸들러 호출

        Returns:
            HTTP 응답
        """
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))

        # 요청 정보 로깅
        logger.info(
            f"Incoming request",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )

        response = await call_next(request)

        # 응답 정보 로깅
        logger.info(
            f"Response sent",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", "unknown"),
            }
        )

        return response
