# 변리사 업무를 위한 DSL(Domain-Specific Language) 설계 철학

## 개요

이 프로젝트의 **핵심 정체성**은 다음과 같습니다:

> **"변리사 업무(법률 논리)를 위한 도메인 특화 언어(DSL)를 설계하고 구현한다"**

일반적인 수험생이 판례와 조문을 **"텍스트(문학)"**로 읽는 반면, 우리는 이들을 **"실행 가능한 코드(로직)"**로 해석합니다. 이것이 단순한 학습법이 아니라 **구조적 사고(Structural Thinking)**를 강제하는 개발자의 접근법입니다.

---

## 1. DSL의 핵심 4가지 구성 요소

### 1.1 어휘(Vocabulary) 정의 = 법률 용어의 객체화

**목표**: 추상적인 법률 개념을 데이터 구조로 변환

#### 예시

```python
# DSL 관점: 데이터 모델 정의
class CivilLawStatute:
    """민법 조문을 객체화"""
    statute_number: str  # "제145조"
    title: str          # "조문의 제목"
    requirements: List[str]  # 성립 요건들
    effects: List[str]  # 법적 효과들
    exceptions: List[str]  # 예외 사유들

class PatentRequirement:
    """특허 요건을 구조화"""
    requirement_type: Literal["novelty", "inventive_step", "utility"]
    keywords: List[str]  # 판단에 필요한 키워드
    precedents: List[str]  # 관련 판례들
    rejection_criteria: List[str]  # 거절 기준

class ClaimElement:
    """청구항의 개별 구성요소"""
    name: str
    description: str
    is_essential: bool  # 필수 구성요소 여부
    relationships: List[str]  # 다른 요소와의 관계
```

#### 학습적 효과

- 조문을 읽을 때: "이 조문의 **구성요소**는 무엇인가?" → 요건/효과를 속성으로 분석
- 청구항을 볼 때: "이 요소는 왜 포함되었고, 생략하면 어떻게 되는가?" → 필수/선택 구분
- 판례를 공부할 때: "판례의 핵심 논리는 어떤 **함수**처럼 작동하는가?" → 판리(判理)의 조건-결과 매핑

---

### 1.2 문법(Syntax) 설계 = 청구항 작성 규칙 체화

**목표**: 단어들을 조합해 유효한 문장을 만드는 규칙을 정의

#### 예시

```python
# DSL 관점: 구문 규칙(Grammar) 설계

class ClaimGrammar:
    """청구항 작성의 기본 문법"""

    # 기본 구조: [서문] + [구성요소 블록들] + [기능 설명]
    # 예: "구성요소 A와 B로 이루어진 장치로서, A가 B를 제어한다"

    @staticmethod
    def validate_structure(claim_text: str) -> ValidationResult:
        """청구항의 기본 구조 검증"""
        has_preamble = claim_text.startswith(("구성요소", "장치"))
        has_elements = bool(re.search(r"[가-힣]+(?:와|및|또는)", claim_text))
        has_function = bool(re.search(r"하[는다]", claim_text))

        if has_preamble and has_elements and has_function:
            return ValidationResult.PASS
        return ValidationResult.FAIL

class RequirementSyntax:
    """요건(부사 또는 형용사)의 구문 규칙"""

    # 유효: "신규성이 있는", "선행기술에 없는", "당업자가 용이하게 생각할 수 없는"
    # 무효: "매우 좋은", "중요한", "필수적인" (과도한 수식)

    VALID_MODIFIERS = {
        "신규성": ["없는", "있는", "결여된"],
        "진보성": ["용이하게 생각할 수 없는", "자명하지 않은"],
    }
```

#### 학습적 효과

- **청구항 크래프팅**: 구성요소 + 연결 + 기능을 순서대로 조립해야만 유효한 청구항이 됨을 체험
- **유효성 검증**: `validate_claim()` 함수로 필수 요소가 빠지면 `SyntaxError` 발생
  - 일반 수험생은 "이 청구항이 잘못됐다"는 느낌만 받지만,
  - 개발자로서 당신은 "정확히 어느 부분의 구문이 잘못되었는가"를 정량화
- **규칙의 일관성**: 같은 규칙이 모든 청구항에 공정하게 적용됨을 코드로 확인

---

