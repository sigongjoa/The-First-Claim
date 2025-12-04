"""
Application Logging System

모든 에러와 중요 이벤트를 일관된 형식으로 기록합니다.
Sentry와 함께 작동하여 에러 추적을 보완합니다.
"""

import logging
import json
import traceback
from datetime import datetime
from typing import Any, Optional, Dict
from enum import Enum
from pathlib import Path


class LogLevel(Enum):
    """로그 레벨 정의"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class StructuredLogger:
    """
    구조화된 로깅을 제공합니다.

    모든 로그는 JSON 형식으로 저장되어 분석이 쉽습니다.
    """

    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        로거 초기화

        Args:
            name: 로거 이름 (모듈명 권장)
            log_file: 로그 파일 경로 (기본: logs/{name}.log)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 로그 디렉토리 생성
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 로그 파일 경로
        if log_file is None:
            log_file = log_dir / f"{name}.log"
        else:
            log_file = log_dir / log_file

        # 파일 핸들러 (JSON 형식)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter('%(message)s')
        )
        self.logger.addHandler(file_handler)

        # 콘솔 핸들러 (간단한 형식)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '[%(levelname)s] %(asctime)s - %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.logger.addHandler(console_handler)

    def _create_log_entry(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        **kwargs
    ) -> str:
        """
        로그 항목 생성

        Args:
            level: 로그 레벨
            message: 로그 메시지
            context: 추가 컨텍스트
            error: 예외 객체
            **kwargs: 추가 필드

        Returns:
            JSON 로그 문자열
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }

        # 추가 컨텍스트
        if context:
            entry["context"] = context

        # 예외 정보
        if error:
            entry["error"] = {
                "type": error.__class__.__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }

        # 추가 필드
        entry.update(kwargs)

        return json.dumps(entry, ensure_ascii=False)

    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        DEBUG 레벨 로그

        Args:
            message: 로그 메시지
            context: 추가 컨텍스트
            **kwargs: 추가 필드
        """
        log_entry = self._create_log_entry("DEBUG", message, context, **kwargs)
        self.logger.debug(log_entry)

    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        INFO 레벨 로그

        Args:
            message: 로그 메시지
            context: 추가 컨텍스트
            **kwargs: 추가 필드
        """
        log_entry = self._create_log_entry("INFO", message, context, **kwargs)
        self.logger.info(log_entry)

    def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        WARNING 레벨 로그

        Args:
            message: 로그 메시지
            context: 추가 컨텍스트
            **kwargs: 추가 필드
        """
        log_entry = self._create_log_entry("WARNING", message, context, **kwargs)
        self.logger.warning(log_entry)

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        ERROR 레벨 로그

        Args:
            message: 로그 메시지
            error: 예외 객체
            context: 추가 컨텍스트
            **kwargs: 추가 필드
        """
        log_entry = self._create_log_entry(
            "ERROR", message, context, error, **kwargs
        )
        self.logger.error(log_entry)

    def critical(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        CRITICAL 레벨 로그

        Args:
            message: 로그 메시지
            error: 예외 객체
            context: 추가 컨텍스트
            **kwargs: 추가 필드
        """
        log_entry = self._create_log_entry(
            "CRITICAL", message, context, error, **kwargs
        )
        self.logger.critical(log_entry)


# 애플리케이션별 로거 인스턴스
app_logger = StructuredLogger("app", "app.log")
api_logger = StructuredLogger("api", "api.log")
game_logger = StructuredLogger("game", "game.log")
llm_logger = StructuredLogger("llm", "llm.log")


def get_logger(name: str) -> StructuredLogger:
    """
    이름으로 로거 가져오기

    Args:
        name: 로거 이름

    Returns:
        StructuredLogger 인스턴스
    """
    return StructuredLogger(name)


# 편의 함수
def log_debug(message: str, **kwargs):
    """전역 DEBUG 로그"""
    app_logger.debug(message, **kwargs)


def log_info(message: str, **kwargs):
    """전역 INFO 로그"""
    app_logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """전역 WARNING 로그"""
    app_logger.warning(message, **kwargs)


def log_error(message: str, error: Optional[Exception] = None, **kwargs):
    """전역 ERROR 로그"""
    app_logger.error(message, error, **kwargs)


def log_critical(message: str, error: Optional[Exception] = None, **kwargs):
    """전역 CRITICAL 로그"""
    app_logger.critical(message, error, **kwargs)
