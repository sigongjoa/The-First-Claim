# 평가 엔진 설정 가이드

## 개요

PROJECT: OVERRIDE의 평가 엔진은 완전히 설정 가능합니다. 모든 임계값, 가중치, 매개변수는 환경 변수 또는 프로그래매틱 설정을 통해 조정할 수 있습니다.

---

## 1. 신규성 평가 설정

### 매개변수 목록

| 매개변수 | 타입 | 기본값 | 범위 | 설명 |
|---------|------|-------|------|------|
| `EVAL_NOVELTY_THRESHOLD` | float | 0.7 | 0.0-1.0 | Jaccard 유사도 임계값 |
| `EVAL_RAG_TOP_K` | int | 5 | 1-20 | 벡터 검색 결과 개수 |
| `EVAL_RAG_SIMILARITY_THRESHOLD` | float | 0.6 | 0.0-1.0 | 코사인 유사도 최소값 |
| `EVAL_NOVELTY_USE_LLM` | bool | true | - | LLM 판단 활성화 |
| `EVAL_NOVELTY_VECTOR_WEIGHT` | float | 0.6 | 0.0-1.0 | 벡터 유사도 가중치 |
| `EVAL_NOVELTY_LLM_WEIGHT` | float | 0.4 | 0.0-1.0 | LLM 판단 가중치 |

### 프로파일별 추천 설정

#### 1. 엄격한 평가 (높은 신규성 요구)

```bash
# .env 또는 환경 변수
EVAL_NOVELTY_THRESHOLD=0.8      # 높은 유사도만 거절
EVAL_RAG_TOP_K=10               # 더 많은 선행기술 검색
EVAL_RAG_SIMILARITY_THRESHOLD=0.7
EVAL_NOVELTY_LLM_WEIGHT=0.6     # LLM 판단 강조 (60%)
```

**효과**: 더 엄격한 신규성 판정, 거절률 증가

#### 2. 균형잡힌 평가 (기본)

```bash
EVAL_NOVELTY_THRESHOLD=0.7      # 기본값
EVAL_RAG_TOP_K=5                # 기본값
EVAL_RAG_SIMILARITY_THRESHOLD=0.6
EVAL_NOVELTY_LLM_WEIGHT=0.4     # 규칙 기반 강조
```

**효과**: 규칙 기반과 LLM의 균형

#### 3. 관대한 평가 (높은 인정률)

```bash
EVAL_NOVELTY_THRESHOLD=0.6      # 낮은 유사도만 거절
EVAL_RAG_TOP_K=3                # 상위 유사 항목만
EVAL_RAG_SIMILARITY_THRESHOLD=0.5
EVAL_NOVELTY_LLM_WEIGHT=0.2     # 규칙 기반 의존
```

**효과**: 더 관대한 신규성 판정, 인정률 증가

### 프로그래매틱 설정

```python
from src.config.evaluation_config import NoveltyConfig, EvaluationConfig

# 기본 설정
default_config = EvaluationConfig()
print(default_config.novelty.min_similarity_threshold)  # 0.7

# 커스텀 설정
strict_config = EvaluationConfig(
    novelty=NoveltyConfig(
        min_similarity_threshold=0.8,
        vector_search_top_k=10,
        llm_judgment_weight=0.6,
    )
)

# 환경 변수로 오버라이드
import os
os.environ["EVAL_NOVELTY_THRESHOLD"] = "0.75"
custom_config = get_evaluation_config()
```

---

## 2. 진보성 평가 설정

### 매개변수 목록

| 매개변수 | 타입 | 기본값 | 설명 |
|---------|------|-------|------|
| `EVAL_TECHNICAL_FIELD` | str | "전자" | 기술 분야 |
| `EVAL_COMPLEXITY_FACTOR` | float | 0.8 | 분야별 복잡도 (0.0-1.0) |
| `EVAL_MIN_FEATURE_COUNT` | int | 10 | 최소 특징 개수 |
| `EVAL_FEATURE_WEIGHT` | float | 0.3 | 특징 개수 가중치 |
| `EVAL_INVENTIVE_USE_PRECEDENT` | bool | true | 판례 검색 활성화 |
| `EVAL_PRECEDENT_TOP_K` | int | 5 | 판례 검색 결과 개수 |
| `EVAL_INVENTIVE_USE_LLM` | bool | true | LLM 판단 활성화 |
| `EVAL_INVENTIVE_LLM_WEIGHT` | float | 0.6 | LLM 판단 가중치 |

