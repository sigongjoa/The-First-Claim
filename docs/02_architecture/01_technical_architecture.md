# PROJECT: OVERRIDE - 기술 아키텍처

## 시스템 개요

PROJECT: OVERRIDE는 4개 주요 컴포넌트로 구성되어 있습니다. 이 문서를 읽으며 **개발자로서 구조적 사고를 훈련**하세요.

```
┌─────────────────────────────────────────────────────────────────┐
│                     PROJECT OVERRIDE 시스템                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Client Layer (게임 UI)                                   │  │
│  │  - Unity / Web Framework (React)                         │  │
│  │  - 배틀 인터페이스, 블록 조립 시스템, 이펙트            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↑                                   │
│                            REST/WS                              │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Logic Engine (AI 심사관)                                 │  │
│  │  - LLM (GPT-4 / Llama)                                   │  │
│  │  - RAG (Retrieval-Augmented Generation)                  │  │
│  │  - 답안 채점 및 반박 로직                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↑                                   │
│                            API                                  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Knowledge Base (법률 데이터베이스)                        │  │
│  │  - Vector DB (Pinecone / Weaviate)                       │  │
│  │  - 민법, 특허법, 판례 저장소                            │  │
│  │  - 기출문제 데이터셋                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Knowledge Base (법률 데이터베이스)

### A. 데이터 구조

#### 1.1 민법 데이터

```python
class CivilLawKnowledge:
    """민법 조문 및 판례 저장소"""

    def __init__(self):
        self.statutes = {
            "제1조": {
                "title": "법의 적용",
                "content": "사법(私法)에 관하여 법률에 규정이 없을 때에는 관례에 따르고...",
                "tags": ["기본", "법의_효력"],
                "related_cases": ["대법원 2020다123456"]
            },
            "제197조": {
                "title": "취득시효",
                "content": "20년간 소유의 의사로 평온하고 공연하게 타인의 물건을 점유한 자는...",
                "tags": ["물권", "시효", "취득"],
                "requirements": ["선의", "평온성", "공연성", "20년"],
                "embedding": [...],  # Vector 임베딩
            }
        }

        self.precedents = {
            "대법원 2020다250000": {
                "case_name": "취득시효 성립 요건",
                "facts": "...",  # 사실관계
                "holdings": "...",  # 판시사항
                "keywords": ["취득시효", "선의", "선의의제"],
                "embedding": [...]
            }
        }
```

#### 1.2 특허법 데이터

```python
class PatentLawKnowledge:
    """특허 요건 및 심사 기준 저장소"""

    def __init__(self):
        self.requirements = {
            "신규성": {
                "definition": "선행기술에 없는 발명",
                "standards": [
                    "공개된 선행기술",
                    "한국 내 사용 기술",
                    "공개된 특허문헌"
                ],
                "exceptions": ["선출원 예외"],
                "keywords": ["선행기술", "공개", "알려짐"]
            },
            "진보성": {
                "definition": "선행기술로부터 용이하게 도출될 수 없는 발명",
                "assessment_factors": [
                    "기술 분야의 교지 수준",
                    "선행기술의 교시 가능성",
                    "결과의 비자명성"
                ],
                "keywords": ["교시", "암시", "동기", "기술적_효과"]
            }
        }

        self.rejection_reasons = {
            "OA_001": {
                "reason": "신규성 상실",
                "standard": "특허법 제29조",
                "counter_arguments": [
                    "공개되지 않음",
                    "기술분야 다름",
                    "특정 과제에 한정됨"
                ]
            }
        }
```

### B. Vector DB 구조

```python
class VectorDatabase:
    """의미론적 검색을 위한 벡터 데이터베이스"""

    def __init__(self):
        # Pinecone 또는 Weaviate 사용
        self.db = PineconeIndex(
            index_name="patent_law_vector_db",
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine"
        )

    def store_statute(self, statute_id, content, embedding):
        """법 조문을 벡터로 저장"""
        self.db.upsert(
            id=statute_id,
            values=embedding,
            metadata={
                "type": "statute",
                "content": content,
                "source": "민법" or "특허법"
            }
        )

    def semantic_search(self, query, top_k=5):
        """의미론적 유사성으로 관련 법 조문 검색"""
        query_embedding = self.encoder.encode(query)
        results = self.db.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return results
```

**검색 예시:**

```python
# 플레이어가 "이 토지를 오래 점유했으면 소유권을 얻을 수 있나?"라고 질문
query = "장기 점유로 인한 소유권 취득"

