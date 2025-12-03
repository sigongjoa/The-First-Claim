# 구현 로드맵: 단계별 개발 계획

## 📋 현재 상태

### ✅ 완료된 작업
- [x] 프로젝트 아키텍처 문서화 (docs/ 1-8번)
- [x] DSL 철학 정리 (08_dsl_design_philosophy.md)
- [x] PDF 분석 도구 (analyze_pdf.py)
- [x] 인터랙티브 PDF 뷰어 (index.html, exam_viewer.html)
- [x] .gitignore 설정 (저작권 파일 제외)

### 🔜 다음 단계: 실제 코드 구현

---

## 🛠️ Phase 1: DSL 어휘(Vocabulary) 정의 (주차 1-2)

### 목표
핵심 데이터 모델을 정의하고, 추상적인 법률 개념을 코드 객체로 변환

### 🎯 Phase 1-1: 민법 기초 데이터 모델 (1주차)

**파일**: `src/dsl/vocabulary/civil_law.py`

```python
# 구현할 클래스들:

class CivilLawStatute:
    """민법 조문을 객체화"""
    statute_number: str  # "제145조"
    title: str
    requirements: List[str]  # 성립 요건
    effects: List[str]  # 법적 효과
    exceptions: List[str]  # 예외 사유
    related_precedents: List[str]  # 관련 판례

class LegalRight:
    """법적 권리"""
    name: str  # "저작권", "특허권"
    scope: str  # 보호 범위
    duration: str  # 보호 기간
    remedies: List[str]  # 구제 수단

class Person:
    """법적 주체"""
    name: str
    role: str  # "저작권자", "침해자", "제3자"
    attributes: Dict[str, bool]  # {"good_faith": True, ...}

class Transaction:
    """거래/법적 행위"""
    parties: List[Person]
    subject: str  # 거래 대상
    consideration: str  # 대가
    date: str  # 발생 일시
```

**체크리스트**:
- [ ] `src/dsl/` 디렉토리 생성
- [ ] `src/dsl/vocabulary/` 디렉토리 생성
- [ ] `civil_law.py` 파일 작성
- [ ] 각 클래스에 `__init__`, `__repr__`, `__eq__` 메서드 구현
- [ ] 단위 테스트 작성 (`tests/test_civil_law_vocabulary.py`)

---

### 🎯 Phase 1-2: 특허법 데이터 모델 (1주차)

**파일**: `src/dsl/vocabulary/patent_law.py`

```python
# 구현할 클래스들:

class PatentRequirement:
    """특허 요건"""
    requirement_type: Literal["novelty", "inventive_step", "utility", "clarity"]
    description: str
    keywords: List[str]  # 판단에 필요한 키워드
    precedents: List[str]  # 관련 판례 ID

class ClaimElement:
    """청구항의 개별 구성요소"""
    id: str  # "element_1"
    name: str  # "전송부"
    description: str
    is_essential: bool  # 필수 구성요소 여부
    relationships: List[Tuple[str, str]]  # [("element_2", "제어한다")]
    prior_art_reference: str  # 선행기술 참조

class Claim:
    """청구항 (완전한 구조)"""
    claim_number: int
    preamble: str  # "다음으로 이루어진 장치"
    elements: List[ClaimElement]
    claims_back_to: Optional[int]  # 종속 청구항 연결
    validity_score: float = 0.0

class PriorArt:
    """선행기술"""
    reference_id: str
    title: str
    publication_date: str
    source: str  # "특허", "논문", "공중의 이용"
    content: str  # 주요 내용
    relevance_score: float = 0.0
```

**체크리스트**:
- [ ] `patent_law.py` 파일 작성
- [ ] 청구항 유효성 판단을 위한 helper 메서드 추가
- [ ] 선행기술 비교를 위한 메서드 추가
- [ ] 단위 테스트 작성 (`tests/test_patent_law_vocabulary.py`)

---

## 📝 Phase 2: DSL 문법(Syntax) 정의 (주차 3-4)

### 목표
유효한 청구항/법적 주장의 구조를 정의하고, 자동 검증 시스템 구축

### 🎯 Phase 2-1: 청구항 구조 검증 (1주차)

**파일**: `src/dsl/grammar/claim_grammar.py`

