"""
Advanced Stress & Reliability Tests - Phase C.3

고급 스트레스 테스트와 안정성 테스트를 수행합니다.
메모리 누수, 동시성 문제, 리소스 고갈 등을 검증합니다.
"""

import pytest
import threading
import gc
import tracemalloc
import time
from src.storage.session_store import InMemorySessionStore
from src.utils.exceptions import SessionNotFoundException


pytestmark = [
    pytest.mark.stress,
    pytest.mark.reliability,
]


class TestMemoryLeaks:
    """메모리 누수 감지"""

    def test_session_create_delete_memory_stable(self):
        """세션 생성/삭제 후 메모리 안정"""
        store = InMemorySessionStore()

        # 초기 메모리 측정
        gc.collect()
        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]

        # 100개 세션 생성/삭제
        for i in range(100):
            session_id = f"test_session_{i}"
            store.create(session_id, {
                "player_name": f"player_{i}",
                "data": "x" * 100,  # 더 큰 데이터
            })
            store.delete(session_id)

        # 최종 메모리 측정
        gc.collect()
        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # 메모리 증가 확인 (10MB 이내)
        memory_increase = final_memory - initial_memory
        assert memory_increase < 10 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"

    def test_large_session_data_cleanup(self):
        """대량 데이터 세션 정리"""
        store = InMemorySessionStore()

        # 큰 데이터를 가진 세션 생성
        large_data = {
            "claims": ["x" * 1000 for _ in range(100)],
            "scores": list(range(1000)),
            "metadata": {"key": "value" * 500},
        }

        for i in range(10):
            store.create(f"large_session_{i}", large_data.copy())

        # 모든 세션 삭제
        for i in range(10):
            store.delete(f"large_session_{i}")

        # 저장소는 비어있어야 함
        assert store.count() == 0


class TestConcurrentStress:
    """동시성 스트레스 테스트"""

    def test_50_concurrent_session_creations(self):
        """50개 스레드에서 동시 세션 생성"""
        store = InMemorySessionStore()
        session_ids = []
        errors = []
        lock = threading.Lock()

        def create_session(thread_id):
            try:
                session_id = f"concurrent_{thread_id}_{int(time.time() * 1000)}"
                store.create(session_id, {"thread_id": thread_id})
                with lock:
                    session_ids.append(session_id)
            except Exception as e:
                with lock:
                    errors.append((thread_id, str(e)))

        # 50개 스레드 생성
        threads = []
        for i in range(50):
            t = threading.Thread(target=create_session, args=(i,))
            threads.append(t)
            t.start()

        # 모든 스레드 대기
        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0, f"Errors: {errors}"
        assert len(session_ids) == 50
        assert store.count() == 50

    def test_concurrent_read_write_mixed(self):
        """읽기/쓰기 혼합 동시 접근"""
        store = InMemorySessionStore()

        # 기본 세션 10개 생성
        for i in range(10):
            store.create(f"session_{i}", {"counter": 0})

        results = {"errors": 0, "reads": 0, "writes": 0}
        lock = threading.Lock()

        def reader_thread(thread_id):
            try:
                for _ in range(20):
                    session = store.get(f"session_{thread_id % 10}")
                    if session:
                        with lock:
                            results["reads"] += 1
            except Exception as e:
                with lock:
                    results["errors"] += 1

        def writer_thread(thread_id):
            try:
                for i in range(20):
                    session_id = f"session_{thread_id % 10}"
                    session = store.get(session_id)
                    if session:
                        counter = session.get("counter", 0) + 1
                        store.update(session_id, {"counter": counter})
                        with lock:
                            results["writes"] += 1
            except Exception as e:
                with lock:
                    results["errors"] += 1

        # 10개 reader, 10개 writer 스레드
        threads = []
        for i in range(10):
            t1 = threading.Thread(target=reader_thread, args=(i,))
            t2 = threading.Thread(target=writer_thread, args=(i,))
            threads.extend([t1, t2])
            t1.start()
            t2.start()

        # 모든 스레드 대기
        for t in threads:
            t.join()

        # 검증
        assert results["errors"] == 0, f"Errors: {results['errors']}"
        assert results["reads"] > 0
        assert results["writes"] > 0

    def test_high_contention_single_session(self):
        """단일 세션 고경합(High Contention)"""
        store = InMemorySessionStore()
        store.create("contested_session", {"value": 0})

        errors = []
        lock = threading.Lock()

        def update_session():
            try:
                for _ in range(50):
                    session = store.get("contested_session")
                    if session:
                        value = session.get("value", 0)
                        store.update("contested_session", {"value": value + 1})
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # 20개 스레드가 같은 세션 업데이트
        threads = []
        for _ in range(20):
            t = threading.Thread(target=update_session)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0, f"Errors: {errors}"


