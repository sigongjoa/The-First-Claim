# 평가 시스템 아키텍처

## 개요

PROJECT: OVERRIDE의 평가 시스템은 특허청구항의 신규성과 진보성을 평가하는 3단계 하이브리드 엔진입니다.

### 평가 구조

```
청구항 입력
   ↓
[단계 1: 규칙 기반] (빠른 필터링)
   ↓
[단계 2: RAG 기반] (의미론적 검색)
   ↓
[단계 3: LLM 기반] (최종 판단)
   ↓
최종 평가 결과
```

## 1. 규칙 기반 평가 (단계 1)

### 신규성 평가
- **방식**: Jaccard 유사도 계산
- **공식**: `similarity = intersection(A,B) / union(A,B)`
- **구성요소**:
  - 기술적 특징 추출 (명사/용어)
  - 특징 비교
  - 유사도 점수 계산

### 진보성 평가
- **기술 분야 복잡도**:
  ```python
  {
    "전자": 0.8,        # Electronics - 높은 복잡도
    "기계": 0.7,        # Mechanical - 중간-높음
    "화학": 0.9,        # Chemical - 매우 높음
    "바이오": 0.9,      # Bio - 매우 높음
    "소프트웨어": 0.6,  # Software - 중간
    "디자인": 0.5       # Design - 중간-낮음
  }
  ```

- **특징 개수 고려**: `feature_weight = min(1.0, feature_count / 10 * 0.3)`
- **선행기술 거리**: `prior_art_distance = min(1.0, (count + 1) / 10)`

## 2. RAG 기반 평가 (단계 2)

### 검색 대상

**법률 조문 (특허법)**
- 총 40개 조문
- 예: 제29조(특허 요건), 제30조(선출원 주의), 제33조(진보성 판단)
- 벡터 임베딩: nomic-embed-text (768차원)

**판례 데이터**
- 총 12개 랜드마크 판례
- 신규성, 진보성, 권리범위, 명세서 기재 불충분
- 벡터 검색 + 풀텍스트 저장

### 검색 프로세스

```python
# 청구항 → 벡터 변환
query = f"특허 선행기술: {claim_text}"
embeddings = ollama.embed(query)  # nomic-embed-text

# 유사 문서 검색
results = vector_db.search(
    embeddings,
    top_k=5,  # 상위 5개
    min_similarity=0.6
)

# 결과 반환: [content, source, similarity, article_number]
```

### 신뢰도 계산
- **코사인 유사도**: 0.0 ~ 1.0
- **threshold**: 0.6 이상만 유의미
- **결합**: `rag_score = max(similarities)` 또는 weighted average

## 3. LLM 기반 평가 (단계 3)

### LLM 모델
- **모델**: Ollama (mistral 또는 llama2)
- **온도**: 0.3 (낮음 = 더 결정적)
- **타임아웃**: 30초

### 신규성 판단 프롬프트

```
다음 청구항의 신규성을 평가하세요.

【청구항】
{청구항 텍스트}

【관련 선행기술 및 법률 조문】
{RAG 결과들}

【판단 기준】
1. 동일한 기술구성이 존재하는가?
2. 기술적 특징이 명확히 구별되는가?
3. 선행기술과의 차이점은 무엇인가?

【응답 형식】
{
    "is_novel": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "판단 이유",
    "key_differences": ["차이점1", "차이점2"]
}
```

### 진보성 판단 프롬프트

```
다음 청구항의 진보성을 평가하세요.

【청구항】
{청구항 텍스트}

【관련 판례】
{판례 검색 결과}

【판단 기준】
1. 선행기술로부터의 기술적 진보가 있는가?
2. 통상의 기술자가 쉽게 도출할 수 있는가?
3. 예측 불가능한 기술 효과가 있는가?

【응답 형식】
{
    "has_inventive_step": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "판단 이유"
}
```

## 4. 점수 결합 로직

### 신규성 최종 점수

```python
final_score = (
    rule_weight * rule_score +      # 규칙: 30% 가중치
    rag_weight * rag_similarity +   # RAG: 40% 가중치
    llm_weight * llm_confidence     # LLM: 30% 가중치
)

is_novel = final_score < 0.7  # 임계값 이하면 신규
```

