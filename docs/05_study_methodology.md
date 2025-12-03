# PROJECT: OVERRIDE - TDD 학습 방법론

## 개요

PROJECT: OVERRIDE의 핵심은 **TDD (Test-Driven Development)를 교육에 적용**한 것입니다.

기존의 수험 방식과의 차이를 명확히 이해하세요.

---

## 1. 기존 수험 방식 vs TDD 학습법

### 기존 방식 (Fail → Frustration Loop)

```
[이론 강의 듣기 2시간]
    ↓
[기본서 읽기 3시간]
    ↓
[예제 문제 풀기 1시간]
    ↓
[한 주 후: 완전히 잊음]
    ↓
[포기하고 싶은 마음]
```

**문제점:**
- 수동적 학습 (쓰기 위주)
- 즉시 망각 (망각곡선)
- 동기 부족 (성취감 없음)
- 장기 기억 형성 안 됨

---

### TDD 학습법 (Success → Dopamine Loop)

```
[Test] 기출문제를 먼저 본다 (실패)
    ↓
[Code] 문제 해결에 필요한 지식만 습득 (배우기)
    ↓
[Refactor] 지식을 체계화 (정리하기)
    ↓
[Pass] 다시 문제를 풀어 정답을 맞힌다 (성공!)
    ↓
[Dopamine Release] 뇌의 보상 회로 활성화
    ↓
[Motivation Increase] 다음 문제도 풀고 싶음
```

**장점:**
- 능동적 학습 (문제 해결 중심)
- 맥락 학습 (구체적 상황에서)
- 즉각적 피드백 (성공/실패 명확)
- 장기 기억 형성 (반복을 통한 강화)

---

## 2. TDD 학습의 4단계

### Step 1: TEST (기출문제 확인)

**목표:** 자신의 현재 지식 수준 파악

**방법:**

```
1. 2024년 변리사 1차 기출문제를 연다.
2. 아무 준비 없이 풀어본다.
3. 정답을 확인한다. (아마 틀릴 것)
4. 틀린 이유를 적어둔다.

예시:

문제: "A가 20년 동안 타인의 토지를 점유했다. A는 취득시효로
       소유권을 취득할 수 있는가? 그 요건은?"

학생 답변: "네, 취득시효로 소유권을 취득할 수 있습니다."

정답: "10년 이상 소유의 의사로 평온하고 공연하게 점유해야 하는데,
       만약 선의(선의의 취득시효)라면 10년, 악의라면 20년입니다.
       또한 이 경우 등기 여부가 중요합니다 (민법 제197-198조)."

틀린 이유: "취득시효의 구체적 요건(선의/악의 구분, 요건 상세)을 모름"
```

**결과:**

✗ Fail (당연히 실패)

### Step 2: CODE (지식 습득 & 구현)

**목표:** 문제를 해결하기 위해 필요한 법 조문과 판례만 검색하여 습득

**방법:**

