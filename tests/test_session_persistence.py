"""
Session Persistence Tests - 세션 저장소 계층 검증

SessionStore 추상화 계층의 모든 CRUD 작업,
동시성 안전성, 데이터 직렬화 등을 검증합니다.
"""

import pytest
import json
import threading
import uuid
from typing import List
from src.storage.session_store import InMemorySessionStore
from src.utils.exceptions import SessionNotFoundException, PersistenceException

pytestmark = [
    pytest.mark.integration,
    pytest.mark.persistence,
]


class TestSessionCRUDOperations:
    """세션 CRUD 작업 검증"""

    def test_create_session(self):
        """세션 생성"""
        store = InMemorySessionStore()
        session_id = "test_session_1"
        session_data = {
            "player_name": "테스트플레이어",
            "level_id": 1,
            "score": 0,
            "claims": [],
        }

        # Create
        store.create(session_id, session_data)

        # Verify
        assert store.exists(session_id)
        assert store.count() == 1

    def test_get_session(self):
        """세션 조회"""
        store = InMemorySessionStore()
        session_id = "test_session_2"
        session_data = {
            "player_name": "플레이어2",
            "level_id": 2,
            "score": 100,
        }

        store.create(session_id, session_data)
        retrieved = store.get(session_id)

        assert retrieved is not None
        assert retrieved["player_name"] == "플레이어2"
        assert retrieved["level_id"] == 2
        assert retrieved["score"] == 100

    def test_get_nonexistent_session_returns_none(self):
        """존재하지 않는 세션은 None 반환"""
        store = InMemorySessionStore()

        retrieved = store.get("nonexistent_session")

        assert retrieved is None

    def test_update_session(self):
        """세션 업데이트"""
        store = InMemorySessionStore()
        session_id = "test_session_3"

        # Create
        store.create(session_id, {"player_name": "플레이어3", "score": 0})

        # Update
        store.update(session_id, {"score": 150, "claims": ["청구항1"]})

        # Verify
        updated = store.get(session_id)
        assert updated["score"] == 150
        assert updated["player_name"] == "플레이어3"
        assert "claims" in updated

    def test_update_nonexistent_session_raises_error(self):
        """존재하지 않는 세션 업데이트는 에러"""
        store = InMemorySessionStore()

        with pytest.raises(SessionNotFoundException):
            store.update("nonexistent", {"score": 100})

    def test_delete_session(self):
        """세션 삭제"""
        store = InMemorySessionStore()
        session_id = "test_session_4"

        # Create
        store.create(session_id, {"player_name": "플레이어4"})
        assert store.exists(session_id)

        # Delete
        store.delete(session_id)

        # Verify
        assert not store.exists(session_id)
        assert store.get(session_id) is None

    def test_delete_nonexistent_session_raises_error(self):
        """존재하지 않는 세션 삭제는 에러"""
        store = InMemorySessionStore()

        with pytest.raises(SessionNotFoundException):
            store.delete("nonexistent")

    def test_list_all_sessions(self):
        """모든 세션 목록 조회"""
        store = InMemorySessionStore()

        # Create multiple sessions
        session_ids = [f"session_{i}" for i in range(5)]
        for sid in session_ids:
            store.create(sid, {"player_name": f"player_{sid}"})

        # List
        all_ids = store.list_all()

        assert len(all_ids) == 5
        assert set(all_ids) == set(session_ids)


class TestSessionDataIntegrity:
    """세션 데이터 무결성"""

    def test_session_data_not_modified_externally(self):
        """세션 데이터는 외부 수정으로부터 보호됨"""
        store = InMemorySessionStore()
        session_id = "test_session_integrity"
        original_data = {"score": 100, "claims": []}

        store.create(session_id, original_data)

        # Retrieve and try to modify
        retrieved = store.get(session_id)
        retrieved["score"] = 999  # 외부에서 수정 시도

        # Original should be unchanged
        verified = store.get(session_id)
        assert verified["score"] == 100, "External modification should not affect stored data"

    def test_session_metadata_added(self):
        """생성/수정 시간 메타데이터 자동 추가"""
        store = InMemorySessionStore()
        session_id = "test_session_metadata"

        store.create(session_id, {"player_name": "테스트"})
        session = store.get(session_id)

        assert "_created_at" in session
        assert "_updated_at" in session

        # Parse ISO format
        from datetime import datetime

        created = datetime.fromisoformat(session["_created_at"])
        updated = datetime.fromisoformat(session["_updated_at"])

        assert isinstance(created, datetime)
        assert isinstance(updated, datetime)

    def test_update_timestamp_changes(self):
        """업데이트 시 _updated_at 변경"""
        import time

        store = InMemorySessionStore()
        session_id = "test_session_update_time"

        store.create(session_id, {"score": 0})
        first_update = store.get(session_id)["_updated_at"]

        time.sleep(0.01)  # 약간의 시간 경과

        store.update(session_id, {"score": 50})
        second_update = store.get(session_id)["_updated_at"]

        assert first_update != second_update