### 진보성 최종 판단

```python
final_score = (
    rule_weight * rule_score +           # 규칙: 40% 가중치
    precedent_weight * precedent_score + # 판례: 30% 가중치
    llm_weight * llm_judgment            # LLM: 30% 가중치
)

has_inventive_step = final_score > 0.6  # 임계값 이상이면 있음
```

## 5. 구성 요소

### 청구항 파서 (ClaimComponentParser)

**기능**:
- 청구항을 전제부, 본문, 특징부로 분해
- 기술적 특징 추출
- 동의어 정규화

**동의어 예시**:
```python
"표시_장치": ["디스플레이", "화면", "모니터", "LCD", "LED", "OLED"]
"저장_장치": ["메모리", "스토리지", "저장부", "HDD", "SSD"]
"처리_장치": ["프로세서", "CPU", "처리부"]
```

### 설정 관리 (EvaluationConfig)

**환경 변수로 오버라이드 가능**:
```bash
# 신규성 평가 설정
EVAL_NOVELTY_THRESHOLD=0.7      # 유사도 임계값
EVAL_RAG_TOP_K=5                # RAG 검색 결과 개수

# LLM 설정
EVAL_LLM_MODEL=mistral          # 모델 선택
EVAL_TIMEOUT=5                  # 평가 타임아웃 (초)

# 기능 활성화
EVAL_ENABLE_LLM=true            # LLM 사용 여부
EVAL_ENABLE_RAG=true            # RAG 사용 여부

# 디버깅
EVAL_DEBUG=false                # 디버그 로깅
```

## 6. 데이터 흐름

### 신규성 평가 흐름

```
청구항 텍스트
    ↓
청구항 파싱 (ClaimComponentParser)
    ↓ [특징 추출 + 정규화]
    ↓
규칙 기반 유사도 (Jaccard)
    ↓ [rule_score]
    ↓
RAG 검색 (벡터 DB)
    ↓ [rag_similarity, 관련 조문]
    ↓
LLM 판단 (Ollama)
    ↓ [llm_confidence, 이유]
    ↓
점수 결합
    ↓ [최종 신뢰도]
    ↓
신규성 결과
```

### 진보성 평가 흐름

```
청구항 텍스트 + 기술분야
    ↓
규칙 기반 평가 (기술 복잡도)
    ↓ [rule_score]
    ↓
판례 검색 (RAG)
    ↓ [precedent_relevance, 관련 판례]
    ↓
LLM 판단 (Ollama)
    ↓ [llm_judgment, 이유]
    ↓
점수 결합
    ↓ [최종 신뢰도]
    ↓
진보성 결과
```

## 7. 성능 특성

| 단계 | 평균 시간 | 특징 |
|------|----------|------|
| 규칙 기반 | <50ms | 빠른 필터링, 메모리 기반 |
| RAG 검색 | 200-500ms | 벡터 유사도 계산 |
| LLM 판단 | 1-3초 | Ollama API 호출 |
| **전체** | **<5초** | 안정적, 신뢰할 수 있음 |

## 8. 확장 계획

### 단기 (1-2개월)
- [ ] 특허법 조문 확대 (40 → 200+)
- [ ] 판례 데이터 확충 (12 → 100+)
- [ ] 동의어 사전 개선
- [ ] 성능 최적화

### 중기 (3-6개월)
- [ ] 실제 특허청구항 학습 데이터
- [ ] 심사기준 문서 통합
- [ ] 다국어 지원 (영문, 중문)
- [ ] 캐싱 메커니즘

### 장기 (6-12개월)
- [ ] Fine-tuning LLM (특허법 전문)
- [ ] 강화학습 (평가 정확도 향상)
- [ ] 산업별 평가 모델 (전자, 화학, 바이오)
- [ ] 실시간 API 배포

## 9. 참고 자료

- **RAG 시스템**: `src/knowledge_base/rag_system.py`
- **벡터 DB**: `src/knowledge_base/vector_database.py`
- **평가 엔진**: `src/dsl/logic/hybrid_evaluator.py`
- **구성**: `src/config/evaluation_config.py`
- **테스트**: `tests/integration/test_hybrid_evaluation.py`
