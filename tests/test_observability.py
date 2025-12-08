"""
Observability Tests - Phase C.4

모니터링, 메트릭, 헬스 체크를 검증합니다.
"""

import pytest
import time
from src.monitoring.observability_metrics import (
    MetricsRegistry,
    Counter,
    Gauge,
    Histogram,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ACTIVE_SESSIONS,
    CLAIM_VALIDATIONS,
    CLAIM_EVALUATION_LATENCY,
    SEARCH_QUERIES,
    ERROR_COUNT,
    track_request,
    track_claim_validation,
    track_claim_evaluation,
    track_search_query,
    update_active_sessions,
    get_metrics_text,
    MetricsSnapshot,
)

pytestmark = [
    pytest.mark.observability,
    pytest.mark.monitoring,
]


class TestMetricsRegistry:
    """메트릭 레지스트리 테스트"""

    def test_register_metric(self):
        """메트릭 등록"""
        registry = MetricsRegistry()
        counter = Counter("test_counter", "Test counter")

        registry.register(counter)

        retrieved = registry.get_metric("test_counter")
        assert retrieved is not None
        assert retrieved.name == "test_counter"

    def test_get_all_metrics(self):
        """모든 메트릭 조회"""
        registry = MetricsRegistry()
        counter = Counter("counter_1", "Counter 1")
        gauge = Gauge("gauge_1", "Gauge 1")

        registry.register(counter)
        registry.register(gauge)

        all_metrics = registry.get_all_metrics()
        assert len(all_metrics) == 2
        assert "counter_1" in all_metrics
        assert "gauge_1" in all_metrics


class TestCounterMetric:
    """카운터 메트릭 테스트"""

    def test_counter_increment(self):
        """카운터 증가"""
        counter = Counter("test", "Test counter")

        counter.inc()
        assert counter.get_value() == 1

        counter.inc(5)
        assert counter.get_value() == 6

    def test_counter_prometheus_format(self):
        """카운터 Prometheus 형식"""
        counter = Counter("test_counter", "Test counter metric")
        counter.inc(10)

        output = counter.to_prometheus_format()

        assert "test_counter" in output
        assert "10" in output
        assert "counter" in output


class TestGaugeMetric:
    """게이지 메트릭 테스트"""

    def test_gauge_set_get(self):
        """게이지 설정 및 조회"""
        gauge = Gauge("test", "Test gauge")

        gauge.set(42)
        assert gauge.get_value() == 42

        gauge.inc(8)
        assert gauge.get_value() == 50

        gauge.dec(10)
        assert gauge.get_value() == 40

    def test_gauge_prometheus_format(self):
        """게이지 Prometheus 형식"""
        gauge = Gauge("test_gauge", "Test gauge metric")
        gauge.set(25)

        output = gauge.to_prometheus_format()

        assert "test_gauge" in output
        assert "25" in output
        assert "gauge" in output


class TestHistogramMetric:
    """히스토그램 메트릭 테스트"""

    def test_histogram_observe(self):
        """히스토그램 관찰"""
        histogram = Histogram("latency", "Response latency")

        histogram.observe(0.001)
        histogram.observe(0.005)
        histogram.observe(0.01)
        histogram.observe(0.1)

        stats = histogram.get_stats()
        assert stats["count"] == 4
        assert stats["sum"] == pytest.approx(0.116, abs=0.001)

    def test_histogram_stats_calculation(self):
        """히스토그램 통계 계산"""
        histogram = Histogram("latency", "Latency")

        for i in range(1, 11):
            histogram.observe(float(i) / 1000)  # 0.001 to 0.01

        stats = histogram.get_stats()

        assert stats["count"] == 10
        assert stats["sum"] == pytest.approx(0.055, abs=0.001)
        assert stats["mean"] == pytest.approx(0.0055, abs=0.0001)

    def test_histogram_prometheus_format(self):
        """히스토그램 Prometheus 형식"""
        histogram = Histogram("test_histogram", "Test histogram")
        histogram.observe(0.001)
        histogram.observe(0.1)

        output = histogram.to_prometheus_format()

        assert "test_histogram" in output
        assert "histogram" in output
        assert "_bucket" in output
        assert "_sum" in output
        assert "_count" in output


