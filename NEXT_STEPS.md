# 다음 단계: 실제 코딩 시작하기

## 📋 지금까지 완료한 것

### ✅ 문서화 완료
- [x] 프로젝트 아키텍처 (8개 문서)
- [x] DSL 철학
- [x] 테스트 전략 및 DOD
- [x] Phase 1-1 상세 테스트 명세서
- [x] 구현 로드맵 (12주)

### ✅ 개발 환경 준비
- [x] 가상환경 생성 (dev_env/)
- [x] requirements.txt 작성
- [x] pytest.ini 설정
- [x] .gitignore 설정

### ✅ 버전 관리
- [x] Git 초기화 및 커밋 이력 정리
- [x] 모든 문서 커밋 및 푸시

---

## 🚀 이제 시작할 것: Phase 1-1 구현

### Step 1: 가상환경 활성화

```bash
cd /mnt/d/progress/The-First-Claim
source dev_env/bin/activate
```

### Step 2: 프로젝트 구조 확인

```bash
tree src/ -L 2
```

예상 결과:
```
src/
├── dsl/
│   ├── vocabulary/
│   │   ├── __init__.py
│   │   └── civil_law.py (← 지금 작성할 파일)
│   ├── grammar/
│   └── __init__.py
├── logic_engine/
├── knowledge_base/
├── ui/
├── learning/
└── main.py
```

### Step 3: Phase 1-1 구현 순서

#### 3-1. 테스트 파일 먼저 작성 (TDD!)

```bash
# tests/test_civil_law_vocabulary.py 파일 생성
# TEST_SPECIFICATIONS_PHASE_1_1.md의 테스트 코드를 여기에 복사-붙여넣기
```

**핵심**: 테스트를 먼저 쓴다!

#### 3-2. 구현 코드 작성

```bash
# src/dsl/vocabulary/civil_law.py 파일 생성
# 다음 클래스들을 구현:
# - CivilLawStatute
# - Person
# - Transaction
# - LegalRight
```

**순서**:
1. 클래스 틀 정의 (pass만)
2. 테스트 실행 → 모두 실패 (Red)
3. 코드 구현 → 테스트 통과 (Green)
4. 코드 정리 → 테스트 여전히 통과 (Refactor)
5. 다음 클래스로

#### 3-3. 테스트 실행 및 검증

```bash
# 테스트 실행
pytest tests/test_civil_law_vocabulary.py -v

# 커버리지 확인
pytest tests/test_civil_law_vocabulary.py --cov=src.dsl.vocabulary.civil_law --cov-report=term

# PEP 8 검사
black src/dsl/vocabulary/ --check

# 타입 체크
mypy src/dsl/vocabulary/ --strict
```

---

## 📝 실제 코드 예시: CivilLawStatute 구현

### Step 1: 테스트 코드 먼저 (test_civil_law_vocabulary.py)

```python
# tests/test_civil_law_vocabulary.py

import pytest
from src.dsl.vocabulary.civil_law import CivilLawStatute

class TestCivilLawStatute:
    @pytest.mark.unit
    def test_valid_statute_creation(self):
        """U1-1: 정상 생성"""
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["독창성"],
            effects=["복제권"],
        )
        assert statute.statute_number == "제145조"
        assert statute.title == "저작권자의 권리"
```

### Step 2: 구현 코드 (civil_law.py)

```python
# src/dsl/vocabulary/civil_law.py

from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class CivilLawStatute:
    """민법 조문"""
    statute_number: str
    title: str
    requirements: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    related_precedents: List[str] = field(default_factory=list)

    def __post_init__(self):
        """유효성 검증"""
        if not self.statute_number or not isinstance(self.statute_number, str):
            raise ValueError("statute_number은 비어있지 않은 문자열이어야 합니다")
        if not self.title or not isinstance(self.title, str):
            raise ValueError("title은 비어있지 않은 문자열이어야 합니다")

        # 중복 제거
        self.requirements = list(dict.fromkeys(self.requirements))
        self.effects = list(dict.fromkeys(self.effects))
```

---

## 📊 진행 추적

### 주간 체크리스트

```
Week 1-1 (Phase 1-1: Civil Law Vocabulary):
- [ ] Day 1: 문서 읽고 이해하기
- [ ] Day 2: test_civil_law_vocabulary.py 파일 생성 및 테스트 코드 작성
- [ ] Day 3: civil_law.py 파일 생성 및 CivilLawStatute 구현
- [ ] Day 4: Person, Transaction, LegalRight 클래스 구현
- [ ] Day 5: 모든 테스트 통과 확인 + 커버리지 95% 이상
- [ ] Day 6: Code quality 체크 (black, mypy, pytest)
- [ ] Day 7: DOD 체크리스트 완료 확인 + 커밋 및 푸시

✅ Week 1-1 완료!
```