# 벡터 DB가 자동으로 관련 조문 검색
results = vector_db.semantic_search(query)
# → 민법 제197조 (취득시효), 제198조 (부동산 등기) 등이 검색됨
```

---

## 2. Logic Engine (AI 심사관)

### A. LLM 기반 답안 평가

```python
class AIExaminer:
    """변리사 시험을 채점하는 AI 심사관"""

    def __init__(self, llm_model="gpt-4"):
        self.llm = LLMClient(model=llm_model)
        self.knowledge_base = VectorDatabase()

    def evaluate_answer(self, problem, player_answer):
        """
        플레이어의 답안을 평가하고 피드백 생성

        Args:
            problem: 기출문제 객체
            player_answer: 플레이어의 법적 주장

        Returns:
            EvaluationResult (점수, 피드백, 반박 논거)
        """

        # 1단계: 관련 법 조문 및 판례 검색 (RAG)
        context = self.knowledge_base.semantic_search(
            problem.facts + player_answer
        )

        # 2단계: 프롬프트 구성
        prompt = f"""
너는 깐깐한 변리사 시험 심사관이다.

[문제]
{problem.description}

[사실관계]
{problem.facts}

[플레이어의 답안]
{player_answer}

[참고: 관련 법 조문 및 판례]
{self._format_context(context)}

너의 역할:
1. 플레이어의 답안이 법적으로 타당한가를 판정한다.
2. 만약 틀렸다면, 어떤 부분이 잘못되었는지 명확히 한다.
3. 플레이어가 놓친 법적 개념이 무엇인지 지적한다.
4. 다음과 같은 JSON 형식으로 응답한다:

{{
    "verdict": "정답" or "오답",
    "score": 0-100,
    "explanation": "이유 설명",
    "missing_elements": ["요소1", "요소2"],
    "counter_argument": "너의 답안이 틀린 이유",
    "correct_answer": "올바른 답변",
    "related_precedent": "참고 판례"
}}
"""

        # 3단계: LLM 응답 생성
        response = self.llm.generate(prompt)
        evaluation = json.loads(response)

        return EvaluationResult(evaluation)

    def _format_context(self, search_results):
        """검색된 판례와 조문을 포맷팅"""
        formatted = []
        for result in search_results:
            formatted.append(f"- {result['content']}")
        return "\n".join(formatted)
```

### B. RAG (Retrieval-Augmented Generation)

```python
class RAGSystem:
    """검색 기반 생성 시스템"""

    def __init__(self):
        self.vector_db = VectorDatabase()
        self.llm = LLMClient()

    def generate_with_context(self, problem, max_relevant_docs=5):
        """
        문제와 관련된 법 조문/판례를 먼저 검색한 후,
        그것을 바탕으로 AI가 답변을 생성

        Process:
        1. Vector DB에서 관련 자료 검색 (Retrieval)
        2. 검색된 자료 + 문제 → LLM 입력 (Augmentation)
        3. LLM이 답변 생성 (Generation)
        """

        # Step 1: Retrieval
        relevant_docs = self.vector_db.semantic_search(
            problem.description,
            top_k=max_relevant_docs
        )

        # Step 2: Augmentation
        context = "\n".join([doc['content'] for doc in relevant_docs])
        augmented_prompt = f"""
[관련 법적 자료]
{context}

[문제]
{problem.description}

위의 자료를 참고하여 다음을 설명하시오:
1. 이 문제가 다루는 법적 개념
2. 적용되는 법 조문
3. 관련된 판례
4. 최종 판정
"""

        # Step 3: Generation
        response = self.llm.generate(augmented_prompt)
        return response
```

**RAG의 이점:**

| 기존 방식 | RAG 방식 |
|----------|---------|
| "너는 모든 법을 알아야 한다" | "관련된 법만 검색해서 사용하면 된다" |
| LLM이 환상적 정보 생성 가능 | 검색된 법 조문을 바탕으로 신뢰할 수 있는 답변 생성 |
| 최신 판례 적용 어려움 | DB를 업데이트하면 최신 판례 자동 반영 |

---

## 3. Client Layer (게임 UI)

### A. 게임 엔진 선택지

#### 옵션 1: Unity (고사양)

```csharp
using UnityEngine;
using UnityEngine.UI;

public class LegalBattleUI : MonoBehaviour
{
    [SerializeField] private Text aiExaminerStatement;
    [SerializeField] private InputField playerAnswerInput;
    [SerializeField] private Button submitButton;
    [SerializeField] private ParticleSystem victoryEffect;

    private RestClient client;
    private LegalBattleController controller;