```python
# 구현할 검증 함수들:

class ClaimGrammar:
    """청구항의 문법 규칙"""

    @staticmethod
    def validate_structure(claim: Claim) -> ValidationResult:
        """청구항 기본 구조 검증"""
        # 검사 항목:
        # 1. 서문(preamble) 필수
        # 2. 최소 1개 이상의 구성요소 필수
        # 3. 기능 설명 필수
        # 4. 종속 청구항은 독립 청구항 참조 필수
        pass

    @staticmethod
    def validate_claim_breadth(claim: Claim, prior_art: List[PriorArt]) -> BreadthScore:
        """청구항의 너비(범위) 판단"""
        # 너무 넓으면 실현 불가능(indefiniteness) 거절
        # 너무 좁으면 선행기술과 차이 없음
        pass

    @staticmethod
    def validate_element_clarity(claim: Claim) -> ClarityScore:
        """구성요소의 명확성 검증"""
        # 각 요소의 설명이 충분한가?
        # 요소 간 관계가 명확한가?
        pass
```

**체크리스트**:
- [ ] `src/dsl/grammar/` 디렉토리 생성
- [ ] `claim_grammar.py` 파일 작성
- [ ] BNF(Backus-Naur Form) 문법 정의 추가
- [ ] 청구항 파싱 로직 구현
- [ ] 단위 테스트 작성

---

### 🎯 Phase 2-2: 법적 요건 문법 정의 (1주차)

**파일**: `src/dsl/grammar/legal_requirement_grammar.py`

```python
# 구현할 검증 함수들:

class RequirementSyntax:
    """법적 요건의 표현 규칙"""

    VALID_MODIFIERS = {
        "신규성": ["없는", "있는", "결여된"],
        "진보성": ["용이하게 생각할 수 없는", "자명하지 않은"],
        "명확성": ["분명한", "불명확한"],
    }

    @staticmethod
    def validate_requirement_statement(statement: str, requirement_type: str) -> ValidationResult:
        """요건에 대한 주장의 문법 검증"""
        # 과도한 수식어 제거 ("매우 좋은" X, "명백한" O)
        # 증거와의 일치 확인
        pass

    @staticmethod
    def validate_rejection_reason(reason: str) -> RejectionReason:
        """거절 사유가 유효한가?"""
        # 특허법에 규정된 거절 사유만 인정
        # 예: 신규성 결여, 진보성 부족, 명확성 결여, 실현가능성 부족
        pass
```

**체크리스트**:
- [ ] `legal_requirement_grammar.py` 파일 작성
- [ ] 거절 사유 타입 정의 (Enum)
- [ ] 요건별 검증 로직 구현
- [ ] 단위 테스트 작성

---

## 🔧 Phase 3: Logic Engine 구현 (주차 5-8)

### 목표
청구항을 평가하고 심사관의 판정을 시뮬레이션하는 엔진 구현

### 🎯 Phase 3-1: 신규성(Novelty) 평가 엔진 (1주차)

**파일**: `src/logic_engine/evaluators/novelty_evaluator.py`

```python
class NoveltyEvaluator:
    """신규성 판정"""

    def evaluate(self, claim: Claim, prior_art: List[PriorArt]) -> EvaluationResult:
        """
        신규성 판정: claim의 모든 요소가 단일 선행기술에 전개되어 있는가?
        """
        # 알고리즘:
        # 1. 각 선행기술에 대해 claim 요소들이 모두 포함되는가 검사
        # 2. 하나의 선행기술도 모든 요소를 포함하지 않으면 신규성 있음
        # 3. 신규성 있음 = PASS, 없음 = FAIL
        pass

    def _match_element_to_prior_art(self, element: ClaimElement, prior_art: PriorArt) -> float:
        """특정 요소가 선행기술에 포함되는 정도 (0.0~1.0)"""
        # Vector 임베딩을 이용한 유사도 계산
        pass

    def generate_reasoning(self, claim: Claim, evaluation: EvaluationResult) -> str:
        """판정 근거 생성"""
        # 예: "청구항 1의 '전송부'는 선행기술 A에 전개되지 않으므로 신규성 있음"
        pass
```

**체크리스트**:
- [ ] `src/logic_engine/` 디렉토리 생성
- [ ] `src/logic_engine/evaluators/` 디렉토리 생성
- [ ] `novelty_evaluator.py` 작성
- [ ] 벡터 임베딩 통합 (OpenAI/HuggingFace)
- [ ] 단위 테스트 작성

---

### 🎯 Phase 3-2: 진보성(Inventive Step) 평가 엔진 (1주차)

**파일**: `src/logic_engine/evaluators/inventive_step_evaluator.py`

