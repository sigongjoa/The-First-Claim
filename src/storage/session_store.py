"""
Session Storage Abstraction Layer

세션 저장소의 인터페이스와 메모리 기반 구현을 제공합니다.
추후 Redis, 데이터베이스 등의 저장소로 확장 가능합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import threading
import json
from datetime import datetime


class SessionStore(ABC):
    """세션 저장소 추상 인터페이스"""

    @abstractmethod
    def create(self, session_id: str, data: dict) -> None:
        """새로운 세션 생성

        Args:
            session_id: 세션 고유 ID
            data: 세션 데이터

        Raises:
            PersistenceException: 저장 실패 시
        """
        pass

    @abstractmethod
    def get(self, session_id: str) -> Optional[dict]:
        """세션 데이터 조회

        Args:
            session_id: 세션 고유 ID

        Returns:
            세션 데이터, 없으면 None

        Raises:
            PersistenceException: 조회 실패 시
        """
        pass

    @abstractmethod
    def update(self, session_id: str, data: dict) -> None:
        """세션 데이터 업데이트

        Args:
            session_id: 세션 고유 ID
            data: 업데이트할 데이터

        Raises:
            PersistenceException: 업데이트 실패 또는 세션 없음
        """
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        """세션 삭제

        Args:
            session_id: 세션 고유 ID

        Raises:
            PersistenceException: 삭제 실패 시
        """
        pass

    @abstractmethod
    def list_all(self) -> List[str]:
        """모든 세션 ID 목록 반환

        Returns:
            세션 ID 리스트

        Raises:
            PersistenceException: 조회 실패 시
        """
        pass

    @abstractmethod
    def exists(self, session_id: str) -> bool:
        """세션 존재 여부 확인

        Args:
            session_id: 세션 고유 ID

        Returns:
            존재하면 True
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """전체 세션 개수

        Returns:
            세션 개수
        """
        pass


class InMemorySessionStore(SessionStore):
    """메모리 기반 세션 저장소 (스레드 안전)"""

    def __init__(self):
        """메모리 저장소 초기화"""
        self._sessions: Dict[str, dict] = {}
        self._lock = threading.RLock()

    def create(self, session_id: str, data: dict) -> None:
        """새로운 세션 생성"""
        from src.utils.exceptions import PersistenceException

        with self._lock:
            if session_id in self._sessions:
                raise PersistenceException(
                    f"Session already exists: {session_id}",
                    operation="create",
                )
            try:
                # 메타데이터 추가
                session_data = {
                    **data,
                    "_created_at": datetime.utcnow().isoformat(),
                    "_updated_at": datetime.utcnow().isoformat(),
                }
                self._sessions[session_id] = session_data
            except Exception as e:
                raise PersistenceException(
                    f"Failed to create session: {str(e)}", operation="create"
                )

    def get(self, session_id: str) -> Optional[dict]:
        """세션 데이터 조회"""
        with self._lock:
            if session_id not in self._sessions:
                return None
            # 딕셔너리 복사본 반환 (외부 수정 방지)
            return dict(self._sessions[session_id])

    def update(self, session_id: str, data: dict) -> None:
        """세션 데이터 업데이트"""
        from src.utils.exceptions import SessionNotFoundException, PersistenceException

        with self._lock:
            if session_id not in self._sessions:
                raise SessionNotFoundException(session_id)
            try:
                self._sessions[session_id].update(data)
                self._sessions[session_id]["_updated_at"] = datetime.utcnow().isoformat()
            except Exception as e:
                raise PersistenceException(
                    f"Failed to update session: {str(e)}", operation="update"
                )

    def delete(self, session_id: str) -> None:
        """세션 삭제"""
        from src.utils.exceptions import SessionNotFoundException, PersistenceException

        with self._lock:
            if session_id not in self._sessions:
                raise SessionNotFoundException(session_id)
            try:
                del self._sessions[session_id]
            except Exception as e:
                raise PersistenceException(
                    f"Failed to delete session: {str(e)}", operation="delete"
                )

    def list_all(self) -> List[str]:
        """모든 세션 ID 목록 반환"""
        with self._lock:
            return list(self._sessions.keys())

    def exists(self, session_id: str) -> bool:
        """세션 존재 여부 확인"""
        with self._lock:
            return session_id in self._sessions

    def count(self) -> int:
        """전체 세션 개수"""
        with self._lock:
            return len(self._sessions)

    def get_all_sessions(self) -> Dict[str, dict]:
        """모든 세션 데이터 반환 (테스트/디버깅용)

        Returns:
            {session_id: session_data} 딕셔너리
        """
        with self._lock:
            return {sid: dict(data) for sid, data in self._sessions.items()}

    def clear(self) -> None:
        """모든 세션 삭제 (테스트용)"""
        with self._lock:
            self._sessions.clear()
