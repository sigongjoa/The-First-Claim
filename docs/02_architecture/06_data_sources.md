# 데이터 소스 및 지식 기반 아키텍처

## 개요

PROJECT: OVERRIDE의 평가 시스템은 다층적 지식 기반에 의존합니다:

1. **특허법 조문**: 한국 특허법 조항 (40개 이상)
2. **판례 데이터**: 대법원/특허법원 판례 (12개 이상)
3. **기술 용어사전**: 특허 기술용어 동의어 매핑
4. **벡터 데이터베이스**: ChromaDB의 임베딩 인덱스

---

## 1. 특허법 조문 데이터베이스

### 데이터 구조

```python
@dataclass
class LawArticle:
    article_number: str           # "제30조"
    title: str                    # "특허를 받을 수 없는 발명"
    content: str                  # 전체 조문 텍스트
    subsections: List[str]        # 항, 호 분류
    category: str                 # "특허법", "시행령"
    requirements: List[str]       # 필수 요건
    effects: List[str]            # 법적 효과
    exceptions: List[str]         # 예외 사항
    effective_date: date          # 시행일
    amendment_history: List[str]  # 개정 이력
```

### 현재 포함 조항 (40개)

#### 기본 조항
- 제1조: 목적
- 제2조: 정의
- 제3조: 특허청의 설치
- 제4조: 특허권

#### 출원 관련
- 제7조: 특허 출원
- 제10조: 출원 방식
- 제13조: 출원서의 기재 사항

#### 신규성 관련
- 제29조: 특허를 받을 수 없는 발명
- 제30조: 선출원 주의
- 제31조: 신규성 상실의 예외

#### 진보성 관련
- 제33조: 진보성
- 제34조: 발명의 명확한 표현 필요성

#### 권리범위 관련
- 제52조: 특허권의 범위
- 제53조: 균등론
- 제54조: 특허권의 침해

#### 심사 절차
- 제45조: 거절이유 통지
- 제46조: 보정
- 제47조: 이의 신청

#### 우선권 관련
- 제55조: 우선권 주장
- 제56조: 파리협약 우선권

#### 기타
- 제84조: 침해 추정
- 제100조: 특허의 무효

### 데이터 파일

**위치**: `data/patent_law_articles.json`

**형식**:
```json
{
  "articles": [
    {
      "article_number": "제30조",
      "title": "특허를 받을 수 없는 발명",
      "content": "...",
      "subsections": ["1", "2", "3"],
      "category": "특허법",
      "requirements": ["신규성", "진보성"],
      "effects": ["특허 불가", "권리 없음"],
      "exceptions": [],
      "effective_date": "2021-08-19",
      "amendment_history": ["2020년 개정", "2021년 8월 시행"]
    },
    ...
  ],
  "total": 40,
  "last_updated": "2025-12-08"
}
```

### 수집 방법

#### 현재 방식: 수동 컴파일

**스크립트**: `src/data_collection/patent_law_scraper.py`

```python
class PatentLawScraper:
    def scrape_articles(self) -> List[LawArticle]:
        """한국 특허법 조항 수집"""
        # 수동으로 정의된 40개 조항
        articles = [
            LawArticle(
                article_number="제30조",
                title="특허를 받을 수 없는 발명",
                content="...",
                ...
            ),
            # ... 40개 총
        ]
        return articles

    def save_articles_to_json(self, articles: List[LawArticle],
                             output_path: str) -> None:
        """JSON으로 저장"""
```

#### 향후 개선: API 기반 수집

**대상**: 대한민국 법제처 Open API (e-법률)

```python
class KLIScraper:
    """법제처 e-법률 API를 통한 자동 수집"""

    async def fetch_law_articles_from_api(self, law_name: str) -> List[LawArticle]:
        # API: https://www.law.go.kr/api
        # 매개변수: 법률명="특허법"
        # 반환: 모든 조항 자동 파싱
        pass
```

### 벡터화 프로세스

**방식**: Ollama nomic-embed-text (768차원)

