"""
SQLite Session Store - 영구적 세션 저장소 with TTL support

GameSession 데이터를 SQLite 데이터베이스에 저장합니다.
TTL(Time To Live) 기반 자동 만료 기능을 포함합니다.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from threading import RLock

from sqlalchemy import create_engine, Column, String, DateTime, Text, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession

from src.storage.session_store import SessionStore

logger = logging.getLogger(__name__)

Base = declarative_base()


class SessionRecord(Base):
    """SQLite 세션 레코드 모델"""

    __tablename__ = "game_sessions"

    session_id = Column(String(36), primary_key=True)
    data_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<SessionRecord session_id={self.session_id} created_at={self.created_at}>"


class SQLiteSessionStore(SessionStore):
    """SQLite 기반 세션 저장소"""

    def __init__(
        self,
        db_path: str = "data/sessions.db",
        ttl_seconds: int = 3600,
        auto_cleanup: bool = True
    ):
        """
        SQLiteSessionStore 초기화

        Args:
            db_path: SQLite 데이터베이스 파일 경로
            ttl_seconds: 세션 만료 시간 (초, 기본값 3600 = 1시간)
            auto_cleanup: 자동 정리 활성화 여부
        """
        # 디렉토리 생성
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        # 데이터베이스 엔진 설정
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True
        )

        # 테이블 생성
        Base.metadata.create_all(self.engine)

        # 세션 팩토리
        self.SessionFactory = sessionmaker(bind=self.engine)

        # 설정
        self.ttl_seconds = ttl_seconds
        self.auto_cleanup = auto_cleanup

        # 스레드 안전성
        self._lock = RLock()

        logger.info(f"SQLiteSessionStore initialized: {db_path}")

    def create(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        새 세션 생성

        Args:
            session_id: 세션 ID
            data: 세션 데이터

        Returns:
            None

        Raises:
            ValueError: 이미 존재하는 세션
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                # 이미 존재하는지 확인
                existing = db_session.query(SessionRecord).filter_by(
                    session_id=session_id
                ).first()

                if existing:
                    raise ValueError(f"Session {session_id} already exists")

                # 새 세션 레코드 생성
                now = datetime.utcnow()
                expires_at = now + timedelta(seconds=self.ttl_seconds)

                record = SessionRecord(
                    session_id=session_id,
                    data_json=json.dumps(data, ensure_ascii=False),
                    created_at=now,
                    updated_at=now,
                    expires_at=expires_at
                )

                db_session.add(record)
                db_session.commit()

                logger.debug(f"Created session: {session_id}")

            except Exception as e:
                db_session.rollback()
                logger.error(f"Failed to create session: {e}")
                raise
            finally:
                db_session.close()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        세션 데이터 조회

        Args:
            session_id: 세션 ID

        Returns:
            세션 데이터 (만료되었으면 None)
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                record = db_session.query(SessionRecord).filter_by(
                    session_id=session_id
                ).first()

                if not record:
                    return None

                # 만료 확인
                if record.expires_at and datetime.utcnow() > record.expires_at:
                    # 만료된 세션 삭제
                    db_session.delete(record)
                    db_session.commit()
                    logger.debug(f"Expired session deleted: {session_id}")
                    return None

                # 데이터 반환 (defensive copy)
                return json.loads(record.data_json)

            except Exception as e:
                logger.error(f"Failed to get session: {e}")
                return None
            finally:
                db_session.close()

    def update(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        세션 데이터 업데이트

        Args:
            session_id: 세션 ID
            data: 업데이트할 데이터

        Raises:
            KeyError: 세션이 존재하지 않음
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                record = db_session.query(SessionRecord).filter_by(
                    session_id=session_id
                ).first()

                if not record:
                    raise KeyError(f"Session {session_id} not found")

                # TTL 연장
                now = datetime.utcnow()
                record.data_json = json.dumps(data, ensure_ascii=False)
                record.updated_at = now
                record.expires_at = now + timedelta(seconds=self.ttl_seconds)

                db_session.commit()
                logger.debug(f"Updated session: {session_id}")

            except Exception as e:
                db_session.rollback()
                logger.error(f"Failed to update session: {e}")
                raise
            finally:
                db_session.close()

    def delete(self, session_id: str) -> None:
        """
        세션 삭제

        Args:
            session_id: 세션 ID

        Raises:
            KeyError: 세션이 존재하지 않음
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                record = db_session.query(SessionRecord).filter_by(
                    session_id=session_id
                ).first()

                if not record:
                    raise KeyError(f"Session {session_id} not found")

                db_session.delete(record)
                db_session.commit()

                logger.debug(f"Deleted session: {session_id}")

            except Exception as e:
                db_session.rollback()
                logger.error(f"Failed to delete session: {e}")
                raise
            finally:
                db_session.close()

    def exists(self, session_id: str) -> bool:
        """
        세션 존재 여부 확인

        Args:
            session_id: 세션 ID

        Returns:
            True if session exists and not expired
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                record = db_session.query(SessionRecord).filter_by(
                    session_id=session_id
                ).first()

                if not record:
                    return False

                # 만료 확인
                if record.expires_at and datetime.utcnow() > record.expires_at:
                    return False

                return True

            except Exception as e:
                logger.error(f"Failed to check session existence: {e}")
                return False
            finally:
                db_session.close()

    def cleanup_expired(self) -> int:
        """
        만료된 세션 정리

        Returns:
            삭제된 세션 개수
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                now = datetime.utcnow()

                # 만료된 세션 조회
                expired_records = db_session.query(SessionRecord).filter(
                    SessionRecord.expires_at < now
                ).all()

                count = len(expired_records)

                # 삭제
                for record in expired_records:
                    db_session.delete(record)

                db_session.commit()

                if count > 0:
                    logger.info(f"Cleaned up {count} expired sessions")

                return count

            except Exception as e:
                db_session.rollback()
                logger.error(f"Failed to cleanup expired sessions: {e}")
                return 0
            finally:
                db_session.close()

    def get_all_active_sessions(self) -> List[str]:
        """
        모든 활성 세션 ID 조회

        Returns:
            활성 세션 ID 리스트
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                now = datetime.utcnow()

                records = db_session.query(SessionRecord).filter(
                    SessionRecord.expires_at >= now
                ).all()

                return [record.session_id for record in records]

            except Exception as e:
                logger.error(f"Failed to get active sessions: {e}")
                return []
            finally:
                db_session.close()

    def get_session_count(self) -> int:
        """
        활성 세션 개수

        Returns:
            활성 세션 개수
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                now = datetime.utcnow()

                count = db_session.query(SessionRecord).filter(
                    SessionRecord.expires_at >= now
                ).count()

                return count

            except Exception as e:
                logger.error(f"Failed to get session count: {e}")
                return 0
            finally:
                db_session.close()

    def clear_all(self) -> int:
        """
        모든 세션 삭제 (테스트/개발용)

        Returns:
            삭제된 세션 개수
        """
        with self._lock:
            db_session = self.SessionFactory()
            try:
                count = db_session.query(SessionRecord).delete()
                db_session.commit()

                logger.warning(f"Cleared all {count} sessions")
                return count

            except Exception as e:
                db_session.rollback()
                logger.error(f"Failed to clear all sessions: {e}")
                return 0
            finally:
                db_session.close()