### 기술 분야별 설정

#### 전자 (Electronics)

```python
technical_complexity = {
    "전자": 0.8,  # 높은 복잡도
}
feature_weight = 0.3
llm_judgment_weight = 0.6
```

**이유**: 전자 기술은 빠르게 진화하며 예측 불가능한 효과가 많음

#### 기계 (Mechanical)

```python
technical_complexity = {
    "기계": 0.7,  # 중간-높음 복잡도
}
feature_weight = 0.35
llm_judgment_weight = 0.5
```

**이유**: 기계 기술은 상대적으로 예측 가능한 영역

#### 화학 (Chemical)

```python
technical_complexity = {
    "화학": 0.9,  # 매우 높은 복잡도
}
feature_weight = 0.25
llm_judgment_weight = 0.7
```

**이유**: 화학은 매우 예측 불가능한 기술 효과 가능

#### 소프트웨어 (Software)

```python
technical_complexity = {
    "소프트웨어": 0.6,  # 중간 복잡도
}
feature_weight = 0.4
llm_judgment_weight = 0.4
```

**이유**: 소프트웨어는 규칙과 논리에 기반함

### 프로그래매틱 설정

```python
from src.config.evaluation_config import InventiveStepConfig, EvaluationConfig

# 화학 분야 설정
chemical_config = EvaluationConfig(
    inventive_step=InventiveStepConfig(
        technical_complexity={
            "화학": 0.9,
            "생물": 0.9,
            "바이오": 0.9,
        },
        min_feature_count=8,
        feature_weight=0.25,
        use_llm_judgment=True,
        llm_judgment_weight=0.7,
    )
)

# 사용
evaluator = HybridInventiveStepEvaluator(rag_system=rag)
result = await evaluator.evaluate_inventive_step(
    claim_text=claim,
    technical_field="화학"
)
```

---

## 3. RAG 시스템 설정

### 벡터 검색 최적화

```bash
# 좁은 검색 (정확도 중시)
EVAL_RAG_TOP_K=3
EVAL_RAG_SIMILARITY_THRESHOLD=0.75  # 높은 임계값

# 넓은 검색 (완전성 중시)
EVAL_RAG_TOP_K=10
EVAL_RAG_SIMILARITY_THRESHOLD=0.5   # 낮은 임계값
```

### 임베딩 모델 선택

```python
# 현재: nomic-embed-text (768차원, 권장)
ollama.embed(
    model="nomic-embed-text",
    input=query
)

# 향후 대안:
# - "all-minilm:latest" (384차원, 빠름)
# - "all-mpnet-base-v2" (768차원, 높은 정확도)
```

### 벡터 DB 캐싱

```python
# ChromaDB 캐시 설정
from chromadb.config import Settings

settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="data/vector_db",
    anonymized_telemetry=False,
    # 캐시 최적화
    allow_reset=True,
    is_persistent=True,
)
```

---

## 4. LLM 설정

### Ollama 연결 설정

```bash
# 로컬 Ollama 서버
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_GENERATION_MODEL=mistral

# 타임아웃
EVAL_LLM_TIMEOUT=30  # 초
```

### 모델 선택

#### Mistral (추천)

```python
model = "mistral"
temperature = 0.3      # 낮음 = 더 결정적
top_p = 0.9
```

**장점**:
- 한국어 이해 우수
- 빠른 응답 (5-10초)
- 작은 모델 (7B)
- 일관된 JSON 출력

#### Llama2

```python
model = "llama2"
temperature = 0.2
top_p = 0.8
```

**특징**:
- 더 큰 모델 (13B)
- 느린 응답 (10-20초)
- 더 정확한 이유 설명

### 프롬프트 엔지니어링

