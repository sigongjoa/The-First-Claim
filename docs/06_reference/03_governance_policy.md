# PROJECT: OVERRIDE - AI 거버넌스 정책 및 안전 가이드라인

**작성일**: 2025-12-07 | **버전**: 1.0 | **상태**: 활성

---

## 📋 목적

이 정책 문서는 PROJECT: OVERRIDE 프로젝트에서 AI(LLM)를 활용하여 코드를 생성할 때 준수해야 할 **안전 기준, 보안 요구사항, 품질 표준**을 정의합니다.

특히 다음을 방지합니다:
- ❌ 패키지 환각 (존재하지 않는 라이브러리 임포트)
- ❌ 하드코딩된 자격증명 (API 키, 비밀번호)
- ❌ 취약한 암호화 또는 검증 로직
- ❌ 동어반복적 테스트 (Tautological Test)
- ❌ 비효율적 알고리즘

---

## Step 0: 프롬프트 엔지니어링 & AI 거버넌스

### 0.1 시스템 프롬프트 (System Prompt)

모든 AI 코드 생성 요청은 다음의 **기본 컨텍스트**를 포함해야 합니다:

```
당신은 PROJECT: OVERRIDE의 숙련된 파이썬 개발자입니다.

## 필수 규칙:

1. 코딩 표준
   - PEP 8 준수
   - 타입 힌팅 필수 (Python 3.10+ 타입 어노테이션)
   - 최대 100자 라인 길이
   - 함수마다 docstring 포함 (Google 스타일)

2. 보안 요구사항
   - 환경 변수에서만 민감 정보 읽기 (하드코딩 금지)
   - 암호화는 cryptography 라이브러리 사용 (커스텀 암호화 금지)
   - SQL/NoSQL 쿼리는 반드시 매개변수화 (parameterized)
   - 입력값 검증 필수

3. 의존성 관리
   - 모든 임포트는 requirements.txt에 명시된 패키지만 사용
   - 임포트 전에 패키지 실재 확인 (예: "pip list | grep package_name")
   - 커뮤니티 평판이 높은 패키지만 제안 (GitHub 스타 1000+, 유지보수 활발)

4. 테스트 코드 작성
   - 각 함수마다 최소 3개의 테스트 케이스
   - 정상 케이스, 경계 케이스, 에러 케이스 포함
   - Mock을 사용하여 외부 의존성 차단
   - 테스트는 구현과 독립적으로 작성 (구현 로직 복사 금지)

5. 성능 최적화
   - 시간 복잡도를 O(n²)보다 나아야 함
   - 불필요한 데이터 복사 방지
   - 반복문에서 list append 대신 list comprehension 사용

## 생성하는 모든 코드에 대해:

- 함수의 핵심 로직을 한 문장으로 설명하세요
- 예상되는 시간 복잡도를 명시하세요
- 테스트 케이스에서 제시된 입력값이 기존 로직을 "따라가지 않는" 것을 확인하세요
- 엣지 케이스(null, 음수, 빈 문자열, 매우 큰 수) 처리를 명시하세요
```

### 0.2 AI 제약 조건 (Constraints)

AI가 코드를 생성할 때 반드시 따를 **부정적 제약**:

| 금지 항목 | 예시 | 대신 사용 |
|----------|------|----------|
| 하드코딩된 자격증명 | `api_key = "sk-..."` | `os.getenv("OPENAI_API_KEY")` |
| 존재하지 않는 라이브러리 | `import fake_lib` | requirements.txt 확인 후 사용 |
| 커스텀 암호화 | `def encrypt(msg): return msg[::-1]` | `from cryptography.fernet import Fernet` |
| 동적 SQL | `f"SELECT * FROM {table}"` | `"SELECT * FROM table WHERE id = %s"` + params |
| 무한 재귀 | `def f(x): return f(x-1)` | base case 포함 또는 반복문 |
| 전역 변수 의존 | `x = 0; def f(): return x` | 함수 매개변수로 전달 |
| 예외 무시 | `try: ... except: pass` | 구체적 예외 처리 |

### 0.3 AI 코드 검수 체크리스트 (Code Review Checklist)

AI가 생성한 코드를 인간이 검토할 때 확인할 항목:

```
보안 검사
☐ 하드코딩된 비밀번호, API 키 없음?
☐ 모든 사용자 입력이 검증되는가?
☐ SQL/명령 실행은 매개변수화되었는가?
☐ 비밀이 로그에 출력되지 않는가?

의존성 검사
☐ 모든 임포트가 requirements.txt에 있는가?
☐ 존재하지 않는 패키지는 없는가?
☐ 버전 충돌은 없는가?

테스트 검사
☐ 테스트가 구현을 "따라가지 않는가"? (독립적인가?)
☐ 정상/경계/에러 케이스가 모두 있는가?
☐ Mock이 적절히 사용되었는가?

성능 검사
☐ O(n²) 이상의 나쁜 알고리즘이 있는가?
☐ 불필요한 루프나 재귀가 있는가?
☐ 메모리 누수 위험이 있는가?

코드 품질
☐ PEP 8 준수하는가?
☐ 함수명과 변수명이 명확한가?
☐ 너무 긴 함수는 없는가? (20줄 이상?)
☐ Docstring이 있는가?
```

