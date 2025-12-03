# 테스트 전략 & Definition of Done (DOD)

## 개요

"좋은 코드"는 테스트 없는 코드가 아닙니다. 이 프로젝트는 **TDD(Test-Driven Development)** 기반으로 진행되므로, 각 Phase마다 명확한 테스트 전략과 완료 기준이 필요합니다.

---

## 1. 테스트 피라미드

```
                    🔺 E2E Tests (End-to-End)
                   /                      \
                  /  배틀 시뮬레이션 전체    \
                 /   법적 판정 전체 흐름      \
                /________________________\
               /                          \
              /  통합 테스트 (Integration)  \
             /   - Logic Engine + KB      \
            /    - Grammar + Vocabulary   \
           /___________________________\
          /                            \
         /   단위 테스트 (Unit Tests)    \
        /    - 각 클래스/함수 검증        \
       /     - 예상 동작 확인             \
      /____________________________\

비율: Unit(60%) > Integration(25%) > E2E(15%)
```

### 테스트 레이어별 목표

| 레이어 | 목표 | 테스트 수 | 실행 시간 | 유지보수 |
|--------|------|---------|---------|---------|
| **Unit** | 개별 함수/클래스의 정확성 | 많음 (100+) | 빠름 | 쉬움 |
| **Integration** | 컴포넌트 간 상호작용 | 중간 (30-50) | 중간 | 중간 |
| **E2E** | 사용자 관점의 전체 흐름 | 적음 (10-15) | 느림 | 어려움 |

---

## 2. 테스트 타입별 정의

### 2.1 Unit Tests (단위 테스트)

**목적**: 개별 클래스/함수가 예상대로 작동하는지 검증

**대상**:
- `CivilLawStatute`, `PatentRequirement` 등 모든 데이터 모델
- `ClaimGrammar.validate_structure()` 등 모든 검증 함수
- `NoveltyEvaluator.evaluate()` 등 모든 평가 함수

**예시**:

```python
# tests/test_civil_law_vocabulary.py

def test_civil_law_statute_creation():
    """CivilLawStatute 객체 생성 테스트"""
    statute = CivilLawStatute(
        statute_number="제145조",
        title="저작권자의 권리",
        requirements=["독창성", "표현 고정"],
        effects=["복제권", "배포권"],
        exceptions=["공정이용"]
    )

    assert statute.statute_number == "제145조"
    assert len(statute.requirements) == 2
    assert "복제권" in statute.effects
    # ✅ PASS


def test_claim_element_missing_name():
    """필수 속성 누락 시 에러 발생 테스트"""
    with pytest.raises(ValueError):
        ClaimElement(
            id="elem_1",
            name="",  # ❌ 빈 문자열
            description="무언가",
            is_essential=True
        )
    # ✅ PASS: 예상대로 에러 발생
```

---

### 2.2 Integration Tests (통합 테스트)

**목적**: 여러 컴포넌트가 함께 정상 작동하는지 검증

**대상**:
- Vocabulary + Grammar 조합 (데이터 모델이 검증 규칙과 호환되는가?)
- Grammar + LogicEngine 조합 (검증된 청구항이 평가되는가?)
- LogicEngine + KnowledgeBase 조합 (판례가 올바르게 적용되는가?)

**예시**:

```python
# tests/test_integration_vocabulary_grammar.py

def test_claim_structure_validation_with_real_claim():
    """실제 청구항으로 Grammar 검증 테스트"""
    # 1. Vocabulary로 청구항 생성
    claim = Claim(
        claim_number=1,
        preamble="다음으로 이루어진 장치",
        elements=[
            ClaimElement(id="e1", name="전송부", is_essential=True),
            ClaimElement(id="e2", name="수신부", is_essential=True),
        ]
    )

    # 2. Grammar로 검증
    validator = ClaimGrammar()
    result = validator.validate_structure(claim)

    # 3. 검증 통과 확인
    assert result.verdict == "PASS"
    assert result.error_count == 0
    # ✅ PASS


def test_novelty_evaluation_with_prior_art():
    """선행기술과 함께 신규성 평가 테스트"""
    # 1. 선행기술 설정
    prior_art = PriorArt(
        reference_id="JP2020-100000",
        title="전송 장치",
        content="전송부와 저장부로 이루어진..."
    )

    # 2. 청구항 설정 (선행기술과 다른 구성)
    claim = Claim(
        claim_number=1,
        elements=[
            ClaimElement(id="e1", name="전송부"),
            ClaimElement(id="e2", name="처리부"),  # ← 다른 요소
        ]
    )

    # 3. 신규성 평가
    evaluator = NoveltyEvaluator()
    result = evaluator.evaluate(claim, [prior_art])

    # 4. 신규성 있음 확인
    assert result.verdict == "PASS"  # 신규성 있음
    # ✅ PASS
```

---

### 2.3 E2E Tests (엔드-투-엔드 테스트)

**목적**: 사용자 관점에서 전체 시스템 흐름이 정상 작동하는지 검증

**시나리오**:
1. 사용자가 청구항을 입력한다
2. 시스템이 문법을 검증한다
3. Logic Engine이 신규성을 평가한다
4. 결과를 사용자에게 표시한다

**예시**:

```python
# tests/test_e2e_complete_workflow.py

def test_complete_patent_examination_workflow():
    """특허 심사의 완전한 워크플로우 E2E 테스트"""

    # 1단계: 사용자 입력 (청구항)
    user_input = {
        "claim_number": 1,
        "preamble": "다음으로 이루어진 장치",
        "elements": [
            {"name": "전송부", "description": "데이터를 전송"},
            {"name": "수신부", "description": "데이터를 수신"},
        ]
    }

    # 2단계: 청구항 생성
    claim = Claim.from_dict(user_input)

    # 3단계: 문법 검증
    grammar = ClaimGrammar()
    grammar_result = grammar.validate_structure(claim)
    assert grammar_result.verdict == "PASS"

    # 4단계: 선행기술 검색 (KB에서)
    kb = PrecedentDatabase()
    prior_arts = kb.query_similar_precedents("전송 장치", top_k=5)

    # 5단계: 평가 (신규성, 진보성)
    engine = LogicEngine(kb)
    evaluation = engine.evaluate_claim(claim, prior_arts)

    # 6단계: 결과 검증
    assert evaluation.verdict in ["ACCEPT", "REJECT"]
    assert evaluation.reasoning is not None
    assert evaluation.confidence_score >= 0.0

    # ✅ PASS: 전체 흐름이 정상 작동
```

---

## 3. Definition of Done (DOD)

### 3.1 Phase 1-1: Civil Law Vocabulary

#### 완료 기준

- [ ] **코드 완성도**
  - [ ] 모든 클래스 구현 (`CivilLawStatute`, `Person`, `Transaction`, `LegalRight`)
  - [ ] 모든 메서드에 타입 힌팅 적용
  - [ ] 모든 메서드에 docstring 작성
  - [ ] `__init__`, `__repr__`, `__eq__`, `__str__` 메서드 구현

- [ ] **단위 테스트 (Unit Tests)**
  - [ ] 클래스 생성 테스트 (정상 케이스 3개 이상)
  - [ ] 속성 설정 및 조회 테스트 (5개 이상)
  - [ ] **엣지 케이스 테스트 (필수!)**
    - [ ] 빈 문자열 입력 처리
    - [ ] None 값 입력 처리
    - [ ] 중복된 요건/효과 처리
    - [ ] 매우 긴 문자열 입력 처리
    - [ ] 특수 문자 포함된 입력 처리
  - [ ] **에러 처리 테스트**
    - [ ] 필수 속성 누락 → ValueError
    - [ ] 잘못된 타입 입력 → TypeError
  - [ ] 테스트 커버리지 ≥ 95%

- [ ] **문서화**
  - [ ] 각 클래스의 목적과 사용법 주석
  - [ ] 각 속성의 의미 설명
  - [ ] 예제 코드 포함 (README.md 또는 docstring)