```python
# 현재 신규성 판정 프롬프트
prompt = f"""
다음 청구항의 신규성을 평가하세요.

【청구항】
{claim_text}

【관련 선행기술】
{prior_art_context}

【판단 기준】
1. 동일한 기술구성이 존재하는가?
2. 기술적 특징이 명확히 구별되는가?

【응답 형식】
{{
    "is_novel": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "판단 이유"
}}
"""

# 프롬프트 개선:
# 1. Few-shot examples 추가
# 2. Chain-of-thought 활용
# 3. 역할 지정 ("너는 한국 특허 심사관이다")
```

---

## 5. 서버 설정

### 환경 변수 (.env 파일)

```ini
# DEBUG & ENVIRONMENT
DEBUG=false
ENVIRONMENT=production

# SERVER
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=4

# DATABASE
DATABASE_PATH=data/sessions.db
DATABASE_SESSION_TTL=3600          # 1시간

# OLLAMA
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_GENERATION_MODEL=mistral

# EVALUATION ENGINE
EVAL_NOVELTY_THRESHOLD=0.7
EVAL_RAG_TOP_K=5
EVAL_RAG_SIMILARITY_THRESHOLD=0.6
EVAL_LLM_TIMEOUT=30
EVAL_NOVELTY_USE_LLM=true
EVAL_INVENTIVE_USE_LLM=true
EVAL_INVENTIVE_USE_PRECEDENT=true
```

### 시작 옵션

```bash
# 개발 환경
python3 -m src.api.server \
    --debug \
    --reload \
    --log-level=debug

# 프로덕션
python3 -m src.api.server \
    --workers=4 \
    --bind=0.0.0.0:8000 \
    --timeout=120

# Docker
docker run -e ENVIRONMENT=production \
           -e SERVER_WORKERS=8 \
           -p 8000:8000 \
           project-override:latest
```

---

## 6. 성능 튜닝

### 메모리 최적화

```python
# 벡터 DB 메모리 캐시 크기 제한
VECTOR_CACHE_SIZE=1000  # 최대 1000개 항목 캐시

# LLM 응답 캐싱 (동일 청구항)
EVAL_RESULT_CACHE_TTL=3600  # 1시간
```

### 동시성 설정

```bash
# 동시 요청 처리 수
SERVER_WORKERS=4

# 데이터베이스 연결 풀
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 응답 시간 최적화

| 최적화 항목 | 기본값 | 빠른 설정 |
|----------|-------|---------|
| RAG top_k | 5 | 3 |
| 유사도 임계값 | 0.6 | 0.7 |
| LLM 활성화 | true | false (borderline만) |
| 캐싱 | enabled | aggressive |

```python
# 빠른 모드 설정
fast_config = EvaluationConfig(
    novelty=NoveltyConfig(
        vector_search_top_k=3,
        vector_similarity_threshold=0.7,
        use_llm_judgment=False,  # 필요시에만
    ),
    enable_result_caching=True,
)
```

---

## 7. 모니터링 및 로깅

### 로그 레벨 설정

```bash
# 환경 변수
LOG_LEVEL=INFO

# Python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluation_engine")
logger.setLevel(logging.DEBUG)
```

### 메트릭 수집

```python
from src.metrics.evaluation_metrics import EvaluationMetrics

metrics = EvaluationMetrics()

# 평가마다
metrics.record_novelty_evaluation(
    claim_id="claim_123",
    duration_ms=2500,
    is_novel=True,
    confidence=0.85
)

# 통계 조회
stats = metrics.get_statistics()
print(f"평균 평가 시간: {stats.avg_duration_ms}ms")
print(f"신규성 인정률: {stats.novelty_approval_rate * 100}%")
```

### 메트릭 대시보드

```bash
# Prometheus 메트릭 엔드포인트
curl http://localhost:8000/metrics