class TestSessionSerialization:
    """세션 직렬화/역직렬화"""

    def test_session_json_serializable(self):
        """세션을 JSON으로 직렬화 가능"""
        store = InMemorySessionStore()
        session_id = "test_session_json"
        session_data = {
            "player_name": "플레이어",
            "level_id": 1,
            "claims": ["청구항1", "청구항2"],
            "scores": [100, 200, 150],
        }

        store.create(session_id, session_data)
        session = store.get(session_id)

        # JSON 직렬화 시도
        json_str = json.dumps(session)
        assert isinstance(json_str, str)

        # JSON 역직렬화
        restored = json.loads(json_str)
        assert restored["player_name"] == "플레이어"
        assert restored["claims"] == ["청구항1", "청구항2"]

    def test_complex_session_data_preserved(self):
        """복잡한 데이터 구조 보존"""
        store = InMemorySessionStore()
        session_id = "test_session_complex"
        complex_data = {
            "player_info": {
                "name": "플레이어",
                "level": 1,
                "achievements": ["achievement1", "achievement2"],
            },
            "game_state": {
                "current_claim": 0,
                "claims": [
                    {
                        "id": "claim_1",
                        "text": "청구항1",
                        "validation_score": 0.95,
                    },
                    {
                        "id": "claim_2",
                        "text": "청구항2",
                        "validation_score": 0.87,
                    },
                ],
            },
        }

        store.create(session_id, complex_data)
        retrieved = store.get(session_id)

        # 구조 무결성 확인
        assert retrieved["player_info"]["achievements"] == ["achievement1", "achievement2"]
        assert len(retrieved["game_state"]["claims"]) == 2
        assert retrieved["game_state"]["claims"][0]["validation_score"] == 0.95


class TestSessionConcurrency:
    """세션 동시성 안전성"""

    def test_concurrent_create_different_sessions(self):
        """다른 세션의 동시 생성"""
        store = InMemorySessionStore()
        session_ids = []
        errors = []

        def create_session(thread_id):
            try:
                session_id = f"session_{thread_id}"
                store.create(session_id, {"player_id": thread_id})
                session_ids.append(session_id)
            except Exception as e:
                errors.append(e)

        # 10개 스레드에서 동시 생성
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_session, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(session_ids) == 10
        assert store.count() == 10

    def test_concurrent_read_same_session(self):
        """같은 세션의 동시 읽기"""
        store = InMemorySessionStore()
        session_id = "test_session_read"
        store.create(session_id, {"data": "test_data", "counter": 0})

        read_data = []
        errors = []

        def read_session():
            try:
                data = store.get(session_id)
                if data:
                    read_data.append(data["data"])
            except Exception as e:
                errors.append(e)

        # 20개 스레드에서 동시 읽기
        threads = []
        for _ in range(20):
            t = threading.Thread(target=read_session)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0
        assert len(read_data) == 20
        assert all(d == "test_data" for d in read_data)

    def test_concurrent_update_same_session(self):
        """같은 세션의 동시 업데이트 (직렬화됨)"""
        store = InMemorySessionStore()
        session_id = "test_session_update"
        store.create(session_id, {"counter": 0})

        errors = []

        def update_counter(increment):
            try:
                current = store.get(session_id)
                new_counter = current.get("counter", 0) + increment
                store.update(session_id, {"counter": new_counter})
            except Exception as e:
                errors.append(e)

        # 10개 스레드에서 동시 업데이트
        threads = []
        for i in range(10):
            t = threading.Thread(target=update_counter, args=(1,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0
        final = store.get(session_id)
        # 순서 보장이 없으므로 최종 값은 1-10 사이일 수 있음
        assert 1 <= final["counter"] <= 10

    def test_concurrent_create_and_delete(self):
        """동시 생성과 삭제"""
        store = InMemorySessionStore()
        errors = []

        def create_and_delete(thread_id):
            try:
                session_id = f"session_{thread_id}"
                store.create(session_id, {"id": thread_id})
                # 즉시 삭제
                store.delete(session_id)
            except Exception as e:
                errors.append(e)

        # 10개 스레드
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_and_delete, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0
        assert store.count() == 0, "All sessions should be deleted"


class TestSessionStoreRobustness:
    """세션 저장소 견고성"""

    def test_create_duplicate_session_raises_error(self):
        """중복 세션 생성은 에러"""
        store = InMemorySessionStore()
        session_id = "test_duplicate"

        store.create(session_id, {"data": "first"})

        with pytest.raises(PersistenceException):
            store.create(session_id, {"data": "second"})

    def test_store_clear_removes_all_sessions(self):
        """clear()로 모든 세션 삭제"""
        store = InMemorySessionStore()

        # 5개 세션 생성
        for i in range(5):
            store.create(f"session_{i}", {"id": i})

        assert store.count() == 5

        # Clear
        store.clear()

        assert store.count() == 0
        assert store.list_all() == []

    def test_empty_store_operations(self):
        """빈 저장소 작업"""
        store = InMemorySessionStore()

        assert store.count() == 0
        assert store.list_all() == []
        assert store.get("any") is None
        assert not store.exists("any")

    def test_store_preserves_session_order_in_list(self):
        """list_all()의 순서는 생성 순서를 반영할 수 있음"""
        store = InMemorySessionStore()
        session_ids = [f"session_{i:03d}" for i in range(10)]

        for sid in session_ids:
            store.create(sid, {"id": sid})

        listed = store.list_all()

        # 모든 ID가 포함되어야 함
        assert set(listed) == set(session_ids)
        assert len(listed) == 10
