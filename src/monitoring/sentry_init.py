"""
Sentry Error Tracking Initialization

프로덕션 에러 추적 및 모니터링을 위한 Sentry SDK 설정
"""

import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry(environment: str = "development", flask_app=None):
    """
    Sentry SDK 초기화

    Args:
        environment: 실행 환경 (development, staging, production)
        flask_app: Flask 앱 인스턴스 (선택적)

    Example:
        from src.monitoring.sentry_init import init_sentry

        init_sentry(
            environment='production',
            flask_app=app
        )
    """

    # Sentry DSN (프로젝트별로 설정 필요)
    # https://sentry.io에서 프로젝트 생성 후 DSN 가져오기
    sentry_dsn = os.getenv(
        'SENTRY_DSN',
        'https://example@o0.ingest.sentry.io/0'  # 기본값 (작동하지 않음)
    )

    # Sentry SDK 초기화
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,

        # 성능 모니터링 (5% 샘플링)
        traces_sample_rate=0.05,

        # 에러 샘플링 (프로덕션에서는 100%)
        sample_rate=1.0 if environment == 'production' else 0.5,

        # Flask 통합
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
        ],

        # 릴리스 정보
        release=os.getenv('APP_VERSION', '0.1.0'),

        # 에러 필터링 (특정 에러 무시)
        ignore_errors=[
            'ResizeObserver',  # 브라우저 에러
            'NetworkError',    # 네트워크 에러
        ],

        # 민감한 정보 필터링
        before_send=_filter_sensitive_data,
    )

    print(f"✅ Sentry initialized for {environment} environment")

    # Flask 앱이 있으면 통합
    if flask_app:
        _setup_flask_routes(flask_app)


def _filter_sensitive_data(event, hint):
    """민감한 데이터 필터링"""

    # 사용자 정보 제거
    if 'request' in event:
        if 'cookies' in event['request']:
            del event['request']['cookies']
        if 'headers' in event['request']:
            # 인증 헤더 제거
            headers = event['request']['headers']
            if 'Authorization' in headers:
                headers['Authorization'] = '[REDACTED]'
            if 'Cookie' in headers:
                headers['Cookie'] = '[REDACTED]'

    # 에러 메시지에서 민감한 정보 제거
    if 'exception' in event:
        for exception in event.get('exception', {}).get('values', []):
            if 'value' in exception:
                # 경로 정보 제거
                exception['value'] = _redact_paths(exception['value'])

    return event


def _redact_paths(text: str) -> str:
    """경로 정보 제거"""
    import re
    # 절대 경로 패턴 제거
    text = re.sub(r'/[a-zA-Z0-9_/\-\.]+', '/***', text)
    return text


def _setup_flask_routes(app):
    """Flask 라우트에 Sentry 통합"""

    @app.errorhandler(Exception)
    def handle_exception(error):
        """예외 처리기"""
        sentry_sdk.capture_exception(error)

        # Flask 기본 에러 핸들러 호출
        return {
            'error': str(error),
            'status': 500,
            'message': 'Internal Server Error'
        }, 500

    @app.before_request
    def before_request():
        """요청 전에 Sentry 사용자 정보 설정"""
        from flask import request

        # 사용자 정보 설정 (예: 세션에서)
        if hasattr(request, 'user_id'):
            sentry_sdk.set_user({
                'id': request.user_id,
                'ip_address': request.remote_addr,
            })

        # 태그 설정
        sentry_sdk.set_tag('endpoint', request.endpoint)
        sentry_sdk.set_tag('method', request.method)


def capture_message(message: str, level: str = 'info', **tags):
    """메시지 캡처"""
    for key, value in tags.items():
        sentry_sdk.set_tag(key, value)

    sentry_sdk.capture_message(message, level=level)


def capture_exception(exception: Exception, **tags):
    """예외 캡처"""
    for key, value in tags.items():
        sentry_sdk.set_tag(key, value)

    sentry_sdk.capture_exception(exception)


def set_user_context(user_id: str, email: str = None, username: str = None):
    """사용자 컨텍스트 설정"""
    sentry_sdk.set_user({
        'id': user_id,
        'email': email,
        'username': username,
    })


def set_context(name: str, context_dict: dict):
    """커스텀 컨텍스트 설정"""
    sentry_sdk.set_context(name, context_dict)


def set_tag(key: str, value):
    """태그 설정"""
    sentry_sdk.set_tag(key, value)


# Example usage in your application:
#
# from src.monitoring.sentry_init import init_sentry, capture_exception
#
# # 앱 시작 시
# init_sentry(environment='production', flask_app=app)
#
# # 에러 발생 시
# try:
#     # 어떤 작업
#     pass
# except Exception as e:
#     capture_exception(e, feature='claim_evaluation')