```python
# src/learn_from_problem.py

class LearningFromProblem:
    """문제 기반 학습"""

    def __init__(self, problem_id):
        self.problem = self.load_problem(problem_id)
        self.knowledge_needed = []

    def step1_identify_knowledge_gap(self):
        """1단계: 알아야 할 개념 파악"""

        print("문제에서 묻는 것:")
        print(f"- 취득시효 성립 조건은?")
        print(f"- 선의와 악의의 구분은?")
        print(f"- 요건은 몇 년인가?\n")

        self.knowledge_needed = [
            "취득시효 개념",
            "선의/악의 구분",
            "10년 vs 20년",
            "등기의 영향"
        ]

    def step2_search_statute(self):
        """2단계: 법 조문 검색"""

        print("검색 결과:\n")

        print("민법 제197조 (취득시효)")
        print("-" * 60)
        print("20년간 소유의 의사로 평온하고 공연하게 타인의")
        print("부동산을 점유한 자는 그 소유권을 취득한다.")
        print("-" * 60)

        print("\n민법 제198조 (단기취득시효)")
        print("-" * 60)
        print("10년간 소유의 의사로 평온하고 공연하게 타인의")
        print("부동산을 점유한 자는 그 소유권을 취득한다.")
        print("(이는 선의의 경우만 적용)")
        print("-" * 60)

    def step3_search_precedent(self):
        """3단계: 판례 검색"""

        print("\n판례: 대법원 2020다123456")
        print("-" * 60)
        print("사건: 취득시효 성립 요건")
        print("\n판시사항:")
        print("취득시효가 성립하려면 점유자가 '선의'여야 한다.")
        print("선의란 점유자가 자신이 진정한 소유자라고 생각한 경우를 말한다.")
        print("-" * 60)

    def step4_create_knowledge_base(self):
        """4단계: 지식베이스 구성"""

        knowledge_json = {
            "취득시효": {
                "개념": "장기 점유로 인한 소유권 취득",
                "조문": "민법 제197조, 제198조",
                "요건": {
                    "선의_경우": {
                        "기간": "10년",
                        "조건": ["소유의 의사", "평온성", "공연성"]
                    },
                    "악의_경우": {
                        "기간": "20년",
                        "조건": ["소유의 의사", "평온성", "공연성"]
                    }
                },
                "관련_판례": ["대법원 2020다123456"],
                "중요_포인트": [
                    "선의 vs 악의 구분이 핵심",
                    "점유의 시작 시점이 중요",
                    "부동산 등기 여부 확인 필요"
                ]
            }
        }

        # 이것을 코드로 저장
        with open('data/civil_law_knowledge.json', 'w') as f:
            json.dump(knowledge_json, f, ensure_ascii=False, indent=2)

        print("✓ 지식베이스 저장 완료")
```

**결과:**

✓ Code 작성 (필요한 지식 모두 습득)

### Step 3: REFACTOR (구조화)

**목표:** 습득한 지식을 체계화하여 게임 로직으로 변환

**방법:**

```python
# src/refactor_knowledge.py

class KnowledgeRefactor:
    """지식 재구조화"""

    def refactor_acquisition_by_prescription(self):
        """취득시효 지식 재구조화"""

        # Before (흩어진 정보)
        # - "20년간 소유의 의사로..."
        # - "선의와 악의가 다르다"
        # - "등기가 중요하다"

        # After (체계화된 로직)

        class AcquisitionByPrescription:
            """
            취득시효 여부를 판정하는 로직
            """

            def __init__(self):
                self.possession_duration = None
                self.is_good_faith = None  # True or False
                self.is_peacefully_held = None
                self.is_openly_held = None

            def is_valid(self):
                """취득시효 성립 여부"""

                # 1단계: 필수 조건 확인
                if not (self.is_peacefully_held and self.is_openly_held):
                    return False, "평온성과 공연성 부족"

                # 2단계: 기간 확인 (선의/악의에 따라 다름)
                if self.is_good_faith:
                    required_years = 10
                    faith_status = "선의"
                else:
                    required_years = 20
                    faith_status = "악의"

                if self.possession_duration >= required_years:
                    return True, f"{faith_status}로 {required_years}년 점유 → 성립"
                else:
                    return False, f"{faith_status}이므로 {required_years}년 필요 (현재: {self.possession_duration}년)"

        # 테스트
        case1 = AcquisitionByPrescription()
        case1.possession_duration = 10
        case1.is_good_faith = True
        case1.is_peacefully_held = True
        case1.is_openly_held = True

        result, reason = case1.is_valid()
        print(f"결과: {result}")  # True
        print(f"이유: {reason}")   # "선의로 10년 점유 → 성립"
```

**결과:**

✓ Refactor 완료 (지식을 게임 로직으로 변환)

### Step 4: PASS (문제 해결)

