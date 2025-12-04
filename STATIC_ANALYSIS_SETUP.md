# Python Static Analysis Setup

**Date:** 2025-12-04
**Status:** ✅ Configured

---

## 📋 Overview

Python 정적 분석 도구 3가지를 설정하고 GitHub Actions CI 파이프라인에 통합했습니다.

---

## 🔧 Tools Configured

### 1. **Flake8** - Code Style & Quality
**파일:** `.flake8`

```ini
max-line-length = 100
ignore = E203, E266, W503, W504
```

**검사 항목:**
- Line length (E501)
- Whitespace issues (W293)
- Unused imports (F401)
- Undefined names (F821)
- Syntax errors

**현재 상태:**
```
src/ 파일 분석 결과:
- 총 100개 문제 발견
  - 53개: Line too long (E501)
  - 26개: Blank line contains whitespace (W293)
  - 12개: Unused imports (F401)
  - 8개: Missing placeholders in f-string (F541)
  - 1개: Module level import not at top (E402)
```

**설정:**
- max-line-length: 100자 (기본 79자보다 느슨함)
- __pycache__, .pytest_cache, .hypothesis 제외
- __init__.py의 미사용 import 무시 (F401)

### 2. **Pylint** - Code Analysis & Best Practices
**파일:** `pylintrc`

```ini
py-version = 3.10
disable = all
enable = E, F
```

**검사 항목:**
- Errors (E): 심각한 오류
- Fatal errors (F): 문법 오류, 비정의 변수
- Warnings (W): 경고 (selective)

**설정:**
- 에러 및 fatal 문제만 검사
- max-nested-blocks: 5
- max-args: 5
- max-attributes: 7
- max-statements: 50

**실행:**
```bash
pylint src/ --rcfile=pylintrc --disable=all --enable=E,F
```

### 3. **Mypy** - Type Checking
**파일:** `mypy.ini`

```ini
python_version = 3.10
check_untyped_defs = True
no_implicit_optional = True
strict_optional = True
```

**검사 항목:**
- Type annotations 검증
- Optional type handling
- Return type consistency
- Function signature matching

**설정:**
- warn_return_any: True
- warn_unused_configs: True
- warn_redundant_casts: True
- tests/ 디렉토리 제외

---

## 🔄 GitHub Actions Integration

### test.yml에 추가된 단계

```yaml
jobs:
  backend-unit-tests:
    steps:
      - name: Lint with flake8
        run: flake8 src/ --count --statistics

      - name: Lint with pylint
        run: pylint src/ --rcfile=pylintrc --disable=all --enable=E,F

      - name: Type check with mypy
        run: mypy src/ --config-file=mypy.ini

      - name: Run unit tests
        run: pytest tests/ --cov=src
```

**특징:**
- 모든 linting은 `continue-on-error: true`
- 실패해도 파이프라인 진행 가능
- 문제 리포트는 로그에 기록
- 실제 테스트는 실패하면 중단

---

## 📊 Current Issues

### Flake8 (100개 문제)

| 코드 | 설명 | 수량 | 심각도 |
|------|------|------|--------|
| E501 | Line too long | 53 | 낮음 |
| W293 | Blank line whitespace | 26 | 매우낮음 |
| F401 | Unused import | 12 | 낮음 |
| F541 | Missing f-string placeholder | 8 | 중간 |
| E402 | Module import not at top | 1 | 낮음 |

**권장사항:**
- E501: max-line-length를 100으로 설정 ✅ (이미 설정됨)
- W293: 자동 포매팅으로 제거 가능 (black 사용)
- F401: 테스트 파일은 무시, src는 정리 필요
- F541: f-string 리터럴 수정 필요

### Pylint
- 현재 E, F만 검사 (경고는 무시)
- 대부분 통과 예상

### Mypy
- Type annotations 없는 레거시 코드
- 현재 주요 에러 없음 (예상)

---

## 🛠️ 개선 계획

### Phase 1: 즉시 (1일)
```bash
# 자동 포매팅으로 일부 문제 해결
black src/        # 자동 포매팅
isort src/        # import 정렬

# 결과: W293, E501 일부 해결
```

### Phase 2: 단기 (1주)
- [ ] F401 미사용 import 정리
- [ ] F541 f-string 수정
- [ ] 주요 F821 (undefined name) 수정

### Phase 3: 중기 (2주)
- [ ] Type hints 추가
- [ ] Mypy strict mode 점진적 활성화
- [ ] Pylint 경고 레벨 추가

### Phase 4: 장기 (1달)
- [ ] 100% Pylint 통과
- [ ] 95% Mypy 통과
- [ ] Type coverage 70% 이상

---

## 🚀 Local Usage

### Flake8
```bash
# 모든 파일 검사
flake8 src/

# 설정 파일 사용
flake8 src/ --config=.flake8

# 통계 표시
flake8 src/ --count --statistics

# 특정 에러만 보기
flake8 src/ --select=E501,W293
```

### Pylint
```bash
# 기본 검사
pylint src/

# 설정 파일 사용
pylint src/ --rcfile=pylintrc

# 특정 파일
pylint src/ui/game.py

# JSON 출력
pylint src/ --output-format=json > report.json
```

### Mypy
```bash
# 기본 검사
mypy src/

# 설정 파일 사용
mypy src/ --config-file=mypy.ini

# 특정 파일
mypy src/ui/game.py

# 진행도 표시
mypy src/ --follow-imports=silent --html htmlreport
```

### Black & Isort (자동 포매팅)
```bash
# Black으로 포매팅
black src/

# Isort로 import 정렬
isort src/

# 함께 사용
isort src/ && black src/

# 변경사항 확인만 (변경 안 함)
black --check src/
```

---

## 📋 Configuration Files

### .flake8
```ini
[flake8]
max-line-length = 100
ignore = E203, E266, W503, W504
exclude = .git, __pycache__, .venv, .pytest_cache, .hypothesis
per-file-ignores =
    __init__.py:F401
    tests/*:F401,F811
```

### pylintrc
```ini
[MASTER]
py-version = 3.10

[MESSAGES CONTROL]
disable = all
enable = E, F

[DESIGN]
max-args = 5
max-attributes = 7
max-statements = 50
```

### mypy.ini
```ini
[mypy]
python_version = 3.10
check_untyped_defs = True
no_implicit_optional = True

[mypy-tests.*]
ignore_errors = True
```

---

## ✅ Checklist

- [x] Flake8 설정 (.flake8)
- [x] Pylint 설정 (pylintrc)
- [x] Mypy 설정 (mypy.ini)
- [x] GitHub Actions에 통합
- [x] 설정 문서화
- [ ] 로컬 개발자 가이드
- [ ] CI 파이프라인 테스트
- [ ] 주기적 개선 계획

---

## 📖 참고자료

### 공식 문서
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)

### 커뮤니티 가이드
- PEP 8 - Style Guide for Python Code
- PEP 484 - Type Hints
- PEP 526 - Syntax for Variable Annotations

---

**Status:** 🟢 Setup Complete, Ready for Local Testing
**Next Step:** GitHub Actions 검증 및 자동 포매팅 실행

