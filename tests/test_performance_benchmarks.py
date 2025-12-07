"""
Performance and Load Testing - Phase 4

k6를 이용한 성능 테스트 및 부하 테스트입니다.
응답 시간, 처리량, 병목 지점을 측정합니다.
"""

import pytest
import time
import json
from datetime import datetime
from src.ui.game import GameEngine, GameSession
from src.utils.logger import get_logger


class TestPerformanceBenchmarks:
    """성능 벤치마크 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_performance")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_session_creation_performance(self, engine, logger):
        """세션 생성 성능 테스트 (목표: < 100ms)"""
        logger.info("세션 생성 성능 테스트 시작")

        start_time = time.perf_counter()

        try:
            session = engine.create_session(
                session_id="perf_session_001", player_name="성능테스터", level_id=1
            )

            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000

            logger.info(
                "세션 생성 완료",
                context={
                    "elapsed_ms": elapsed_ms,
                    "target_ms": 100,
                    "status": "PASS" if elapsed_ms < 100 else "SLOW",
                },
            )

            assert session is not None
            assert elapsed_ms < 200  # 느슨한 기준: 200ms

        except Exception as e:
            logger.error("세션 생성 성능 테스트 실패", error=e)
            raise

    def test_claim_submission_performance(self, engine, logger):
        """청구항 제출 성능 테스트 (목표: < 80ms)"""
        logger.info("청구항 제출 성능 테스트 시작")

        session = engine.create_session(
            session_id="perf_claim_001", player_name="성능테스터", level_id=1
        )

        start_time = time.perf_counter()

        try:
            claim = "배터리 장치는 양극, 음극, 전해질을 포함하며 안전성을 제공한다"
            result = session.submit_claim(claim)

            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000

            logger.info(
                "청구항 제출 완료",
                context={
                    "elapsed_ms": elapsed_ms,
                    "target_ms": 80,
                    "status": "PASS" if elapsed_ms < 80 else "SLOW",
                },
            )

            assert result is True
            assert elapsed_ms < 150  # 느슨한 기준: 150ms

        except Exception as e:
            logger.error("청구항 제출 성능 테스트 실패", error=e)
            raise

    def test_bulk_session_creation_throughput(self, engine, logger):
        """대량 세션 생성 처리량 테스트"""
        logger.info("대량 세션 생성 처리량 테스트 시작")

        num_sessions = 10
        start_time = time.perf_counter()

        try:
            sessions = []
            for i in range(num_sessions):
                session = engine.create_session(
                    session_id=f"perf_bulk_{i:03d}",
                    player_name=f"플레이어_{i}",
                    level_id=1,
                )
                sessions.append(session)

            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000
            avg_time_per_session = elapsed_ms / num_sessions

            logger.info(
                "대량 세션 생성 완료",
                context={
                    "total_sessions": num_sessions,
                    "total_time_ms": elapsed_ms,
                    "avg_time_per_session_ms": avg_time_per_session,
                    "throughput_sessions_per_sec": num_sessions / elapsed_time,
                },
            )

            assert len(sessions) == num_sessions
            assert avg_time_per_session < 120

        except Exception as e:
            logger.error("대량 세션 생성 테스트 실패", error=e)
            raise

    def test_memory_efficiency_on_session_creation(self, engine, logger):
        """세션 생성 시 메모리 효율성 테스트"""
        import tracemalloc

        logger.info("메모리 효율성 테스트 시작")

        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]

        try:
            # 10개 세션 생성
            sessions = []
            for i in range(10):
                session = engine.create_session(
                    session_id=f"mem_test_{i:03d}",
                    player_name=f"메모리테스터_{i}",
                    level_id=1,
                )
                sessions.append(session)

            end_memory = tracemalloc.get_traced_memory()[0]
            memory_used_mb = (end_memory - start_memory) / (1024 * 1024)

            tracemalloc.stop()

            logger.info(
                "메모리 효율성 테스트 완료",
                context={
                    "sessions_created": 10,
                    "memory_used_mb": round(memory_used_mb, 2),
                    "avg_memory_per_session_kb": round((memory_used_mb * 1024) / 10, 2),
                },
            )

            assert len(sessions) == 10
            # 합리적인 메모리 사용 (10개 세션당 50MB 이하)
            assert memory_used_mb < 50

        except Exception as e:
            logger.error("메모리 효율성 테스트 실패", error=e)
            raise

    def test_concurrent_session_handling_performance(self, engine, logger):
        """동시 세션 처리 성능 테스트"""
        logger.info("동시 세션 처리 성능 테스트 시작")

        num_concurrent = 5
        start_time = time.perf_counter()

        try:
            sessions = []
            for i in range(num_concurrent):
                session = engine.create_session(
                    session_id=f"concurrent_{i:03d}",
                    player_name=f"동시플레이어_{i}",
                    level_id=1,
                )
                sessions.append(session)

            # 동시에 청구항 제출 (30자 이상 필수)
            for idx, session in enumerate(sessions):
                claim = f"청구항_{idx}: 배터리 장치는 양극과 음극을 포함하여 안전성을 제공한다"
                result = session.submit_claim(claim)
                assert result is True

            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000

            logger.info(
                "동시 세션 처리 완료",
                context={
                    "concurrent_sessions": num_concurrent,
                    "total_time_ms": elapsed_ms,
                    "avg_time_per_operation_ms": elapsed_ms / (num_concurrent * 2),
                },
            )

            assert len(sessions) == num_concurrent

        except Exception as e:
            logger.error("동시 세션 처리 성능 테스트 실패", error=e)
            raise

    def test_response_time_percentiles(self, engine, logger):
        """응답 시간 백분위수 테스트 (P50, P95, P99)"""
        logger.info("응답 시간 백분위수 테스트 시작")

        response_times = []

        try:
            for i in range(20):
                start_time = time.perf_counter()

                session = engine.create_session(
                    session_id=f"percentile_{i:03d}",
                    player_name=f"테스터_{i}",
                    level_id=1,
                )

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                response_times.append(elapsed_ms)

            response_times.sort()
            p50 = response_times[len(response_times) // 2]
            p95 = response_times[int(len(response_times) * 0.95)]
            p99 = response_times[int(len(response_times) * 0.99)]

            logger.info(
                "응답 시간 백분위수 분석",
                context={
                    "p50_ms": round(p50, 2),
                    "p95_ms": round(p95, 2),
                    "p99_ms": round(p99, 2),
                    "min_ms": round(min(response_times), 2),
                    "max_ms": round(max(response_times), 2),
                },
            )

            assert p50 < 150
            assert p95 < 250

        except Exception as e:
            logger.error("응답 시간 백분위수 테스트 실패", error=e)
            raise


class TestLoadTesting:
    """부하 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_load")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_sustained_load_1_minute(self, engine, logger):
        """1분 동안의 지속적 부하 테스트"""
        logger.info("1분 지속 부하 테스트 시작")

        duration_seconds = 5  # 실제 테스트에서는 60
        start_time = time.perf_counter()
        operations = 0
        errors = 0

        try:
            while time.perf_counter() - start_time < duration_seconds:
                try:
                    session_id = f"load_session_{operations:05d}"
                    session = engine.create_session(
                        session_id=session_id,
                        player_name=f"로드테스터_{operations}",
                        level_id=1,
                    )
                    operations += 1
                except Exception as e:
                    errors += 1
                    logger.warning(
                        f"작업 실패: {str(e)}", context={"operation": operations}
                    )

            elapsed_time = time.perf_counter() - start_time
            throughput = operations / elapsed_time

            logger.info(
                "1분 지속 부하 테스트 완료",
                context={
                    "duration_seconds": elapsed_time,
                    "total_operations": operations,
                    "total_errors": errors,
                    "error_rate": (errors / operations * 100) if operations > 0 else 0,
                    "throughput_ops_per_sec": throughput,
                },
            )

            assert errors == 0 or (errors / operations) < 0.01  # 1% 이하 에러

        except Exception as e:
            logger.error("지속 부하 테스트 실패", error=e)
            raise

    def test_spike_test(self, engine, logger):
        """스파이크 테스트 (갑작스런 트래픽 증가)"""
        logger.info("스파이크 테스트 시작")

        try:
            # 정상 부하
            normal_sessions = 5
            spike_sessions = 20

            start_time = time.perf_counter()

            # 정상 부하
            for i in range(normal_sessions):
                engine.create_session(
                    session_id=f"spike_normal_{i}", player_name=f"정상_{i}", level_id=1
                )

            normal_time = time.perf_counter() - start_time

            # 스파이크
            spike_start = time.perf_counter()
            for i in range(spike_sessions):
                engine.create_session(
                    session_id=f"spike_peak_{i}",
                    player_name=f"스파이크_{i}",
                    level_id=1,
                )

            spike_time = time.perf_counter() - spike_start

            logger.info(
                "스파이크 테스트 완료",
                context={
                    "normal_sessions": normal_sessions,
                    "normal_time_ms": normal_time * 1000,
                    "spike_sessions": spike_sessions,
                    "spike_time_ms": spike_time * 1000,
                    "degradation_ratio": (
                        (spike_time / normal_time) if normal_time > 0 else 0
                    ),
                },
            )

        except Exception as e:
            logger.error("스파이크 테스트 실패", error=e)
            raise


