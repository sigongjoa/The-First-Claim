"""
Observability Metrics - 모니터링 메트릭 수집

Prometheus 형식의 메트릭을 수집하고 추적합니다.
요청 수, 레이턴시, 활성 세션 등을 모니터링합니다.
"""

from typing import Dict, List
import threading
from datetime import datetime, timedelta


class MetricsRegistry:
    """메트릭 레지스트리"""

    def __init__(self):
        """메트릭 레지스트리 초기화"""
        self._metrics: Dict[str, "Metric"] = {}
        self._lock = threading.RLock()

    def register(self, metric: "Metric") -> None:
        """메트릭 등록

        Args:
            metric: 등록할 메트릭
        """
        with self._lock:
            self._metrics[metric.name] = metric

    def get_metric(self, name: str) -> "Metric":
        """메트릭 조회

        Args:
            name: 메트릭명

        Returns:
            메트릭 객체
        """
        with self._lock:
            return self._metrics.get(name)

    def get_all_metrics(self) -> Dict[str, "Metric"]:
        """모든 메트릭 조회

        Returns:
            모든 메트릭
        """
        with self._lock:
            return dict(self._metrics)

    def generate_prometheus_output(self) -> str:
        """Prometheus 형식으로 메트릭 생성

        Returns:
            Prometheus 형식의 메트릭 텍스트
        """
        lines = []

        with self._lock:
            for metric in self._metrics.values():
                lines.append(metric.to_prometheus_format())

        return "\n".join(lines)


class Metric:
    """메트릭 기본 클래스"""

    def __init__(self, name: str, description: str):
        """메트릭 초기화

        Args:
            name: 메트릭명
            description: 메트릭 설명
        """
        self.name = name
        self.description = description
        self._lock = threading.RLock()

    def to_prometheus_format(self) -> str:
        """Prometheus 형식으로 변환

        Returns:
            Prometheus 형식 문자열
        """
        raise NotImplementedError


class Counter(Metric):
    """카운터 메트릭 (증가만 가능)"""

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self._value = 0

    def inc(self, amount: float = 1) -> None:
        """카운터 증가

        Args:
            amount: 증가량
        """
        with self._lock:
            self._value += amount

    def get_value(self) -> float:
        """현재 값 조회

        Returns:
            카운터 값
        """
        with self._lock:
            return self._value

    def to_prometheus_format(self) -> str:
        """Prometheus 형식으로 변환"""
        return f"# HELP {self.name} {self.description}\n# TYPE {self.name} counter\n{self.name} {self.get_value()}"


class Gauge(Metric):
    """게이지 메트릭 (증가/감소 가능)"""

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self._value = 0

    def set(self, value: float) -> None:
        """값 설정

        Args:
            value: 설정할 값
        """
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1) -> None:
        """값 증가

        Args:
            amount: 증가량
        """
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1) -> None:
        """값 감소

        Args:
            amount: 감소량
        """
        with self._lock:
            self._value -= amount

    def get_value(self) -> float:
        """현재 값 조회

        Returns:
            게이지 값
        """
        with self._lock:
            return self._value

    def to_prometheus_format(self) -> str:
        """Prometheus 형식으로 변환"""
        return f"# HELP {self.name} {self.description}\n# TYPE {self.name} gauge\n{self.name} {self.get_value()}"


class Histogram(Metric):
    """히스토그램 메트릭 (분포 추적)"""

    def __init__(self, name: str, description: str, buckets: List[float] = None):
        super().__init__(name, description)
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._bucket_counts = {bucket: 0 for bucket in self.buckets}
        self._bucket_counts[float('inf')] = 0
        self._sum = 0
        self._count = 0

    def observe(self, value: float) -> None:
        """값 관찰

        Args:
            value: 관찰할 값
        """
        with self._lock:
            self._sum += value
            self._count += 1

            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1

            self._bucket_counts[float('inf')] += 1

    def get_stats(self) -> Dict:
        """통계 조회

        Returns:
            통계 정보
        """
        with self._lock:
            if self._count == 0:
                return {
                    "count": 0,
                    "sum": 0,
                    "mean": 0,
                    "buckets": dict(self._bucket_counts),
                }

            return {
                "count": self._count,
                "sum": self._sum,
                "mean": self._sum / self._count,
                "buckets": dict(self._bucket_counts),
            }

    def to_prometheus_format(self) -> str:
        """Prometheus 형식으로 변환"""
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} histogram",
        ]

        stats = self.get_stats()
        for bucket, count in stats["buckets"].items():
            bucket_str = "+Inf" if bucket == float('inf') else str(bucket)
            lines.append(f'{self.name}_bucket{{le="{bucket_str}"}} {count}')

        lines.append(f"{self.name}_sum {stats['sum']}")
        lines.append(f"{self.name}_count {stats['count']}")

        return "\n".join(lines)