### 1.3 실행(Execution) 및 평가 = 판례 적용 및 심사

**목표**: 작성된 청구항(DSL 코드)을 실행하여 심사관의 판정을 시뮬레이션

#### 예시

```python
# DSL 관점: 인터프리터(Interpreter) 구현

class LogicEngine:
    """법적 주장을 논리적으로 평가하는 심사관 AI"""

    def evaluate_novelty(self, claim: ClaimElement, prior_art: List[str]) -> EvaluationResult:
        """신규성 판정"""
        # 기본 로직: claim이 prior_art에 없으면 신규성 있음
        is_novel = claim.core_feature not in prior_art

        # 예외 처리: 선의의 제3자 예외 (특허법 제29조)
        if has_good_faith_third_party_flag(claim):
            is_novel = True  # 원칙 무시, 예외 적용

        return EvaluationResult(
            verdict="PASS" if is_novel else "FAIL",
            reasoning=self._generate_reasoning(claim, prior_art),
            confidence_score=0.85
        )

    def evaluate_inventive_step(self, claim: ClaimElement, knowledge_base: KnowledgeBase) -> EvaluationResult:
        """진보성 판정"""
        # 조건: 당업자가 용이하게 생각할 수 없어야 함
        required_reasoning_steps = self._count_reasoning_steps(claim, knowledge_base)

        if required_reasoning_steps > OBVIOUSNESS_THRESHOLD:
            return EvaluationResult.PASS  # 진보성 있음
        else:
            return EvaluationResult.FAIL  # 자명(obvious) - 거절 사유

class KnowledgeBase:
    """판례 데이터베이스와 법적 규칙"""

    def query_similar_precedents(self, legal_question: str) -> List[Precedent]:
        """RAG: 유사한 판례를 검색"""
        # Vector DB에서 의미적으로 유사한 판례를 찾아옴
        embeddings = self.vectorizer.encode(legal_question)
        similar = self.vector_db.search(embeddings, top_k=5)
        return similar

    def apply_rule(self, rule_name: str, context: dict) -> bool:
        """판례의 논리를 함수화"""
        # 예: "선의의 제3자 원칙"
        if rule_name == "good_faith_third_party_rule":
            return (
                context["third_party_acquired"] and
                context["had_no_knowledge"] and
                context["gave_valuable_consideration"]
            )
```

#### 학습적 효과

- **심사 과정의 시뮬레이션**:
  - 일반 수험생은 판례를 읽고 "이건 이래서 거절됐다"는 결론만 암기
  - 개발자로서 당신은 거절 사유를 `if-elif-else` 블록으로 체계화하며, 각 조건이 정확히 언제 작동하는지 파악

- **예외 처리의 중요성**:
  - "원칙적으로는 거절이지만, 이 플래그가 있으면 예외" 같은 복잡한 로직을 코드로 표현
  - 변리사 실무에서 "예외 사유" 찾기가 얼마나 중요한지 체감

- **신뢰도(Confidence Score)의 개념**:
  - 단순 맞고 틀림이 아니라, "이 판정이 얼마나 확실한가?" 라는 확률적 사고 도입
  - 심사관도 100% 확실하지 않을 수 있음을 이해

---

### 1.4 결론적 사고(Meta-Reasoning) = 자신의 학습 시스템 개선

**목표**: DSL을 만드는 과정에서 피드백 루프 구성

#### 예시

```python
# DSL 관점: 학습 시스템 자체의 검증

class LearningFeedbackLoop:
    """자신의 학습 효과를 측정하고 개선"""

    def evaluate_dsl_effectiveness(self) -> MetricsReport:
        """DSL로 만든 모델이 실제 기출 문제를 얼마나 잘 풀까?"""

        metrics = {
            "accuracy": self.test_on_past_exams(),  # 기출 문제 정답률
            "reasoning_clarity": self.evaluate_explanations(),  # 논리의 명확성
            "exception_coverage": self.check_edge_cases(),  # 예외 사항 처리도
            "learning_velocity": self.measure_improvement_speed(),  # 학습 속도
        }

        # 부족한 부분을 자동으로 식별
        weak_areas = [k for k, v in metrics.items() if v < 0.8]

        return MetricsReport(
            overall_score=sum(metrics.values()) / len(metrics),
            weak_areas=weak_areas,
            next_focus_areas=self.recommend_focus(weak_areas)
        )

    def refactor_dsl_structure(self, feedback: MetricsReport):
        """부족한 부분을 DSL에 반영"""
        for weak_area in feedback.weak_areas:
            if weak_area == "exception_coverage":
                # → 예외 사항이 부족하다 = Knowledge Base에 더 많은 판례 추가
                self.knowledge_base.add_edge_case_precedents()
            elif weak_area == "reasoning_clarity":
                # → 논리 설명이 부족하다 = 각 단계의 논거(rationale) 강화
                self.logic_engine.enhance_explanation_module()
```