# 주요 메트릭:
# - evaluation_duration_ms (히스토그램)
# - evaluation_count (카운터)
# - novelty_approval_rate (게이지)
# - rag_search_latency_ms (히스토그램)
```

---

## 8. 설정 검증

### 설정 유효성 확인

```bash
# 스크립트
python3 -c "
from src.config.evaluation_config import get_evaluation_config
config = get_evaluation_config()
print('✅ 설정 로드 성공')
print(f'신규성 임계값: {config.novelty.min_similarity_threshold}')
print(f'RAG 활성화: {config.enable_rag}')
print(f'LLM 활성화: {config.enable_llm}')
"
```

### 설정 마이그레이션

```python
# v1 → v2 마이그레이션
def migrate_config_v1_to_v2(v1_config_dict):
    """이전 설정 형식 마이그레이션"""
    return {
        "novelty": {
            "min_similarity_threshold": v1_config_dict.get("similarity_threshold", 0.7),
            "vector_search_top_k": v1_config_dict.get("top_k", 5),
        },
        "inventive_step": {
            "technical_complexity": v1_config_dict.get("complexity_map", {}),
        },
        "enable_rag": v1_config_dict.get("use_rag", True),
        "enable_llm": v1_config_dict.get("use_llm", True),
    }
```

---

## 9. 샘플 설정 파일

### .env.example

```ini
# .env.example - 프로젝트 루트에 복사 후 수정

# ==============================================================================
# DEBUG & ENVIRONMENT
# ==============================================================================
DEBUG=false
ENVIRONMENT=production

# ==============================================================================
# SERVER CONFIGURATION
# ==============================================================================
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=4

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================
DATABASE_PATH=data/sessions.db
DATABASE_SESSION_TTL=3600

# ==============================================================================
# OLLAMA CONFIGURATION
# ==============================================================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_GENERATION_MODEL=mistral

# ==============================================================================
# EVALUATION ENGINE - NOVELTY
# ==============================================================================
EVAL_NOVELTY_THRESHOLD=0.7
EVAL_RAG_TOP_K=5
EVAL_RAG_SIMILARITY_THRESHOLD=0.6
EVAL_NOVELTY_USE_LLM=true
EVAL_NOVELTY_VECTOR_WEIGHT=0.6
EVAL_NOVELTY_LLM_WEIGHT=0.4

# ==============================================================================
# EVALUATION ENGINE - INVENTIVE STEP
# ==============================================================================
EVAL_MIN_FEATURE_COUNT=10
EVAL_FEATURE_WEIGHT=0.3
EVAL_INVENTIVE_USE_PRECEDENT=true
EVAL_PRECEDENT_TOP_K=5
EVAL_INVENTIVE_USE_LLM=true
EVAL_INVENTIVE_LLM_WEIGHT=0.6

# ==============================================================================
# EVALUATION ENGINE - GENERAL
# ==============================================================================
EVAL_LLM_TIMEOUT=30
EVAL_ENABLE_CACHING=true
EVAL_CACHE_TTL=3600
```

---

## 10. 문제 해결

### 신규성 판정이 너무 엄격함

**증상**: 모든 청구항을 신규성 없음으로 판정

**해결책**:
```python
# 임계값 낮추기
EVAL_NOVELTY_THRESHOLD=0.6

# 또는 LLM 가중치 증가
EVAL_NOVELTY_LLM_WEIGHT=0.6
```

### 평가가 너무 느림

**증상**: 평가 시간이 10초 이상

**해결책**:
```python
# RAG 결과 개수 감소
EVAL_RAG_TOP_K=3

# LLM 비활성화 (borderline만)
EVAL_NOVELTY_USE_LLM=false
```

### LLM이 유효한 JSON을 반환하지 않음

**증상**: JSON 파싱 오류

**해결책**:
```python
# 프롬프트 개선 (더 명확한 지시)
# 모델 변경 (mistral → llama2)
OLLAMA_GENERATION_MODEL=llama2

# 또는 응답 후처리 개선
def parse_llm_response(response: str) -> dict:
    # JSON 추출 로직 강화
    import json
    import re
    # { ... } 부분만 추출
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        return json.loads(match.group())
```

---

## 참고 자료

- **config 모듈**: `src/config/evaluation_config.py`
- **환경 설정**: `.env.example` (프로젝트 루트)
- **설정 로더**: `src/config/settings.py`
- **테스트**: `tests/test_evaluation_config.py`