# 글로벌 메트릭 레지스트리
_registry = MetricsRegistry()

# 주요 메트릭 정의
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total HTTP requests"
)
_registry.register(REQUEST_COUNT)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "HTTP request latency in seconds"
)
_registry.register(REQUEST_LATENCY)

ACTIVE_SESSIONS = Gauge(
    "game_sessions_active",
    "Number of active game sessions"
)
_registry.register(ACTIVE_SESSIONS)

CLAIM_VALIDATIONS = Counter(
    "claims_validated_total",
    "Total claim validations"
)
_registry.register(CLAIM_VALIDATIONS)

CLAIM_EVALUATION_LATENCY = Histogram(
    "claim_evaluation_duration_seconds",
    "Claim evaluation latency in seconds"
)
_registry.register(CLAIM_EVALUATION_LATENCY)

SEARCH_QUERIES = Counter(
    "search_queries_total",
    "Total search queries"
)
_registry.register(SEARCH_QUERIES)

ERROR_COUNT = Counter(
    "errors_total",
    "Total errors"
)
_registry.register(ERROR_COUNT)


def get_registry() -> MetricsRegistry:
    """글로벌 메트릭 레지스트리 조회

    Returns:
        MetricsRegistry 인스턴스
    """
    return _registry


def track_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """API 요청 추적

    Args:
        method: HTTP 메서드
        endpoint: 엔드포인트 경로
        status_code: HTTP 상태 코드
        duration: 요청 처리 시간 (초)
    """
    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(duration)

    if status_code >= 400:
        ERROR_COUNT.inc()


def track_claim_validation() -> None:
    """청구항 검증 추적"""
    CLAIM_VALIDATIONS.inc()


def track_claim_evaluation(duration: float) -> None:
    """청구항 평가 추적

    Args:
        duration: 평가 시간 (초)
    """
    CLAIM_EVALUATION_LATENCY.observe(duration)


def track_search_query() -> None:
    """검색 쿼리 추적"""
    SEARCH_QUERIES.inc()


def update_active_sessions(count: int) -> None:
    """활성 세션 수 업데이트

    Args:
        count: 활성 세션 수
    """
    ACTIVE_SESSIONS.set(count)


def get_metrics_text() -> str:
    """모든 메트릭을 Prometheus 형식으로 반환

    Returns:
        Prometheus 형식의 메트릭 텍스트
    """
    return _registry.generate_prometheus_output()


class MetricsSnapshot:
    """메트릭 스냅샷"""

    def __init__(self):
        """스냅샷 캡처"""
        self.timestamp = datetime.utcnow()
        self.request_count = REQUEST_COUNT.get_value()
        self.request_latency_stats = REQUEST_LATENCY.get_stats()
        self.active_sessions = ACTIVE_SESSIONS.get_value()
        self.claim_validations = CLAIM_VALIDATIONS.get_value()
        self.claim_evaluation_stats = CLAIM_EVALUATION_LATENCY.get_stats()
        self.search_queries = SEARCH_QUERIES.get_value()
        self.error_count = ERROR_COUNT.get_value()

    def to_dict(self) -> Dict:
        """딕셔너리로 변환

        Returns:
            메트릭 스냅샷을 딕셔너리로
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "request_count": self.request_count,
            "request_latency": self.request_latency_stats,
            "active_sessions": self.active_sessions,
            "claim_validations": self.claim_validations,
            "claim_evaluation": self.claim_evaluation_stats,
            "search_queries": self.search_queries,
            "error_count": self.error_count,
        }