```python
# 1. 텍스트 준비
query = f"""
제목: {article.title}
조문: {article.content}
요건: {', '.join(article.requirements)}
효과: {', '.join(article.effects)}
"""

# 2. 임베딩 생성
embeddings = ollama.embed(
    model="nomic-embed-text",
    input=query
)  # 768차원 벡터

# 3. 벡터 DB 저장
vector_db.upsert(
    ids=[article.article_number],
    embeddings=[embeddings],
    metadatas=[{
        "article_number": article.article_number,
        "title": article.title,
        "category": article.category,
        "effective_date": str(article.effective_date),
        "source_type": "law"
    }],
    documents=[query]
)
```

---

## 2. 판례 데이터베이스

### 데이터 구조

```python
@dataclass
class PrecedentCase:
    case_number: str           # "2020후1234"
    court: str                 # "대법원", "특허법원"
    decision_date: date        # 선고일
    case_type: str             # "신규성", "진보성", "권리범위"
    summary: str               # 사건의 개요 (500자 이내)
    full_text: str             # 전문 (판시사항, 이유)
    key_holdings: List[str]    # 핵심 판단 요지
    cited_articles: List[str]  # 인용한 법조문
    outcome: str               # "인용", "기각", "파기환송"
    patent_field: str          # "전자", "기계", "화학"
```

### 현재 포함 판례 (12개)

#### 신규성 관련 (3건)
1. **대법원 2020다237618**
   - 주제: 공개된 기술과의 신규성 판단
   - 판시: "기술적 특징이 명확히 구별되면 신규"

2. **특허법원 2019허7890**
   - 주제: 복합적 기술 조합의 신규성
   - 판시: "선행기술과의 부분 중복은 무관"

3. **대법원 2021다54321**
   - 주제: 공개의 범위와 신규성
   - 판시: "불완전한 공개는 신규성 상실 아님"

#### 진보성 관련 (4건)
4. **특허법원 2018허12345**
   - 주제: 진보성 판단 기준
   - 판시: "통상의 기술자가 용이하게 도출할 수 없어야 함"

5. **대법원 2019다88765**
   - 주제: 기술 분야의 복잡도
   - 판시: "화학 분야는 예측 불가능성 높음"

6. **특허법원 2020허34567**
   - 주제: 예측 불가능한 기술 효과
   - 판시: "선행기술에서 예상 불가능한 효과 = 진보"

7. **대법원 2021다76543**
   - 주제: 선행기술 조합의 동기부여
   - 판시: "기술적 필연성 없는 조합은 진보"

#### 권리범위 관련 (3건)
8. **특허법원 2019허55555**
   - 주제: 권리범위 해석 (균등론)
   - 판시: "동일한 기술적 구성으로 유사 기능"

9. **대법원 2020다99999**
   - 주제: 명세서 기재 범위
   - 판시: "명세서에 명시되지 않은 범위는 보호 안 함"

#### 명세서 기재 불충분 (2건)
10. **특허법원 2018허11111**
    - 주제: 발명의 명확한 표현 부족
    - 판시: "모호한 기술용어는 거절이유"

11. **대법원 2019다22222**
    - 주제: 재현성 부족
    - 판시: "기술자가 실시할 수 없으면 불충분"

12. **특허법원 2021허88888**
    - 주제: 구체적 실시 예 부재
    - 판시: "일반적 기재만으로는 불충분"

### 데이터 파일

**위치**: `data/patent_precedent_cases.json`

**형식**:
```json
{
  "cases": [
    {
      "case_number": "2020다237618",
      "court": "대법원",
      "decision_date": "2020-12-15",
      "case_type": "신규성",
      "summary": "공개된 기술과 청구항의 기술적 특징이 명확히 구별되는 경우의 신규성 인정 기준을 판시하였다.",
      "full_text": "...",
      "key_holdings": [
        "기술적 특징이 명확히 구별되면 신규성 인정",
        "부분적 중복만으로는 신규성 상실 아님"
      ],
      "cited_articles": ["제29조", "제30조"],
      "outcome": "인용",
      "patent_field": "전자"
    },
    ...
  ],
  "total": 12,
  "by_case_type": {
    "신규성": 3,
    "진보성": 4,
    "권리범위": 3,
    "명세서": 2
  },
  "last_updated": "2025-12-08"
}
```