---

## ⚡ 빠른 시작 스크립트

Phase 1-1을 시작하기 위해 한 번에 실행할 수 있는 스크립트:

```bash
#!/bin/bash

# 1. 가상환경 활성화
source dev_env/bin/activate

# 2. 필수 파일 생성
touch src/dsl/vocabulary/__init__.py
touch src/dsl/__init__.py
touch tests/test_civil_law_vocabulary.py

# 3. 테스트 틀 생성 (아래 코드를 tests/test_civil_law_vocabulary.py에 붙여넣기)
cat > tests/test_civil_law_vocabulary.py << 'EOF'
import pytest
from src.dsl.vocabulary.civil_law import CivilLawStatute, Person, Transaction, LegalRight

# TEST_SPECIFICATIONS_PHASE_1_1.md의 코드를 여기에 붙여넣기
EOF

# 4. 구현 파일 생성
cat > src/dsl/vocabulary/civil_law.py << 'EOF'
from typing import List
from dataclasses import dataclass, field

@dataclass
class CivilLawStatute:
    """민법 조문"""
    statute_number: str
    title: str
    requirements: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    related_precedents: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.statute_number:
            raise ValueError("statute_number은 필수입니다")
        if not self.title:
            raise ValueError("title은 필수입니다")

# 나머지 클래스들...
EOF

# 5. 첫 테스트 실행
pytest tests/test_civil_law_vocabulary.py -v

echo "✅ Phase 1-1 준비 완료!"
```

---

## 🎯 성공의 정의 (Phase 1-1 완료)

다음을 모두 만족하면 Phase 1-1이 완료된 것입니다:

```bash
# 1. 모든 테스트 통과
pytest tests/test_civil_law_vocabulary.py -v
# 결과: ====== 20 passed in 0.XX s ======

# 2. 커버리지 95% 이상
pytest tests/test_civil_law_vocabulary.py --cov=src.dsl.vocabulary.civil_law --cov-report=term
# 결과: Name Stmts Miss Cover
#      civil_law.py    XX    1   95%

# 3. PEP 8 준수
black src/dsl/vocabulary/ --check
# 결과: All done! ✨

# 4. 타입 체크 통과
mypy src/dsl/vocabulary/ --strict
# 결과: Success: no issues found

# 5. 깃 커밋
git add src/dsl/vocabulary/civil_law.py tests/test_civil_law_vocabulary.py
git commit -m "Implement Phase 1-1: Civil Law Vocabulary"
git push origin master
```

---

## 💡 주의사항

### ❌ 하지 말아야 할 것
- 테스트 없이 코드 작성하기 ❌
- DOD를 무시하고 넘어가기 ❌
- 커버리지 95% 미만으로 커밋하기 ❌
- 타입 힌팅 없이 코드 작성하기 ❌
- Docstring 없이 함수 정의하기 ❌

### ✅ 반드시 해야 할 것
- 먼저 테스트 코드 작성 (Red) ✅
- 그 다음 구현 (Green) ✅
- 마지막에 리팩토링 (Refactor) ✅
- 매일 커밋 ✅
- 주마다 DOD 확인 ✅

---

## 📞 막혔을 때 확인할 것

### 테스트가 실패할 때
1. 테스트 코드가 올바른가?
2. 구현이 테스트 조건을 모두 만족하는가?
3. 엣지 케이스가 처리되었는가?

### 커버리지가 95% 미만일 때
1. 테스트되지 않은 코드를 찾기 (--cov-report=html)
2. 해당 코드를 테스트하는 케이스 추가
3. 또는 불필요한 코드 제거

### 타입 에러가 있을 때
1. 함수 인자에 타입 힌팅 추가
2. 반환값에 타입 힌팅 추가
3. mypy 오류 메시지 읽고 수정

---

## 🎓 학습 자료

추천 읽을거리:
1. TESTING_STRATEGY.md - 전체 테스트 전략
2. TEST_SPECIFICATIONS_PHASE_1_1.md - 구체적인 테스트 케이스
3. 08_dsl_design_philosophy.md - DSL 철학

추천 영상:
- "Test-Driven Development" - Robert C. Martin
- "pytest Tutorial" - Real Python

---

## 🚀 다음 Phase 일정

- **Phase 1-1 완료 후**: Phase 1-2 (Patent Law Vocabulary) 시작
- **Week 2-3**: Phase 2 (DSL Grammar)
- **Week 4-7**: Phase 3 (Logic Engine)
- **Week 8-9**: Phase 4 (UI)
- **Week 10-12**: Phase 5 (Feedback Loop) + 최종 테스트

---

**지금 바로 시작하세요!**

```bash
source dev_env/bin/activate
pytest tests/test_civil_law_vocabulary.py -v
```

행운을 빕니다! 🍀