    void Start()
    {
        client = new RestClient("http://localhost:8000");
        submitButton.onClick.AddListener(OnSubmitAnswer);
    }

    void OnSubmitAnswer()
    {
        string playerAnswer = playerAnswerInput.text;

        // 백엔드에 답안 전송
        client.Post("/evaluate", new { answer = playerAnswer }, (response) =>
        {
            if (response.verdict == "정답")
            {
                TriggerVictoryEffect();
                DisplayFeedback(response.explanation);
            }
            else
            {
                DisplayDefeat(response.counter_argument);
            }
        });
    }

    void TriggerVictoryEffect()
    {
        // 화면 쉐이크
        StartCoroutine(ShakeScreen(0.5f));

        // 파티클 이펙트
        victoryEffect.Play();

        // 사운드
        AudioManager.Instance.Play("victory_chime");
    }
}
```

#### 옵션 2: Web Framework (경량)

```typescript
// React 기반 법률 배틀 컴포넌트
import React, { useState } from 'react';
import axios from 'axios';

interface EvaluationResult {
  verdict: 'PASS' | 'FAIL';
  score: number;
  explanation: string;
  counter_argument: string;
}

const LegalBattleComponent: React.FC = () => {
  const [playerAnswer, setPlayerAnswer] = useState('');
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);

    try {
      const response = await axios.post('/api/evaluate', {
        answer: playerAnswer
      });

      setResult(response.data);

      // 승리 이펙트
      if (response.data.verdict === 'PASS') {
        triggerVictoryAnimation();
      }
    } catch (error) {
      console.error('Evaluation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="legal-battle">
      <div className="examiner-statement">
        {/* AI 심사관의 공격 메시지 */}
      </div>
      <textarea
        value={playerAnswer}
        onChange={(e) => setPlayerAnswer(e.target.value)}
        placeholder="당신의 법적 주장을 입력하세요..."
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? '평가 중...' : '제출'}
      </button>
      {result && <FeedbackDisplay result={result} />}
    </div>
  );
};
```

### B. 주요 UI 컴포넌트

```python
# UI 컴포넌트 구조 (아키텍처)

class UIComponent:
    """모든 UI 컴포넌트의 기본 클래스"""
    def render(self): pass
    def on_input(self, user_input): pass
    def on_event(self, event): pass


class ProblemDisplayPanel(UIComponent):
    """기출문제를 표시하는 패널"""
    def __init__(self, problem):
        self.problem = problem

    def render(self):
        return f"""
        ┌────────────────────────────────────┐
        │ {self.problem.exam_year}년 변리사 시험 │
        │ 문제번호: {self.problem.number}        │
        ├────────────────────────────────────┤
        │ {self.problem.description}            │
        └────────────────────────────────────┘
        """


class ClaimBuildingPanel(UIComponent):
    """청구항 블록을 조립하는 패널"""
    def __init__(self):
        self.selected_blocks = []

    def add_block(self, block_element):
        self.selected_blocks.append(block_element)
        self.validate()

    def validate(self):
        required = ['요소', '연결', '기능']
        missing = set(required) - set(b.type for b in self.selected_blocks)
        if missing:
            raise ValidationError(f"누락된 요소: {missing}")


class BattleLog(UIComponent):
    """배틀 기록을 표시"""
    def __init__(self):
        self.logs = []

    def add_message(self, speaker, message, result=None):
        self.logs.append({
            'speaker': speaker,
            'message': message,
            'result': result,
            'timestamp': datetime.now()
        })
        self.render()

    def render(self):
        for log in self.logs:
            if log['result'] == 'success':
                print(f"✓ {log['speaker']}: {log['message']}")
            elif log['result'] == 'failure':
                print(f"✗ {log['speaker']}: {log['message']}")
            else:
                print(f"→ {log['speaker']}: {log['message']}")
```

---

## 4. 전체 시스템 흐름

### A. 사용자 상호작용 플로우

```
User Input (플레이어가 답변 입력)
    ↓
[Client] 입력값 검증
    ↓
[API] REST 요청 전송: POST /api/evaluate
    ↓
[Logic Engine] 답안 평가
    ├─ Vector DB에서 관련 판례 검색
    ├─ LLM이 평가 로직 실행
    └─ 피드백 생성
    ↓
[Client] 응답 수신
    ├─ 정답 → 승리 이펙트 + XP 획득
    └─ 오답 → 피드백 표시 + 다시 시도
    ↓
Game State Update (플레이어 레벨, 경험치 업데이트)
```

### B. 데이터 흐름 (데이터 구조)

```python
class GameState:
    """게임 전체 상태 관리"""

    def __init__(self):
        self.player = PlayerProfile()
        self.current_problem = Problem()
        self.battle_log = BattleLog()
        self.knowledge_base = VectorDatabase()