```python
class InventiveStepEvaluator:
    """진보성 판정"""

    def evaluate(self, claim: Claim, prior_art: List[PriorArt], knowledge_base: KnowledgeBase) -> EvaluationResult:
        """
        진보성 판정: 당업자가 청구항의 결합을 용이하게 생각할 수 없는가?
        """
        # 알고리즘:
        # 1. 필요한 조합의 수 계산
        # 2. 조합의 동기 또는 암시 여부 검사
        # 3. 예상 가능한 결과인지 판단
        # 4. 진보성 있음 = PASS, 자명함 = FAIL
        pass

    def _calculate_combination_complexity(self, claim: Claim, prior_art: List[PriorArt]) -> int:
        """조합의 복잡성 (조합 개수 계산)"""
        pass

    def _check_suggestion_or_motivation(self, combination: List[PriorArt], knowledge_base: KnowledgeBase) -> bool:
        """조합에 대한 동기나 암시가 있는가?"""
        pass

    def _is_predictable_result(self, combination: List[PriorArt], knowledge_base: KnowledgeBase) -> bool:
        """예상 가능한 결과인가?"""
        pass
```

**체크리스트**:
- [ ] `inventive_step_evaluator.py` 작성
- [ ] 조합 알고리즘 구현
- [ ] 동기/암시 판단 로직 구현
- [ ] 단위 테스트 작성

---

### 🎯 Phase 3-3: Knowledge Base 구축 (1주차)

**파일**: `src/knowledge_base/precedent_db.py`

```python
class PrecedentDatabase:
    """판례 데이터베이스"""

    def __init__(self, vector_db_connection):
        self.vector_db = vector_db_connection  # Pinecone / Weaviate
        self.cache = {}

    def add_precedent(self, precedent: Precedent):
        """판례 추가"""
        # 1. 판례 객체 저장
        # 2. 요약 생성
        # 3. 벡터 임베딩 생성 및 저장
        pass

    def query_similar_precedents(self, query: str, top_k: int = 5) -> List[Precedent]:
        """유사 판례 검색 (RAG)"""
        # 1. 쿼리를 벡터로 변환
        # 2. Vector DB에서 유사도 검색
        # 3. 상위 k개 반환
        pass

    def apply_precedent_rule(self, precedent: Precedent, case: Case) -> bool:
        """판례의 논리를 현재 사건에 적용"""
        # 판례의 키 사항이 현재 사건에도 적용되는가?
        pass
```

**체크리스트**:
- [ ] `src/knowledge_base/` 디렉토리 생성
- [ ] `precedent_db.py` 작성
- [ ] Vector DB 연결 설정 (Pinecone or Weaviate)
- [ ] 초기 판례 데이터 로드 (JSON/CSV)
- [ ] 단위 테스트 작성

---

### 🎯 Phase 3-4: 통합 Logic Engine (1주차)

**파일**: `src/logic_engine/engine.py`

```python
class LogicEngine:
    """통합 심사 엔진"""

    def __init__(self, knowledge_base: PrecedentDatabase):
        self.knowledge_base = knowledge_base
        self.novelty_eval = NoveltyEvaluator()
        self.inventive_step_eval = InventiveStepEvaluator()

    def evaluate_claim(self, claim: Claim, prior_art: List[PriorArt]) -> ClaimEvaluation:
        """청구항 종합 평가"""
        # 1단계: 신규성 검사
        novelty_result = self.novelty_eval.evaluate(claim, prior_art)
        if novelty_result.verdict == "FAIL":
            return ClaimEvaluation(
                verdict="REJECT",
                reason="lack of novelty",
                details=novelty_result
            )

        # 2단계: 진보성 검사
        inventive_result = self.inventive_step_eval.evaluate(claim, prior_art, self.knowledge_base)
        if inventive_result.verdict == "FAIL":
            return ClaimEvaluation(
                verdict="REJECT",
                reason="lack of inventive step",
                details=inventive_result
            )

        # 3단계: 명확성 검사
        clarity_result = self._evaluate_clarity(claim)
        if clarity_result.verdict == "FAIL":
            return ClaimEvaluation(
                verdict="REJECT",
                reason="lack of clarity",
                details=clarity_result
            )

        # 모든 검사 통과
        return ClaimEvaluation(
            verdict="ACCEPT",
            confidence_score=0.95,
            details={
                "novelty": novelty_result,
                "inventive_step": inventive_result,
                "clarity": clarity_result
            }
        )

    def _evaluate_clarity(self, claim: Claim) -> EvaluationResult:
        """명확성 평가"""
        pass
```