### 0.4 특화된 지침: RAG 및 벡터 DB 코드

AI가 벡터 데이터베이스나 LLM을 활용하는 코드를 작성할 때:

```
프롬프트 인젝션 방지
☐ 사용자 입력이 LLM 프롬프트에 직접 삽입되지 않음
☐ 사용자 입력을 마크다운으로 감싸기 (```...```)
☐ 민감한 시스템 프롬프트를 숨김

벡터 DB 보안
☐ 벡터 DB 액세스는 인증으로 보호됨
☐ 민감한 문서는 암호화되어 저장됨
☐ 검색 결과가 사용자의 권한 범위 내인지 확인

RAG 정확성
☐ 검색된 문서가 실제로 관련 있는지 확인
☐ 신뢰도 점수가 임계값 이상인지 확인
☐ 할루시네이션을 감지하기 위한 정합성 검사
```

---

## Step 1: 심층 코드 검증 - 프로세스

### 1.1 패키지 환각 감지

**목표**: AI가 생성한 코드가 존재하지 않는 라이브러리를 사용하지 않도록 강제

**구현**:

```python
# ci/validate_imports.py
import ast
import subprocess
import sys

def check_imports_exist(file_path):
    """
    파이썬 파일의 모든 import을 파싱하여
    해당 패키지가 실제로 설치되어 있는지 확인
    """
    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    installed = set(x.split('==')[0].lower()
                   for x in subprocess.check_output(
                       [sys.executable, '-m', 'pip', 'list']
                   ).decode().split('\n')[2:])

    missing = imports - installed - {'builtins', '__future__'}

    if missing:
        print(f"❌ 설치되지 않은 패키지: {missing}")
        return False

    return True
```

**CI 파이프라인에 통합**:

```yaml
# .github/workflows/validate.yml
name: Validate AI Generated Code

on: [pull_request]

jobs:
  check-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: |
          for file in $(find src -name "*.py"); do
            python ci/validate_imports.py "$file" || exit 1
          done
```

### 1.2 비밀 스캔 강화

**목표**: 하드코딩된 API 키, 비밀번호, 토큰 감지

**사용 도구**: TruffleHog (Python) 또는 Pre-commit hook

```python
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.70.0
    hooks:
      - id: trufflehog
        name: TruffleHog Secret Scan
        entry: trufflehog filesystem . --json
        language: system
        types: [python]
        pass_filenames: false
```

### 1.3 돌연변이 테스트 (Mutation Testing)

**목표**: 테스트 코드 자체의 품질 검증 (코드를 망가뜨렸을 때 테스트가 실패하는가?)

**도구**: Mutmut (Python)

```bash
# 설치
pip install mutmut

# 실행
mutmut run --paths-to-mutate=src/ --tests-dir=tests/

# 결과
# Mutmut은 다음을 리포트함:
# - Killed: 테스트가 잡아낸 결함
# - Survived: 테스트가 놓친 결함
# - Skipped: 분석 불가능한 결함
```

**목표**: **Mutation Score ≥ 85%** (전체 결함의 85% 이상을 테스트가 감지)

현재 프로젝트:
```
기존 Code Coverage: 95%
예상 Mutation Score: 60-70% (예상치)
→ 테스트 코드 개선 필요
```

---

## Step 2-3: 적대적 시스템 테스트

### 2.1 생성형 퍼징 (Generative Fuzzing)

**목표**: 예상치 못한 입력값으로 시스템 붕괴 유도

**도구**: Hypothesis (Python)

```python
# tests/test_fuzz_vector_db.py
from hypothesis import given, strategies as st, settings, HealthCheck
from src.knowledge_base.vector_database import MemoryVectorDatabase

@given(
    statute_number=st.text(min_size=1, max_size=100),
    title=st.text(min_size=1, max_size=500),
    content=st.text(min_size=0, max_size=10000)
)
@settings(
    max_examples=10000,  # 10,000개 무작위 입력값 테스트
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None
)
def test_add_statute_robustness(statute_number, title, content):
    """
    Vector DB가 어떤 입력값이 와도
    크래시하지 않는지 검증
    """
    db = MemoryVectorDatabase()

    try:
        db.add_statute(
            statute_id=f"test_{statute_number}",
            statute_number=statute_number,
            title=title,
            content=content,
            source_type="civil_law"
        )
        # 추가 후에도 정상 상태 유지
        assert len(db.vectors) > 0
    except (ValueError, TypeError) as e:
        # 명시적인 검증 실패는 OK
        # 하지만 의도하지 않은 크래시는 X
        pass
```

### 2.2 메타모픽 테스트 (Metamorphic Testing)