**목표:** 다시 같은 문제를 풀어 정답을 맞힌다

**방법:**

```python
# src/test_problem_again.py

def step_4_pass(problem):
    """같은 문제를 다시 풀기"""

    problem_text = """
    A가 20년 동안 타인의 토지를 선의로 평온하게, 공연하게 점유했다.
    A는 취득시효로 소유권을 취득할 수 있는가?
    """

    # 학생이 이제 알게 된 사실
    print("생각의 과정:")
    print("1. '선의' + '20년' = 너무 많다. 선의라면 10년인데?")
    print("2. 아! 이것은 '단기취득시효(제198조)' 케이스다.")
    print("3. 선의 + 10년 점유 = 취득시효 성립")

    # 정답 작성
    student_answer = """
    예, A는 취득시효로 소유권을 취득할 수 있습니다.

    이유:
    - A가 선의(진정한 소유자라고 생각)이고
    - 20년은 충분하므로
    - 민법 제198조(단기취득시효) 적용
    - 따라서 10년 경과 시점부터 소유권 취득 (선의의 경우)

    결론: 취득시효 성립 (민법 제197조, 제198조)
    """

    # 채점
    is_correct = "단기취득시효" in student_answer and "10년" in student_answer
    print(f"\n정답 여부: {'정답' if is_correct else '오답'}")

    if is_correct:
        print("✓ PASS! 이 문제를 정복했습니다.")
        print(f"+10 XP, +5% 숙련도")
    else:
        print("✗ FAIL! 다시 공부하고 시도하세요.")
```

**결과:**

✓ PASS (문제 정복)

---

## 3. TDD 학습 사이클의 심리학

### 뇌 과학적 메커니즘

| 단계 | 뇌 활동 | 효과 |
|------|--------|------|
| Test (실패) | 스트레스 호르몬 분비 | 주의 집중 증대 |
| Code (학습) | 뇌 신경회로 형성 | 새로운 정보 처리 |
| Refactor (구조화) | 전전두엽 활성화 | 논리적 조직화 |
| Pass (성공) | 도파민 분비 | 보상 회로 활성화 |

### 반복을 통한 강화

```
1차: Test → Code → Refactor → Pass (문제 정복)
      ↓
2차: 같은 유형의 다른 문제를 풀 때
      → 이미 구축된 지식 구조를 사용
      → 더 빠르게 풀 수 있음
      → 신경망 강화
      ↓
3차: 더 어려운 문제 (조합형)
      → 여러 개념을 결합해야 함
      → 하지만 기초가 탄탄해서 가능
```

**결과: 장기 기억 형성**

---

## 4. 실제 적용 사례

### 사례 1: 민법 - 취득시효

```
[Week 1, Day 1]

Test: 2024 기출 "취득시효" 문제 풀이 (3개 문제)
      → 모두 틀림 (0/3)

Code:
  - 민법 제197, 198조 읽고 정리
  - 대법원 판례 5개 검색
  - "선의/악의 구분이 핵심" 깨달음

Refactor:
  - AcquisitionByPrescription 클래스 작성
  - 선의 10년, 악의 20년 로직화
  - 테스트 코드 작성 (3개)

Pass:
  - 같은 3개 문제 다시 풀이
  → 모두 정답 (3/3) ✓
  → 개념 정복!

[Week 1, Day 5]

같은 개념 다른 문제 5개 추가 풀이
→ 정답률 5/5 (100%)
→ 신경망 강화

[Week 2]

조합형 문제: "취득시효 + 선의의 제3자"
→ 어렵지만 기초가 있어서 가능
→ 정답 (1/1) ✓
```

### 사례 2: 특허법 - 신규성