class TestGlobalMetrics:
    """글로벌 메트릭 테스트"""

    def test_request_count_tracking(self):
        """요청 수 추적"""
        initial = REQUEST_COUNT.get_value()

        track_request(method="GET", endpoint="/test", status_code=200, duration=0.1)

        assert REQUEST_COUNT.get_value() == initial + 1

    def test_request_latency_tracking(self):
        """요청 레이턴시 추적"""
        REQUEST_LATENCY.observe(0.05)
        REQUEST_LATENCY.observe(0.1)
        REQUEST_LATENCY.observe(0.15)

        stats = REQUEST_LATENCY.get_stats()
        assert stats["count"] >= 3

    def test_active_sessions_tracking(self):
        """활성 세션 추적"""
        update_active_sessions(5)
        assert ACTIVE_SESSIONS.get_value() == 5

        update_active_sessions(10)
        assert ACTIVE_SESSIONS.get_value() == 10

        update_active_sessions(0)
        assert ACTIVE_SESSIONS.get_value() == 0

    def test_claim_validation_tracking(self):
        """청구항 검증 추적"""
        initial = CLAIM_VALIDATIONS.get_value()

        track_claim_validation()
        track_claim_validation()

        assert CLAIM_VALIDATIONS.get_value() == initial + 2

    def test_claim_evaluation_latency_tracking(self):
        """청구항 평가 레이턴시 추적"""
        CLAIM_EVALUATION_LATENCY.observe(0.5)
        CLAIM_EVALUATION_LATENCY.observe(0.8)

        stats = CLAIM_EVALUATION_LATENCY.get_stats()
        assert stats["count"] >= 2

    def test_search_query_tracking(self):
        """검색 쿼리 추적"""
        initial = SEARCH_QUERIES.get_value()

        track_search_query()
        track_search_query()
        track_search_query()

        assert SEARCH_QUERIES.get_value() == initial + 3

    def test_error_count_tracking(self):
        """에러 수 추적"""
        initial = ERROR_COUNT.get_value()

        # track_request에서 400+ 상태 코드일 때 에러 카운트 증가
        track_request(method="POST", endpoint="/test", status_code=400, duration=0.1)
        track_request(method="POST", endpoint="/test", status_code=500, duration=0.2)

        assert ERROR_COUNT.get_value() == initial + 2


class TestMetricsSnapshot:
    """메트릭 스냅샷 테스트"""

    def test_snapshot_creation(self):
        """스냅샷 생성"""
        snapshot = MetricsSnapshot()

        assert snapshot.timestamp is not None
        assert isinstance(snapshot.request_count, (int, float))
        assert isinstance(snapshot.active_sessions, (int, float))

    def test_snapshot_to_dict(self):
        """스냅샷 딕셔너리 변환"""
        snapshot = MetricsSnapshot()
        data = snapshot.to_dict()

        assert "timestamp" in data
        assert "request_count" in data
        assert "active_sessions" in data
        assert "error_count" in data


class TestMetricsOutput:
    """메트릭 출력 테스트"""

    def test_prometheus_output_format(self):
        """Prometheus 형식 출력"""
        output = get_metrics_text()

        assert isinstance(output, str)
        assert len(output) > 0
        # HELP와 TYPE이 포함되어야 함
        assert "HELP" in output or "counter" in output or "gauge" in output

    def test_prometheus_output_includes_metrics(self):
        """출력에 주요 메트릭 포함"""
        output = get_metrics_text()

        # 주요 메트릭들이 포함되어야 함
        assert "api_requests_total" in output
        assert "api_request_duration_seconds" in output
        assert "game_sessions_active" in output


class TestMetricsThreadSafety:
    """메트릭 스레드 안전성 테스트"""

    def test_concurrent_metric_updates(self):
        """동시 메트릭 업데이트"""
        import threading

        counter = Counter("concurrent_test", "Test")
        errors = []

        def increment_counter():
            try:
                for _ in range(100):
                    counter.inc()
            except Exception as e:
                errors.append(str(e))

        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment_counter)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0
        assert counter.get_value() == 1000

    def test_concurrent_gauge_updates(self):
        """동시 게이지 업데이트"""
        import threading

        gauge = Gauge("concurrent_gauge", "Test")
        gauge.set(0)
        errors = []

        def increment_gauge():
            try:
                for _ in range(50):
                    gauge.inc()
            except Exception as e:
                errors.append(str(e))

        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment_gauge)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0
        # 10 * 50 = 500
        assert gauge.get_value() == 500


class TestHealthCheckMetrics:
    """헬스 체크 관련 메트릭"""

    def test_health_check_latency(self):
        """헬스 체크 레이턴시"""
        histogram = Histogram("health_check_duration", "Health check duration")

        # 빠른 헬스 체크 시뮬레이션
        for _ in range(5):
            histogram.observe(0.001)  # 1ms

        stats = histogram.get_stats()
        assert stats["mean"] < 0.01  # 평균 10ms 이내

    def test_health_check_failures(self):
        """헬스 체크 실패"""
        health_check_errors = Counter("health_check_errors", "Health check failures")

        # 에러 발생 없음 - 카운트 0
        assert health_check_errors.get_value() == 0