**체크리스트**:
- [ ] `engine.py` 작성
- [ ] 평가 결과 자료구조 정의
- [ ] 통합 테스트 작성

---

## 🎮 Phase 4: 게임 UI/인터페이스 (주차 9-10)

### 🎯 Phase 4-1: 청구항 크래프팅 인터페이스 (1주차)

**파일**: `src/ui/claim_crafting_ui.py`

```python
class ClaimCraftingUI:
    """청구항 작성 인터페이스"""

    def display_claim_editor(self):
        """청구항 편집 화면"""
        # UI 요소:
        # 1. 서문 입력 필드
        # 2. 구성요소 추가/삭제 버튼
        # 3. 요소 관계 정의 패널
        # 4. 실시간 유효성 검사 (초록/빨강)
        # 5. 미리보기 패널
        pass

    def validate_and_highlight_errors(self, claim: Claim):
        """입력한 청구항의 오류를 시각화"""
        # 구문 오류: 빨강 밑줄
        # 경고: 노랑 밑줄
        # 최적화 제안: 초록 밑줄
        pass

    def suggest_improvements(self, claim: Claim) -> List[str]:
        """청구항 개선 제안"""
        # AI가 생성하는 개선 제안
        pass
```

**체크리스트**:
- [ ] `src/ui/` 디렉토리 생성
- [ ] Flask/FastAPI 백엔드 설정
- [ ] React/Vue 프론트엔드 설정
- [ ] 실시간 검증 WebSocket 구현
- [ ] UI 테스트 작성

---

### 🎯 Phase 4-2: 배틀 시뮬레이션 UI (1주차)

**파일**: `src/ui/battle_ui.py`

```python
class BattleSimulationUI:
    """심사관과의 배틀 인터페이스"""

    def display_examiner_action(self, rejection_reason: str, confidence: float):
        """심사관의 거절 이유 표시"""
        # 애니메이션: 심사관 캐릭터가 거절 이유 발언
        # 오디오: 음성 출력
        # 텍스트: 상세 이유
        pass

    def display_applicant_response_options(self, claim: Claim) -> List[str]:
        """출원인의 대응 방법 제시"""
        # 1. 청구항 수정 제안
        # 2. 반박 논거 제시
        # 3. 증거 제출
        pass

    def show_battle_result(self, result: ClaimEvaluation):
        """배틀 결과 표시"""
        # 승리/패배 애니메이션
        # 상세 채점 결과
        # 다음 배틀로 진행 or 다시 시도
        pass
```

**체크리스트**:
- [ ] `battle_ui.py` 작성
- [ ] 게임 엔진 통합 (Unity/Pygame 고려)
- [ ] 애니메이션 시스템 구현
- [ ] 사운드 시스템 구현
- [ ] UI 테스트 작성

---

## 📊 Phase 5: 피드백 루프 & 메트릭 시스템 (주차 11-12)

### 파일: `src/learning/feedback_loop.py`

```python
class LearningFeedbackLoop:
    """자신의 학습 효과를 측정하고 개선"""

    def evaluate_dsl_effectiveness(self) -> MetricsReport:
        """DSL 모델의 효과도 측정"""
        metrics = {
            "accuracy": self._test_on_past_exams(),  # 기출 문제 정답률
            "reasoning_clarity": self._evaluate_explanations(),  # 논리의 명확성
            "exception_coverage": self._check_edge_cases(),  # 예외 처리도
            "learning_velocity": self._measure_improvement_speed(),  # 학습 속도
        }
        return MetricsReport(
            overall_score=sum(metrics.values()) / len(metrics),
            weak_areas=[k for k, v in metrics.items() if v < 0.8],
        )

    def refactor_dsl_structure(self, feedback: MetricsReport):
        """부족한 부분을 DSL에 반영"""
        for weak_area in feedback.weak_areas:
            if weak_area == "exception_coverage":
                # → Knowledge Base에 더 많은 판례 추가
                self.knowledge_base.add_edge_case_precedents()
            elif weak_area == "reasoning_clarity":
                # → Logic Engine의 설명 모듈 강화
                self.logic_engine.enhance_explanation_module()
```

**체크리스트**:
- [ ] `src/learning/` 디렉토리 생성
- [ ] 메트릭 수집 시스템 구현
- [ ] 대시보드 생성
- [ ] 자동 개선 제안 시스템 구현

---

## 📁 최종 디렉토리 구조