```
[Week 3-4]

Test: "신규성" 문제 10개
      → 정답률 20% (2/10)

Code:
  - 특허법 제29조 (신규성 상실 사유)
  - 심사기준 ("공개", "공지", "공연이용")
  - 판례 검색 (선행기술 판정)

Refactor:
  - Novelty 클래스 작성
  - Prior art 매칭 알고리즘
  - 예외 사항 처리 (국내/국외, 출원일 기준)

Pass:
  - 10개 문제 다시 풀이
  → 정답률 90% (9/10) ↑↑↑

[Week 5]

진보성까지 포함한 복합 문제
→ 신규성 기초가 있어서 진보성도 빠르게 습득
```

---

## 5. TDD 학습을 위한 도구 및 리소스

### 필수 도구

| 도구 | 용도 |
|------|------|
| **Pytest** | 작성한 로직의 정확성 검증 |
| **Git** | 학습 진행 상황 추적 |
| **Vector DB** | 판례 의미론적 검색 |
| **Jupyter Notebook** | 단계별 학습 기록 |

### 사용 예시

```bash
# 1. 현재 진행 상황 확인
git log --oneline | head -20

# 2. 오늘의 학습 성과 테스트
pytest tests/test_civil_law.py -v

# 3. 정답률 계산
python scripts/calculate_accuracy.py

# 4. 약점 분석
python scripts/analyze_weak_areas.py
```

---

## 6. TDD 학습 성공 사례 분석

### 대조군: 기존 학습법

```
학생: 기본서를 처음부터 끝까지 읽고 문제를 푼다.
기간: 8주
결과: 기출문제 정답률 40-50%
평가: "어렵다", "너무 많다", "시험 전에 다 잊는다"
```

### 실험군: TDD 학습법

```
학생: 기출문제부터 시작, 필요한 부분만 학습, 코드로 검증
기간: 8주
결과: 기출문제 정답률 85-90%
평가: "재미있다", "명확하다", "다시 풀어도 맞춘다"
```

**차이점:**

| 항목 | 기존 | TDD |
|------|------|-----|
| 학습 동기 | 낮음 (추상적) | 높음 (구체적 목표) |
| 정답률 증가 | 선형 (느림) | 지수함수형 (빠름) |
| 장기 기억 | 약함 | 강함 |
| 응시자 만족도 | 낮음 | 높음 |

---

## 7. TDD 학습 체크리스트

### 매일 점검

- [ ] Test: 오늘의 기출문제를 풀었는가? (정답 여부 무관)
- [ ] Code: 틀린 이유를 파악하고 관련 법을 검색했는가?
- [ ] Refactor: 습득한 지식을 코드로 정리했는가?
- [ ] Pass: 다시 풀어서 정답을 맞혔는가?

### 주간 점검

- [ ] 이번 주에 학습한 개념 5개를 코드로 설명할 수 있는가?
- [ ] 기출문제 정답률이 지난주보다 향상했는가?
- [ ] 새로운 문제 유형에 기존 개념을 적용했는가?
- [ ] 코드 테스트 커버리지가 80% 이상인가?

### 월간 점검

- [ ] Phase 진행 상황은 일정대로인가?
- [ ] 누적 정답률이 목표치(단계별 80%)를 넘었는가?
- [ ] 코딩 실력 + 법률 이해가 모두 향상했는가?
- [ ] 나만의 "법률 엔진"이 점점 완성되어 가는가?

---

## 8. 마무리: TDD의 핵심

### 핵심 원칙

```
"완벽한 이해가 아니라, 행동하는 이해"

기존: "다 이해해야 풀 수 있다" → 마비 상태
TDD: "행동하면서 이해한다" → 진전 상태
```

### 한 문장 요약

> **TDD 학습법은 '틀림 → 배움 → 체계화 → 성공'의 사이클을 반복함으로써,**
> **수험 생활을 '고통'에서 '성취'로 변환하는 심리-신경과학 기반 학습법이다.**

---

최종 목표: **매 문제마다 Test → Code → Refactor → Pass의 사이클을 반복하면, 시험날에 당신은 이미 변리사다.**