class TestResourceExhaustion:
    """리소스 고갈 테스트"""

    def test_1000_sessions_memory_bounded(self):
        """1000개 세션 생성 시 메모리 경계"""
        store = InMemorySessionStore()

        gc.collect()
        tracemalloc.start()
        initial = tracemalloc.get_traced_memory()[0]

        # 1000개 세션 생성
        for i in range(1000):
            store.create(
                f"session_{i:04d}",
                {
                    "player_id": i,
                    "claims": [f"claim_{j}" for j in range(5)],
                    "score": i * 10,
                }
            )

        gc.collect()
        final = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # 메모리 증가 (500MB 이내)
        increase = final - initial
        assert increase < 500 * 1024 * 1024, f"Memory: {increase / 1024 / 1024:.2f}MB"

        # 세션 수 확인
        assert store.count() == 1000

    def test_system_stable_with_500_active_sessions(self):
        """500개 활성 세션 유지 안정성"""
        store = InMemorySessionStore()

        # 500개 세션 생성
        for i in range(500):
            store.create(f"active_{i}", {"id": i, "active": True})

        # 랜덤 세션 접근
        for _ in range(1000):
            import random
            session_id = f"active_{random.randint(0, 499)}"
            session = store.get(session_id)
            assert session is not None

        # 최종 상태 확인
        assert store.count() == 500

    def test_many_concurrent_creates_limits(self):
        """많은 동시 생성의 한계 테스트"""
        store = InMemorySessionStore()
        created_ids = []
        errors = []
        lock = threading.Lock()

        def create_many(thread_id):
            try:
                for i in range(100):
                    session_id = f"t{thread_id}_s{i}_{int(time.time() * 1000)}"
                    store.create(session_id, {"thread": thread_id, "seq": i})
                    with lock:
                        created_ids.append(session_id)
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # 10개 스레드에서 각각 100개 세션 생성 (총 1000개)
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_many, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 검증
        assert len(errors) == 0
        assert len(created_ids) == 1000
        assert store.count() == 1000


class TestRaceConditionDetection:
    """경합 상태 감지"""

    def test_concurrent_create_same_id_prevention(self):
        """동시 동일 ID 생성 방지"""
        store = InMemorySessionStore()
        test_id = "race_test_session"
        errors = []
        success_count = [0]
        lock = threading.Lock()

        def try_create():
            try:
                store.create(test_id, {"data": "test"})
                with lock:
                    success_count[0] += 1
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # 10개 스레드가 동일 ID로 동시 생성
        threads = []
        for _ in range(10):
            t = threading.Thread(target=try_create)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 정확히 1개만 성공해야 함
        assert success_count[0] == 1, f"Expected 1 success, got {success_count[0]}"
        assert store.count() == 1

    def test_read_after_write_consistency(self):
        """쓰기 후 읽기 일관성"""
        store = InMemorySessionStore()
        session_id = "consistency_test"

        results = {"errors": 0}
        lock = threading.Lock()

        # 기본 데이터로 세션 생성
        store.create(session_id, {"value": 0, "history": []})

        def reader_writer_pair(pair_id):
            try:
                for _ in range(50):
                    # 읽기
                    session = store.get(session_id)
                    old_value = session.get("value", 0)

                    # 쓰기
                    new_value = old_value + 1
                    history = session.get("history", [])
                    history.append(pair_id)

                    store.update(session_id, {
                        "value": new_value,
                        "history": history
                    })
            except Exception as e:
                with lock:
                    results["errors"] += 1

        # 10개 pair 생성 (10개 스레드)
        threads = []
        for i in range(10):
            t = threading.Thread(target=reader_writer_pair, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 최종 상태 확인
        assert results["errors"] == 0
        final = store.get(session_id)
        # 10개 스레드 * 50회 = 최대 500개 업데이트 시도
        # value는 1-500 사이의 값 (race condition으로 인해 모두 적용되지 않을 수 있음)
        assert final["value"] > 0 and final["value"] <= 500


class TestSystemResilience:
    """시스템 복원력"""

    def test_recovery_after_multiple_errors(self):
        """여러 에러 후 복구"""
        store = InMemorySessionStore()

        # 정상 세션 생성
        store.create("good_session", {"data": "test"})

        # 에러 발생 시도
        error_count = 0
        try:
            store.create("good_session", {"data": "duplicate"})  # 에러
        except Exception:
            error_count += 1

        try:
            store.delete("nonexistent")  # 에러
        except Exception:
            error_count += 1

        try:
            store.update("nonexistent", {"data": "test"})  # 에러
        except Exception:
            error_count += 1

        # 에러 발생 확인
        assert error_count == 3

        # 시스템 여전히 작동
        store.create("another_session", {"data": "after_errors"})
        assert store.count() == 2

        # 정상 세션 여전히 존재
        session = store.get("good_session")
        assert session is not None
        assert session["data"] == "test"

    def test_partial_failure_isolation(self):
        """부분 실패 격리"""
        store = InMemorySessionStore()

        # 10개 세션 생성
        for i in range(10):
            store.create(f"session_{i}", {"id": i})

        # 일부 세션 업데이트 시도 (일부 실패)
        success = 0
        for i in range(15):
            try:
                session_id = f"session_{i}"
                session = store.get(session_id)
                if session:
                    store.update(session_id, {"modified": True})
                    success += 1
            except Exception:
                pass

        # 일부만 성공해야 함 (0-9는 성공, 10-14는 없음)
        assert success == 10

        # 다른 세션들은 영향 없음
        for i in range(10):
            session = store.get(f"session_{i}")
            assert session is not None