- [ ] **Code Quality**
  - [ ] PEP 8 스타일 준수 (black으로 자동 포맷)
  - [ ] 모든 함수 길이 < 50줄
  - [ ] Cyclomatic complexity < 5

#### 테스트 케이스 명세

```python
# tests/test_civil_law_vocabulary.py

class TestCivilLawStatuteCreation:
    """CivilLawStatute 생성 테스트"""

    def test_valid_statute_creation(self):
        """✅ 정상 케이스: 모든 속성 유효"""
        # given, when, then 패턴
        pass

    def test_statute_with_empty_requirements(self):
        """✅ 엣지 케이스: 요건 리스트가 비어있음"""
        pass

    def test_statute_with_duplicate_effects(self):
        """✅ 엣지 케이스: 중복된 효과"""
        pass

    def test_statute_with_very_long_description(self):
        """⚠️ 엣지 케이스: 매우 긴 설명"""
        pass

    def test_statute_with_special_characters(self):
        """⚠️ 엣지 케이스: 특수 문자 포함"""
        pass

class TestCivilLawStatuteValidation:
    """CivilLawStatute 검증 테스트"""

    def test_missing_statute_number(self):
        """❌ 에러 케이스: 조문 번호 없음 → ValueError"""
        with pytest.raises(ValueError):
            pass

    def test_invalid_type_for_effects(self):
        """❌ 에러 케이스: 효과가 리스트가 아님 → TypeError"""
        with pytest.raises(TypeError):
            pass

class TestPersonEquality:
    """Person 객체 동등성 테스트"""

    def test_same_person_are_equal(self):
        """두 명의 같은 사람은 동등해야 함"""
        person1 = Person(name="홍길동", role="저작권자")
        person2 = Person(name="홍길동", role="저작권자")
        assert person1 == person2
```

---

### 3.2 Phase 1-2: Patent Law Vocabulary

#### 완료 기준

- [ ] **코드 완성도**
  - [ ] 모든 클래스 구현 (`PatentRequirement`, `ClaimElement`, `Claim`, `PriorArt`)
  - [ ] 모든 메서드 타입 힌팅 + docstring
  - [ ] Claim 객체의 계층 구조 (독립/종속 청구항) 구현

- [ ] **단위 테스트**
  - [ ] 각 클래스별 기본 생성 테스트 (최소 3개)
  - [ ] **엣지 케이스 테스트 (필수!)**
    - [ ] 청구항 숫자가 0 또는 음수
    - [ ] 종속 청구항이 존재하지 않는 청구항 참조
    - [ ] 순환 참조 (A→B→A)
    - [ ] 구성요소가 100개 이상
    - [ ] 선행기술 참조가 존재하지 않음
  - [ ] 테스트 커버리지 ≥ 95%

- [ ] **Integration 테스트**
  - [ ] Claim과 ClaimElement의 관계 검증
  - [ ] PriorArt와 ClaimElement의 유사도 계산

- [ ] **문서화 & Code Quality**
  - [ ] PEP 8 준수
  - [ ] 함수 길이 < 50줄
  - [ ] Complexity < 5

---

### 3.3 Phase 2-1: Claim Grammar

#### 완료 기준

- [ ] **코드 완성도**
  - [ ] `ClaimGrammar` 클래스의 모든 검증 함수 구현
  - [ ] BNF 문법 정의 문서화
  - [ ] 각 검증 함수마다 상세 docstring

- [ ] **단위 테스트**
  - [ ] 유효한 청구항 5개 이상 (PASS)
  - [ ] **무효한 청구항 (FAIL) 케이스 5개 이상**
    - [ ] 서문 없음
    - [ ] 구성요소 없음
    - [ ] 기능 설명 없음
    - [ ] 종속 청구항이 존재하지 않는 청구항 참조
    - [ ] 명확성 부족 (사용하지 않은 수식어 포함)