**목표**: 정답이 정확하지 않아도 "관계(Relation)"는 유지되는가?

```python
# tests/test_metamorphic_rag.py
def test_rag_consistency_under_input_transformation():
    """
    쿼리를 변형해도 결과의 '핵심'은 같아야 함
    """
    rag = get_rag_system()

    # 원본 쿼리
    query1 = "20년 동안 토지를 점유했을 때 소유권을 취득할 수 있는가?"
    response1 = rag.query(query1)

    # 변형된 쿼리 (문장 순서 바꿈)
    query2 = "소유권을 취득할 수 있는가? 20년 동안 토지를 점유했을 때"
    response2 = rag.query(query2)

    # 관계 검증:
    # 1. 같은 소스가 인용되어야 함
    assert response1.sources == response2.sources, \
        f"소스가 다름: {response1.sources} vs {response2.sources}"

    # 2. 신뢰도가 비슷해야 함 (±10%)
    assert abs(response1.confidence - response2.confidence) < 0.1, \
        f"신뢰도 편차: {response1.confidence} vs {response2.confidence}"

    # 3. 핵심 키워드가 모두 포함되어야 함
    keywords = {"취득시효", "점유", "소유권"}
    assert keywords <= set(response1.answer.split()), \
        "핵심 키워드 누락"
    assert keywords <= set(response2.answer.split()), \
        "핵심 키워드 누락"
```

---

## Step 4-7: 배포 및 운영 거버넌스

### 4.1 정책 코드화 (Policy-as-Code)

**도구**: Open Policy Agent (OPA)

```rego
# policies/security.rego
package kubernetes

deny[msg] {
    container := input.spec.containers[_]
    container.securityContext.runAsUser == 0
    msg := sprintf("Container '%v' runs as root (UID 0)", [container.name])
}

deny[msg] {
    not input.spec.securityContext.fsReadOnlyRootFilesystem
    msg := "Root filesystem must be read-only"
}

deny[msg] {
    secret_env := input.spec.containers[_].env[_]
    secret_env.valueFrom.secretKeyRef
    not secret_env.name
    msg := sprintf("Missing env var name for secret", [])
}
```

**CI에서 강제**:

```yaml
- name: Policy Check
  run: |
    opa eval -d policies/ "data.kubernetes.deny" -i <(cat infra.json)
```

### 4.2 카오스 엔지니어링 테스트

**목표**: 운영 중 장애가 발생해도 자동 복구되는가?

```python
# tests/test_chaos_resilience.py
import random
from unittest.mock import patch

def test_api_resilience_to_vector_db_failure():
    """
    Vector DB가 다운되어도 API가 graceful하게 처리하는가?
    """
    # Vector DB를 임의로 차단
    with patch('src.api.server.get_vector_database') as mock_vdb:
        mock_vdb.side_effect = ConnectionError("DB unavailable")

        from src.api.server import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get(
            "/api/search",
            params={"query": "테스트"}
        )

        # 503 Service Unavailable을 반환해야 함
        # 500 Internal Server Error가 아니라
        assert response.status_code in [503, 504]
        assert "unavailable" in response.json().get("detail", "").lower()
```

---

## 📊 거버넌스 구현 로드맵

```
Week 1: Step 0 거버넌스
├─ ✅ 이 문서 작성 (완료)
├─ ⏳ 프롬프트 템플릿 준비
├─ ⏳ 코딩 컨벤션 자동화 (Black, MyPy)
└─ ⏳ 체크리스트 문서화

Week 2: Step 1 심층 검증
├─ ⏳ 패키지 환각 감지 (validate_imports.py)
├─ ⏳ 비밀 스캔 강화 (TruffleHog)
├─ ⏳ 돌연변이 테스트 (Mutmut)
└─ ⏳ 결과 리포트: Mutation Score 측정

Week 3: Step 2-3 적대적 테스트
├─ ⏳ 생성형 퍼징 (Hypothesis)
├─ ⏳ 메타모픽 테스트 작성
└─ ⏳ 엣지 케이스 자동 탐색

Week 4: Step 4-7 운영
├─ ⏳ OPA 정책 코드화
├─ ⏳ 카오스 엔지니어링
└─ ⏳ AIOps 모니터링 설정
```

---

## 참고 자료

- [PEP 8 - Python 스타일 가이드](https://pep8.org)
- [OWASP Top 10 - 보안 취약점](https://owasp.org/www-project-top-ten/)
- [TruffleHog - 비밀 스캔](https://github.com/trufflesecurity/trufflehog)
- [Mutmut - 돌연변이 테스트](https://mutmut.readthedocs.io)
- [Hypothesis - 생성형 퍼징](https://hypothesis.readthedocs.io)
- [OPA - 정책 코드화](https://www.openpolicyagent.org)

---

**버전 히스토리**

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0 | 2025-12-07 | 초안 작성 |

**승인자**: PROJECT: OVERRIDE 팀
**다음 검토**: 2025-12-14