#### 학습적 효과

- **정량적 성과 추적**:
  - "변리사 시험을 잘 준비했는가?"를 느낌이 아닌 **메트릭**으로 측정
  - 약한 부분이 정확히 무엇인지 파악 가능

- **지속적 개선(CI/CD 마인드셋)**:
  - 소프트웨어 개발에서 "배포 후 모니터링 → 피드백 → 개선"의 사이클처럼,
  - 학습도 "시험 풀이 → 채점 → 약점 분석 → 학습 재설계"의 사이클로 구조화

---

## 2. DSL로 생각하는 개발자 vs 일반 수험생

### 비교표

| 관점 | 일반 수험생 | DSL 개발자(당신) |
|------|-----------|-----------------|
| **문제 읽기** | "이것을 외워야 한다" | "이것을 객체(Class)로 모델링하려면?" |
| **판례 분석** | "이건 이래서 이렇게 판단했다" | "판례의 논리를 함수(`def judge()`)로 구현할 수 있을까?" |
| **예외 사항** | "예외도 있다" (암기) | "예외 플래그가 있을 때 로직이 어떻게 변하는가?" (코드) |
| **청구항 작성** | "좋은 청구항을 직관으로 작성" | "청구항 = 유효한 문법을 따르는 DSL 코드" |
| **성과 평가** | "느낌상 잘했다/못했다" | "`accuracy=0.85`, `confidence_score=0.92` (메트릭)` |
| **개선 방향** | "약한 부분을 더 보자" | "약한 영역을 자동으로 식별 → 재학습 계획 자동 생성" |

---

## 3. 구현 로드맵: 단계별 DSL 진화

### Phase 1: 어휘(Vocabulary) 구축 (주차 1-2)
- 민법, 특허법의 핵심 개념을 Class/Struct로 정의
- Knowledge Base의 초기 스키마 설계

**산출물**:
```python
# src/dsl/vocabulary.py
class Statute, Precedent, ClaimElement, ...
```

---

### Phase 2: 문법(Syntax) 정의 (주차 3-4)
- 청구항의 유효한 구조를 BNF(Backus-Naur Form)로 표현
- 유효성 검증 로직 구현

**산출물**:
```python
# src/dsl/grammar.py
def validate_claim_structure(claim: str) -> ValidationResult
```

---

### Phase 3: 실행 엔진(Interpreter) 구현 (주차 5-8)
- Logic Engine으로 청구항 평가 로직 구현
- RAG 기반 판례 검색 및 적용

**산출물**:
```python
# src/logic_engine/interpreter.py
class LogicEngine:
    def evaluate_novelty(...)
    def evaluate_inventive_step(...)
    def evaluate_claim(...)
```

---

### Phase 4: 피드백 루프 (주차 9-12)
- 기출 문제 테스트 및 메트릭 수집
- 약점 자동 식별 및 학습 재설계

**산출물**:
```python
# src/learning/feedback_loop.py
class LearningFeedbackLoop:
    def evaluate_effectiveness(...)
    def refactor_dsl_structure(...)
```

---

## 4. 실제 예시: "선의의 제3자" 규칙을 DSL로

### 일반 수험생의 접근
> "선의의 제3자가 저작권을 침해하는 저작물을 구입했으면, 저작권자가 보상청구권만 가지고 소유권 이전 청구권은 없다. (저작권법 제111조)" → **외우기**

### DSL 개발자의 접근