class PlayerProfile:
    """플레이어 프로필"""
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.civil_law_level = 0  # 민법 숙련도 0-100
        self.patent_law_level = 0  # 특허법 숙련도 0-100
        self.accuracy_rate = 0.0  # 정답률
        self.solved_problems = []  # 풀어본 문제 목록


class Problem:
    """기출문제"""
    def __init__(self, exam_year, number, category, description, facts):
        self.exam_year = exam_year
        self.number = number
        self.category = category  # "취득시효" or "신규성" etc.
        self.description = description
        self.facts = facts
        self.correct_answer = None
        self.keywords = []  # 정답에 포함되어야 할 핵심 키워드


class EvaluationResult:
    """평가 결과"""
    def __init__(self, verdict, score, explanation):
        self.verdict = verdict  # "PASS" or "FAIL"
        self.score = score  # 0-100
        self.explanation = explanation
        self.correct_answer = None
        self.keywords_matched = []  # 플레이어가 맞힌 핵심 키워드
        self.keywords_missed = []  # 플레이어가 놓친 핵심 키워드
```

---

## 5. 데이터 파이프라인 (Data Pipeline)

### A. 초기 데이터 수집 (Data Collection)

```python
class DataPipeline:
    """법률 데이터 수집 및 처리"""

    def __init__(self):
        self.scraper = WebScraper()
        self.embedder = Embedder(model="openai")
        self.vector_db = VectorDatabase()

    def collect_statutes(self):
        """국가법령정보센터에서 민법, 특허법 크롤링"""
        statutes = self.scraper.crawl("https://www.law.go.kr")
        return statutes

    def collect_precedents(self):
        """판례 검색 웹사이트에서 판례 데이터 수집"""
        # 예: 판례검색 (glaw.scourt.go.kr)
        precedents = self.scraper.crawl("https://glaw.scourt.go.kr")
        return precedents

    def collect_exam_questions(self):
        """변리사 시험 기출문제 수집"""
        # 2015년 ~ 2024년 문제 수집
        questions = []
        for year in range(2015, 2025):
            questions.extend(self.scraper.crawl(f"exam_site/{year}"))
        return questions

    def embed_documents(self, documents):
        """문서들을 벡터로 변환"""
        embeddings = []
        for doc in documents:
            embedding = self.embedder.encode(doc['content'])
            embeddings.append({
                'id': doc['id'],
                'embedding': embedding,
                'metadata': doc
            })
        return embeddings

    def store_to_vector_db(self, embeddings):
        """벡터 DB에 저장"""
        for item in embeddings:
            self.vector_db.store(
                id=item['id'],
                vector=item['embedding'],
                metadata=item['metadata']
            )

    def run_pipeline(self):
        """전체 파이프라인 실행"""
        print("수집 중: 법 조문...")
        statutes = self.collect_statutes()

        print("수집 중: 판례...")
        precedents = self.collect_precedents()

        print("수집 중: 기출문제...")
        questions = self.collect_exam_questions()

        all_documents = statutes + precedents + questions

        print("임베딩 중...")
        embeddings = self.embed_documents(all_documents)

        print("벡터 DB에 저장 중...")
        self.store_to_vector_db(embeddings)

        print("✓ 데이터 파이프라인 완료!")
```

---

## 6. 시스템 배포 (Deployment)

### A. 마이크로서비스 아키텍처

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 백엔드 서버
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${OPENAI_API_KEY}
      - VECTOR_DB_URL=${PINECONE_URL}
    depends_on:
      - vector_db

  # 벡터 데이터베이스
  vector_db:
    image: pinecone  # 또는 weaviate
    ports:
      - "6379:6379"

  # 프론트엔드
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000
```

---

## 7. 개발자 학습 체크리스트

이 아키텍처를 이해하는 것이 곧 **구조적 사고 훈련**입니다.

- [ ] Vector DB가 왜 필요한가? (의미론적 검색 vs 키워드 검색)
- [ ] RAG 시스템의 장점을 설명할 수 있는가?
- [ ] 프롬프트 엔지니어링이 법률 평가에 미치는 영향은?
- [ ] 왜 클라이언트와 백엔드를 분리하는가?
- [ ] 마이크로서비스 vs 모놀리식 아키텍처의 트레이드오프는?

---

최종 목표: **이 시스템을 이해하고 구축하는 과정이 곧 변리사 시험 합격의 지름길이다.**