### 수집 방법

#### 현재 방식: 수동 입력

**스크립트**: `src/data_collection/initialize_precedent_db.py`

```python
def initialize_precedent_database(output_path: str = "data/patent_precedent_cases.json"):
    """판례 데이터베이스 초기화"""
    cases = [
        PrecedentCase(
            case_number="2020다237618",
            court="대법원",
            decision_date=date(2020, 12, 15),
            case_type="신규성",
            summary="...",
            full_text="...",
            ...
        ),
        # ... 12개 총
    ]

    save_cases_to_json(cases, output_path)
```

#### 향후 개선: 웹 스크래핑

**대상 1**: 대법원 판례검색 (glaw.scourt.go.kr)
```python
class SupremeCourtScraper:
    async def fetch_patent_cases(self, keyword: str) -> List[PrecedentCase]:
        # 특허 관련 판례 검색
        # 선고문 파싱
        # 메타데이터 추출
        pass
```

**대상 2**: 특허법원 판례 (patent.court.go.kr)
```python
class PatentCourtScraper:
    async def fetch_cases(self, case_type: str) -> List[PrecedentCase]:
        # 신규성, 진보성, 권리범위 등 카테고리별 검색
        # 최신 판례 수집
        pass
```

### 벡터화 프로세스

**방식**: 요약 + 핵심 판시 사항 임베딩

```python
# 1. 검색용 텍스트 준비
query = f"""
판례: {case.case_number}
법원: {case.court}
주제: {case.case_type}

요약:
{case.summary}

핵심 판시:
{chr(10).join('- ' + h for h in case.key_holdings)}

인용 조문:
{', '.join(case.cited_articles)}
"""

# 2. 임베딩 생성 및 저장
embeddings = ollama.embed(
    model="nomic-embed-text",
    input=query
)

vector_db.upsert(
    ids=[case.case_number],
    embeddings=[embeddings],
    metadatas=[{
        "case_number": case.case_number,
        "court": case.court,
        "case_type": case.case_type,
        "patent_field": case.patent_field,
        "decision_date": str(case.decision_date),
        "outcome": case.outcome,
        "source_type": "precedent"
    }],
    documents=[query]
)

# 3. 별도 SQL 저장소에 전문 저장
sql_store.insert_precedent(
    case_number=case.case_number,
    full_text=case.full_text,
    metadata=case.to_dict()
)
```

---

## 3. 기술 용어 동의어 사전

### 데이터 구조

```python
class SynonymDictionary:
    """특허 기술용어 동의어 매핑"""

    def __init__(self):
        self.synonyms = {
            "표시_장치": {
                "한글": ["표시장치", "디스플레이", "화면", "모니터"],
                "영문": ["display", "screen", "monitor"],
                "약어": ["LCD", "LED", "OLED"]
            },
            "저장_장치": {
                "한글": ["메모리", "스토리지", "저장부", "저장소"],
                "영문": ["storage", "memory"],
                "약어": ["HDD", "SSD", "DRAM"]
            },
            "처리_장치": {
                "한글": ["프로세서", "처리부", "중앙처리장치"],
                "영문": ["processor", "cpu"],
                "약어": ["CPU", "GPU", "APU"]
            },
            # ... 100+ 항목
        }

    def get_canonical_form(self, term: str) -> str:
        """동의어를 표준형으로 정규화"""
        term_lower = term.lower()
        for canonical, variants in self.synonyms.items():
            if self._match_variant(term_lower, variants):
                return canonical
        return term

    def are_synonyms(self, term1: str, term2: str) -> bool:
        """두 용어가 동의어인지 확인"""
        canonical1 = self.get_canonical_form(term1)
        canonical2 = self.get_canonical_form(term2)
        return canonical1 == canonical2
```