- [ ] **Integration 테스트**
  - [ ] 생성된 Claim 객체를 Grammar로 검증
  - [ ] 검증 결과가 상세한 에러 메시지 포함

- [ ] **E2E 테스트**
  - [ ] 사용자 입력 → 파싱 → 검증 → 결과 전체 흐름

---

### 3.4 Phase 3-1: Novelty Evaluator

#### 완료 기준

- [ ] **코드 완성도**
  - [ ] `NoveltyEvaluator.evaluate()` 구현
  - [ ] 선행기술 매칭 로직 구현
  - [ ] 판정 근거 생성 함수 구현

- [ ] **단위 테스트**
  - [ ] 신규성 있음 (PASS) 케이스 5개
    - [ ] 청구항의 핵심 요소가 어떤 선행기술에도 없음
    - [ ] 청구항이 여러 선행기술의 조합이 필요
    - [ ] etc.
  - [ ] 신규성 없음 (FAIL) 케이스 5개
    - [ ] 청구항의 모든 요소가 단일 선행기술에 전개
    - [ ] 명확한 일치
    - [ ] etc.
  - [ ] **엣지 케이스**
    - [ ] 선행기술이 없음 (리스트가 비어있음) → 신규성 있음
    - [ ] 선행기술이 1개만 있음
    - [ ] 선행기술이 100개 이상

- [ ] **Integration 테스트**
  - [ ] KnowledgeBase에서 선행기술 검색 후 평가
  - [ ] 벡터 임베딩을 이용한 유사도 계산 검증

- [ ] **E2E 테스트**
  - [ ] 청구항 입력 → KB 검색 → 신규성 평가 → 결과 반환

---

## 4. 테스트 실행 방법

### 4.1 전체 테스트 실행

```bash
# 가상환경 활성화
source dev_env/bin/activate

# 모든 테스트 실행 (verbose 모드)
pytest tests/ -v

# 커버리지 리포트 포함
pytest tests/ --cov=src --cov-report=html

# 특정 테스트 파일만 실행
pytest tests/test_civil_law_vocabulary.py -v

# 특정 테스트 함수만 실행
pytest tests/test_civil_law_vocabulary.py::test_statute_creation -v
```

### 4.2 테스트 그룹별 실행

```bash
# Unit 테스트만 실행
pytest tests/ -m unit -v

# Integration 테스트만 실행
pytest tests/ -m integration -v

# E2E 테스트만 실행
pytest tests/ -m e2e -v
```

### 4.3 pytest 설정 파일

```ini
# pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    edge_case: Edge case tests
```

---

## 5. 엣지 케이스 & 유즈 케이스 매트릭스

### 5.1 Civil Law Vocabulary 엣지 케이스

| 엣지 케이스 | 입력 | 예상 출력 | 테스트 함수 |
|-----------|------|---------|-----------|
| 빈 리스트 | `requirements=[]` | ValueError 또는 빈 리스트 허용 | `test_empty_requirements` |
| None 값 | `title=None` | ValueError | `test_none_title` |
| 중복 | `requirements=["A", "A"]` | 자동 중복 제거 또는 경고 | `test_duplicate_requirements` |
| 특수 문자 | `title="제①조"` | 정상 처리 | `test_special_characters` |
| 매우 긴 문자열 | `title="X" * 10000` | 정상 또는 길이 제한 | `test_very_long_title` |

### 5.2 Patent Law Vocabulary 엣지 케이스

| 엣지 케이스 | 입력 | 예상 출력 | 테스트 함수 |
|-----------|------|---------|-----------|
| 청구항 번호 0 | `claim_number=0` | ValueError | `test_claim_number_zero` |
| 음수 청구항 | `claim_number=-1` | ValueError | `test_negative_claim_number` |
| 순환 참조 | `A→B→C→A` | ValueError | `test_circular_reference` |
| 요소 100개+ | `elements=[...]*100` | 정상 또는 경고 | `test_many_elements` |
| 존재하지 않는 종속 | `claims_back_to=999` | ValueError | `test_invalid_back_reference` |