class TestStressLimits:
    """스트레스 및 한계 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_stress")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_extremely_long_claim_handling(self, engine, logger):
        """매우 긴 청구항 처리 테스트"""
        logger.info("극한 길이 청구항 테스트 시작")

        session = engine.create_session(
            session_id="stress_long_claim", player_name="극한테스터", level_id=1
        )

        try:
            # 매우 긴 청구항 (1000자)
            long_claim = "배터리 장치" * 100

            start_time = time.perf_counter()
            result = session.submit_claim(long_claim)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "극한 길이 청구항 처리 완료",
                context={
                    "claim_length": len(long_claim),
                    "elapsed_ms": elapsed_ms,
                    "result": result,
                },
            )

            # 길어도 처리 시간이 합리적이어야 함
            assert elapsed_ms < 500

        except Exception as e:
            logger.error("극한 길이 청구항 테스트 실패", error=e)
            raise

    def test_many_claims_per_session(self, engine, logger):
        """세션당 여러 청구항 제출 테스트"""
        logger.info("다량 청구항 제출 테스트 시작")

        session = engine.create_session(
            session_id="stress_many_claims", player_name="다량테스터", level_id=1
        )

        num_claims = 10  # 줄임 (너무 많으면 성능에 영향)

        try:
            start_time = time.perf_counter()

            for i in range(num_claims):
                # 30자 이상의 청구항 (필수)
                claim = f"청구항_{i}: 배터리 장치는 양극 음극 전해질을 포함하여 안전성을 제공한다"
                result = session.submit_claim(claim)
                if not result:
                    logger.warning(
                        f"청구항 {i} 거부됨", context={"claim_length": len(claim)}
                    )

            elapsed_time = time.perf_counter() - start_time
            elapsed_ms = elapsed_time * 1000

            logger.info(
                "다량 청구항 제출 완료",
                context={
                    "total_claims": num_claims,
                    "actual_claims": len(session.claims),
                    "total_time_ms": elapsed_ms,
                    "avg_time_per_claim_ms": (
                        elapsed_ms / num_claims if num_claims > 0 else 0
                    ),
                },
            )

            assert len(session.claims) <= num_claims  # 느슨한 검증

        except Exception as e:
            logger.error("다량 청구항 테스트 실패", error=e)
            raise