### 데이터 파일

**위치**: `assets/synonyms.json`

**형식**:
```json
{
  "표시_장치": {
    "한글": ["표시장치", "디스플레이", "화면", "모니터"],
    "영문": ["display", "screen", "monitor"],
    "약어": ["LCD", "LED", "OLED", "TFT"]
  },
  "저장_장치": {
    "한글": ["메모리", "스토리지", "저장부"],
    "영문": ["memory", "storage"],
    "약어": ["HDD", "SSD", "DRAM", "ROM"]
  },
  "처리_장치": {
    "한글": ["프로세서", "처리부", "CPU"],
    "영문": ["processor"],
    "약어": ["CPU", "GPU"]
  },
  ...
}
```

### 관리 방법

#### 추가 방법

```bash
# 1. assets/synonyms.json 편집
# 2. 테스트
python3 -c "
from src.dsl.logic.claim_parser import SynonymDictionary
syn_dict = SynonymDictionary.from_json('assets/synonyms.json')
print(syn_dict.get_canonical_form('디스플레이'))  # '표시_장치' 확인
"
# 3. 커밋
git add assets/synonyms.json
git commit -m "Update: Add new synonyms for [용어]"
```

#### 확장 자동화

```python
# 향후: NLP 기반 자동 발견
class SynonymExtractor:
    """Word2Vec, FastText 기반 동의어 자동 발견"""

    def extract_from_corpus(self, patent_corpus: List[str]) -> Dict[str, Set[str]]:
        """특허 문서에서 동의어 후보 추출"""
        # 1. Word2Vec 학습
        # 2. 유사도 계산
        # 3. 클러스터링
        # 4. 결과 제안
        pass
```

---

## 4. 벡터 데이터베이스 아키텍처

### 백엔드: ChromaDB

**설정**:
```python
from chromadb.config import Settings
from chromadb import Client

# 로컬 파일 기반 스토리지
settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="data/vector_db",
    anonymized_telemetry=False
)

client = Client(settings)
collection = client.get_or_create_collection(
    name="patent_knowledge_base",
    metadata={
        "description": "특허법 및 판례 벡터 인덱스",
        "embedding_model": "nomic-embed-text",
        "dimension": 768
    }
)
```

### 인덱싱 구조

```
patent_knowledge_base (ChromaDB Collection)
├── Law Articles (40개)
│   ├── Document: 조문 텍스트
│   ├── Embedding: 768차원 벡터
│   └── Metadata:
│       ├── article_number: "제30조"
│       ├── category: "특허법"
│       ├── source_type: "law"
│       └── effective_date: "2021-08-19"
│
└── Precedent Cases (12개)
    ├── Document: 판례 요약 + 핵심 판시
    ├── Embedding: 768차원 벡터
    └── Metadata:
        ├── case_number: "2020다237618"
        ├── case_type: "신규성"
        ├── source_type: "precedent"
        └── decision_date: "2020-12-15"
```

### 검색 프로세스

```python
async def search_knowledge_base(query: str, top_k: int = 5) -> List[SearchResult]:
    """지식 기반 검색"""

    # 1. 쿼리 임베딩
    query_embedding = ollama.embed(
        model="nomic-embed-text",
        input=query
    )

    # 2. 벡터 검색
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "$or": [
                {"source_type": "law"},
                {"source_type": "precedent"}
            ]
        }
    )

    # 3. 결과 변환
    search_results = []
    for i, doc in enumerate(results["documents"][0]):
        search_results.append(SearchResult(
            content=doc,
            source=results["metadatas"][0][i].get("article_number") or
                   results["metadatas"][0][i].get("case_number"),
            similarity=results["distances"][0][i],  # 코사인 거리
            metadata=results["metadatas"][0][i]
        ))

    return search_results
```

### 성능 특성