### 5.3 유즈 케이스

#### Use Case 1: 전형적인 특허 청구항 작성

```
Actor: 출원인 (변리사)
Trigger: 새로운 발명에 대한 특허 출원
Flow:
1. 출원인이 청구항 1을 작성한다
2. 시스템이 문법을 검증한다 (ClaimGrammar)
3. 시스템이 선행기술을 검색한다 (KnowledgeBase)
4. 시스템이 신규성과 진보성을 평가한다 (LogicEngine)
5. 시스템이 결과를 출력한다
Result: 청구항의 유효성 판정 결과 표시
```

#### Use Case 2: 심사관의 거절 이유에 대한 대응

```
Actor: 출원인
Trigger: 심사관의 거절 이유 접수
Flow:
1. 출원인이 거절 이유를 읽는다
2. 출원인이 청구항을 수정한다
3. 시스템이 수정된 청구항을 평가한다
4. 시스템이 개선도를 보여준다
Result: 개선된 청구항이 통과 가능성 증가
```

---

## 6. 테스트 자동화 (CI/CD)

### 6.1 GitHub Actions 워크플로우

```yaml
# .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: 3.12

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run Unit Tests
      run: pytest tests/ -m unit -v

    - name: Run Integration Tests
      run: pytest tests/ -m integration -v

    - name: Generate Coverage Report
      run: pytest tests/ --cov=src --cov-report=xml

    - name: Upload Coverage
      uses: codecov/codecov-action@v3
```

---

## 7. 테스트 체크리스트 (개발자용)

각 Phase를 시작하기 전에 이 체크리스트를 확인하세요:

### 코드 작성 전
- [ ] 테스트 케이스 목록 작성 (test_*.md)
- [ ] 엣지 케이스 식별 및 문서화
- [ ] DOD 명확히 이해

### 코드 작성 중
- [ ] Red → Green → Refactor 사이클 반복
- [ ] 각 함수마다 최소 3개의 테스트 작성
- [ ] 엣지 케이스 테스트 포함

### 코드 작성 후
- [ ] `pytest tests/ -v` 통과
- [ ] `pytest tests/ --cov=src` 커버리지 ≥ 95%
- [ ] `black src/` 코드 포맷
- [ ] `mypy src/` 타입 체크 통과
- [ ] DOD 체크리스트 모두 완료

---

## 8. 메트릭 추적

### 8.1 추적할 메트릭

```python
# metrics.json (매주 업데이트)
{
    "phase": "1-1",
    "test_coverage": 0.95,
    "test_count": 45,
    "edge_case_coverage": 0.90,
    "code_quality": {
        "cyclomatic_complexity": 3.2,
        "average_function_length": 25,
        "pep8_violations": 0
    },
    "performance": {
        "unit_test_duration_ms": 150,
        "integration_test_duration_ms": 300
    }
}
```

### 8.2 성공 기준

| 메트릭 | 목표 | 검사 방법 |
|--------|------|---------|
| **테스트 커버리지** | ≥ 95% | `pytest --cov` |
| **테스트 개수** | Phase별 30개 이상 | `pytest --collect-only` |
| **엣지 케이스** | 각 함수마다 최소 2개 | 수동 검증 |
| **Code Quality** | Complexity < 5 | `radon cc` |
| **PEP 8** | 위반 0개 | `black --check` |
| **Type Hints** | 100% | `mypy --strict` |

---

## 다음 단계

1. **이 문서 읽기 및 이해** (필수!)
2. **pytest 설정 파일 작성** (`pytest.ini`)
3. **첫 테스트 케이스 명세서 작성** (`TESTING_SPECIFICATIONS.md`)
4. **Phase 1-1 테스트 코드 작성** (테스트-주도 개발)
5. **Phase 1-1 구현 코드 작성** (테스트를 통과하도록)
6. **DOD 체크리스트 완료 확인**
7. **다음 Phase로 진행**

> **기억하세요**: 테스트 없는 코드는 완성된 코드가 아닙니다!