```
The-First-Claim/
├── src/
│   ├── dsl/
│   │   ├── vocabulary/
│   │   │   ├── civil_law.py
│   │   │   ├── patent_law.py
│   │   │   └── __init__.py
│   │   ├── grammar/
│   │   │   ├── claim_grammar.py
│   │   │   ├── legal_requirement_grammar.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── logic_engine/
│   │   ├── evaluators/
│   │   │   ├── novelty_evaluator.py
│   │   │   ├── inventive_step_evaluator.py
│   │   │   └── __init__.py
│   │   ├── engine.py
│   │   └── __init__.py
│   ├── knowledge_base/
│   │   ├── precedent_db.py
│   │   ├── data/
│   │   │   └── precedents.json
│   │   └── __init__.py
│   ├── ui/
│   │   ├── claim_crafting_ui.py
│   │   ├── battle_ui.py
│   │   └── __init__.py
│   ├── learning/
│   │   ├── feedback_loop.py
│   │   └── __init__.py
│   └── main.py
├── tests/
│   ├── test_civil_law_vocabulary.py
│   ├── test_patent_law_vocabulary.py
│   ├── test_claim_grammar.py
│   ├── test_novelty_evaluator.py
│   ├── test_inventive_step_evaluator.py
│   ├── test_logic_engine.py
│   └── test_feedback_loop.py
├── docs/
│   ├── 01_project_overview.md
│   ├── 02_game_mechanics.md
│   ├── 03_technical_architecture.md
│   ├── 04_roadmap.md
│   ├── 05_study_methodology.md
│   ├── 06_design_philosophy.md
│   ├── 08_dsl_design_philosophy.md
│   └── INDEX.md
├── IMPLEMENTATION_ROADMAP.md (이 파일)
├── requirements.txt
├── pytest.ini
└── .gitignore
```

---

## 📌 우선순위

### 우선순위 1 (필수)
1. Phase 1-1: Civil Law Vocabulary
2. Phase 1-2: Patent Law Vocabulary
3. Phase 2-1: Claim Grammar
4. Phase 3-1: Novelty Evaluator

**이유**: 이 4개가 없으면 시스템이 작동하지 않음

### 우선순위 2 (중요)
5. Phase 3-3: Knowledge Base
6. Phase 3-2: Inventive Step Evaluator
7. Phase 3-4: Logic Engine 통합

**이유**: 평가 엔진의 핵심

### 우선순위 3 (심화)
8. Phase 4-1: Claim Crafting UI
9. Phase 4-2: Battle UI
10. Phase 5: Feedback Loop

**이유**: 게임화와 학습 최적화

---

## 🚀 즉시 시작 명령어

```bash
# 1. 환경 설정
cd /mnt/d/progress/The-First-Claim
python -m venv venv_dev
source venv_dev/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt
pip install pytest pytest-cov

# 3. 디렉토리 생성
mkdir -p src/{dsl,logic_engine,knowledge_base,ui,learning}/{vocabulary,evaluators,data}
mkdir -p tests

# 4. 첫 번째 파일 생성 시작
# → src/dsl/vocabulary/civil_law.py 작성 시작
# → tests/test_civil_law_vocabulary.py 작성

# 5. 테스트 실행
pytest tests/test_civil_law_vocabulary.py -v
```

---

## ⏰ 예상 타임라인

| Phase | 기간 | 주요 작업 | 산출물 |
|-------|------|---------|--------|
| 1 | 2주 | DSL 어휘 정의 | vocabulary/*.py (데이터 모델) |
| 2 | 2주 | DSL 문법 정의 | grammar/*.py (검증 시스템) |
| 3 | 4주 | Logic Engine | evaluators/*.py, engine.py (평가 시스템) |
| 4 | 2주 | UI/게임 구현 | ui/*.py, frontend (인터페이스) |
| 5 | 2주 | 피드백 루프 | learning/*.py (개선 시스템) |
| **합계** | **12주** | **전체 구현** | **완전한 AI 변리사 시스템** |

---

## 📚 다음 단계

1. **지금 바로 시작할 것**:
   - `src/dsl/vocabulary/civil_law.py` 작성 시작
   - `tests/test_civil_law_vocabulary.py` 작성

2. **코드 작성 원칙**:
   - TDD (Test-Driven Development) 순서대로
   - 각 클래스마다 단위 테스트 필수
   - Type hints 사용 (Python 3.10+)
   - Docstring 작성

3. **진행 추적**:
   - TODO 체크리스트 활용
   - 주간 진행 보고서 작성
   - 문서 업데이트

---

**시작일**: 2025-12-03
**예상 완료**: 2026-02-27
**상태**: 🚀 Ready to Code