| 작업 | 시간 | 용량 |
|------|------|------|
| 인덱싱 (40 + 12) | ~2초 | ~10MB |
| 검색 (top_k=5) | 50-100ms | - |
| 메모리 로드 | 시작 시 ~50MB | - |

---

## 5. 데이터 통합 파이프라인

### 초기화 프로세스

```bash
# 1단계: 데이터 수집
python3 src/data_collection/patent_law_scraper.py
python3 src/data_collection/initialize_precedent_db.py

# 2단계: 벡터 임베딩
python3 -c "
from src.knowledge_base.vector_db_loader import load_knowledge_base
load_knowledge_base()
"

# 3단계: 서버 시작
python3 -m src.api.server
```

### 라이프사이클

```
애플리케이션 시작
    ↓
[vector_db_loader.py] 로드 기준 확인
    ↓
    ├─ 데이터 없음 → 초기화 (2-3초)
    └─ 데이터 있음 → 기존 로드 (1초)
    ↓
ChromaDB 인메모리 캐시
    ↓
평가 엔진 준비 완료
    ↓
요청 처리 시작
```

### 업데이트 전략

#### 일일 업데이트 (개발 환경)

```python
# 새 판례 발견 시
def update_precedent_database():
    # 1. 새 판례 수집
    new_cases = await patent_court_scraper.fetch_recent_cases()

    # 2. JSON 추가
    existing = load_json("data/patent_precedent_cases.json")
    existing["cases"].extend(new_cases)
    save_json(existing, "data/patent_precedent_cases.json")

    # 3. 벡터 DB 업데이트
    await reload_vector_database()

    # 4. 커밋
    git_commit(f"Add {len(new_cases)} new precedent cases")
```

#### 분기별 업데이트 (프로덕션)

```
Q1: 신규성 관련 판례 확충
Q2: 진보성 관련 판례 확충
Q3: 권리범위 관련 판례 확충
Q4: 특허법 조문 개정사항 반영
```

---

## 6. 데이터 품질 관리

### 검증 체크리스트

```python
def validate_knowledge_base() -> ValidationReport:
    """지식 기반 데이터 품질 검증"""

    errors = []
    warnings = []

    # 1. 법조문 검증
    if len(law_articles) < 40:
        errors.append(f"법조문 부족: {len(law_articles)}/40")

    # 2. 판례 검증
    if len(precedent_cases) < 12:
        errors.append(f"판례 부족: {len(precedent_cases)}/12")

    # 3. 벡터 검증
    embeddings_count = count_embeddings_in_vector_db()
    if embeddings_count != len(law_articles) + len(precedent_cases):
        errors.append(f"임베딩 불일치: {embeddings_count} vs {len(law_articles) + len(precedent_cases)}")

    # 4. 동의어 검증
    if not SynonymDictionary.load_successfully():
        warnings.append("동의어 사전 로드 경고")

    return ValidationReport(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

### 모니터링

```bash
# 데이터 상태 확인
python3 -c "
from src.knowledge_base.vector_db_loader import validate_knowledge_base
report = validate_knowledge_base()
print(report)
"
```

---

## 7. 향후 확장 계획

### 단기 (1-3개월)

- 특허법 조문: 40 → 100개 (전체 조문 완성)
- 판례: 12 → 50개 (주요 판례 집중 수집)
- 동의어: 50 → 200개 (기술 분야별 확충)

### 중기 (3-6개월)

- 실제 특허청구항 학습 데이터 (100-200건)
- 심사기준 문서 통합
- 다국어 지원 (영문, 중문)
- 캐싱 메커니즘 추가

### 장기 (6-12개월)

- Fine-tuning LLM (특허법 전문)
- 산업별 평가 모델 (전자, 화학, 바이오)
- 실시간 판례 업데이트 자동화
- 공개 API 제공

---

## 8. 참고 자료

- **스크래퍼**: `src/data_collection/`
- **모델**: `src/knowledge_base/models.py`
- **로더**: `src/knowledge_base/vector_db_loader.py`
- **테스트**: `tests/test_knowledge_base.py`
- **데이터**: `data/` 디렉토리