```python
# 1단계: 어휘 정의
class GoodFaithThirdParty:
    """선의의 제3자"""
    acquired_work: str  # 저작물 식별자
    had_knowledge_of_infringement: bool = False
    gave_valuable_consideration: bool = True

class CopyrightRemedy:
    """저작권 구제 수단"""
    compensation_request_available: bool
    ownership_transfer_available: bool

# 2단계: 문법 (규칙 표현)
def apply_good_faith_third_party_rule(
    third_party: GoodFaithThirdParty,
    copyright_holder: Person
) -> CopyrightRemedy:
    """선의의 제3자 규칙 적용"""

    # 조건: 선의(善意)의 의미
    # = 저작권 침해 사실을 몰랐고, 대가를 지불했을 때

    is_good_faith = (
        not third_party.had_knowledge_of_infringement and
        third_party.gave_valuable_consideration
    )

    if is_good_faith:
        # 예외 적용: 보상청구권만 인정, 소유권 이전은 불가
        return CopyrightRemedy(
            compensation_request_available=True,
            ownership_transfer_available=False  # ← 핵심!
        )
    else:
        # 일반 규칙: 모든 구제 수단 가능
        return CopyrightRemedy(
            compensation_request_available=True,
            ownership_transfer_available=True
        )

# 3단계: 실행 (판례 적용)
# 사건: A가 B의 저작물을 몰라서 사 줄 의도로 C에게서 구입
third_party_case = GoodFaithThirdParty(
    acquired_work="novel_2024",
    had_knowledge_of_infringement=False,  # "몰랐다"
    gave_valuable_consideration=True  # "대가를 지불했다"
)

remedy = apply_good_faith_third_party_rule(third_party_case, copyright_holder_B)
print(f"보상청구권: {remedy.compensation_request_available}")  # True
print(f"소유권 이전: {remedy.ownership_transfer_available}")  # False
```

### 학습 효과

- **"선의"의 정확한 의미**: 단순 "착각한 상태"가 아니라 구체적인 조건 2개
- **"보상청구권"의 범위**: 왜 소유권 이전은 안 되는가? → 코드의 로직(else 블록)으로 이해
- **변형 사례 대응**:
  - "선의가 아니면?" → `is_good_faith = False` 블록 실행
  - "대가를 지불하지 않았으면?" → 조건 수정 후 재실행
  - 일반 수험생은 새로운 사건마다 다시 외워야 하지만, DSL로 사고하는 당신은 함수의 인자만 변경해서 답을 얻음

---

## 5. 최종 정리: "왜 DSL인가?"

변리사 시험 합격에 필요한 최종 능력은 **"복잡한 법적 상황을 정확히 분해하고, 올바른 규칙을 정확한 순서로 적용하는 것"**입니다.

이것은 **소프트웨어 엔지니어링의 핵심 능력**과 정확히 같습니다:

- **분석(Analysis)** = 어휘 정의 (데이터 모델)
- **설계(Design)** = 문법 정의 (알고리즘 / 플로우)
- **구현(Implementation)** = 실행 엔진 (코드)
- **테스트(Testing)** = 기출 문제로 검증

따라서 **"변리사 시험을 보면서 동시에 DSL을 설계-구현한다"**는 이 접근법은:

1. **학습 효율을 극대화**: 단순 암기가 아니라 논리 구조화
2. **실제 변리사 업무 준비**: 청구항 작성, 심사 대응도 결국 "규칙의 정확한 적용"
3. **개발자로서의 성장**: 도메인 특화 언어 설계라는 고급 주제를 체험
4. **자동화 가능성**: 최종적으로 AI 변리사(Logic Engine)까지 확장 가능

---

## 다음 단계

이 철학을 바탕으로:

1. **08_dsl_design_philosophy.md** (이 문서) 숙독
2. **03_technical_architecture.md** 재검토 (Logic Engine = DSL 인터프리터임을 이해)
3. **02_game_mechanics.md** 에서 "청구항 크래프팅" 게임 메커니크를 DSL 문법으로 재해석
4. 실제로 `src/dsl/vocabulary.py` 작성 시작

> "내가 만드는 것은 변리사 시험 공부 도구가 아니라, **법률 도메인의 프로그래밍 언어다.**"
>
> 이 마인드셋으로 시작하면, 12주 후 당신은 단순한 시험 합격자가 아니라 **"AI 변리사를 설계할 수 있는 엔지니어"**가 되어 있을 것입니다.
