# PROJECT: OVERRIDE - 단계별 개발 및 학습 로드맵

## 개요

이 로드맵을 따라가는 것이 곧 **변리사 시험 합격을 위한 수험 계획표**입니다.

단순 개발 계획이 아니라, **개발 단계 = 학습 단계**인 맞춤형 로드맵입니다.

```
Phase 1: 민법의 기초 (로직 게이트)
    ↓ (3-4주)
Phase 2: 특허법의 구조 (시스템 아키텍처)
    ↓ (4-5주)
Phase 3: 판례의 시각화 (데이터베이스 구축)
    ↓ (5-6주)
Phase 4: Final Override (시험장 배포)
    ↓
변리사 시험 합격 + AI Legal Tech 포트폴리오 완성 🚀
```

---

## Phase 1: 민법의 기초 (The Logic Gates)

### 1-1. 프로젝트 초기화

#### 개발 목표
- Python 프로젝트 구조 설정
- Git 저장소 초기화
- 간단한 텍스트 배틀 프로토타입 구현

#### 개발 작업 (Dev)

```bash
# 프로젝트 폴더 생성
mkdir The-First-Claim
cd The-First-Claim

# Python 가상 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install openai python-dotenv pytest

# Git 초기화
git init
git add .
git commit -m "Initial commit: PROJECT OVERRIDE"
```

#### 코드 구조

```
The-First-Claim/
├── src/
│   ├── __init__.py
│   ├── main.py              # 메인 진입점
│   ├── game_engine.py       # 게임 로직 엔진
│   ├── knowledge_base.py    # 민법 기초 데이터
│   └── ai_examiner.py       # AI 심사관 (Phase 1: 간단한 버전)
├── tests/
│   ├── test_game_logic.py
│   └── test_evaluator.py
├── docs/
├── data/
│   ├── civil_law_statutes.json  # 민법 조문 (제1~184조)
│   └── exam_questions_phase1.json
├── requirements.txt
└── .gitignore
```

### 1-2. 민법 데이터 모델링

#### 학습 목표
**민법총칙(제1조~제184조) 정복**

특히 다음 내용에 집중:
- 제1조: 법의 적용
- 제3조: 법인
- 제5조 ~ 제27조: 권리 능력
- 제105조 ~ 제184조: 소멸시효

#### 개발 작업

```python
# src/knowledge_base.py

class CivilLawStatute:
    """민법 조문의 기본 구조"""

    def __init__(self, article_number, title, content, tags=None):
        self.article_number = article_number  # e.g., "제197조"
        self.title = title                     # e.g., "취득시효"
        self.content = content                 # 조문 전문
        self.tags = tags or []                 # 주제 태그
        self.related_articles = []             # 관련 조문
        self.precedents = []                   # 관련 판례


class CivilLawBase:
    """민법 데이터베이스"""

    def __init__(self):
        self.statutes = {}

    def load_statutes(self):
        """JSON에서 조문 로드"""
        with open('data/civil_law_statutes.json') as f:
            data = json.load(f)
            for statute in data:
                self.statutes[statute['number']] = CivilLawStatute(**statute)

    def get_statute(self, article_number):
        """조문 검색"""
        return self.statutes.get(article_number)

    def get_related_statutes(self, article_number, depth=1):
        """관련 조문 찾기"""
        statute = self.get_statute(article_number)
        return statute.related_articles
```

#### 데이터 예시

```json
// data/civil_law_statutes.json

[
  {
    "number": "제1조",
    "title": "법의 적용",
    "content": "사법(私法)에 관하여 법률에 규정이 없을 때에는 관례에 따르고, 관례가 없을 때에는 조리(條理)에 따른다.",
    "tags": ["기본", "법의효력"],
    "related_articles": ["제2조", "제3조"],
    "difficulty": 1
  },
  {
    "number": "제197조",
    "title": "취득시효",
    "content": "20년간 소유의 의사로 평온하고 공연하게 타인의 부동산을 점유한 자는 그 소유권을 취득한다.",
    "tags": ["물권", "시효", "취득"],
    "requirements": ["선의성", "평온성", "공연성", "20년"],
    "related_articles": ["제198조", "제204조"],
    "difficulty": 3
  }
]
```

### 1-3. 간단한 텍스트 배틀 구현

#### 개발 목표
**If-Then 논리를 코드로 구현**

```python
# src/game_engine.py

class SimpleLegalBattle:
    """Phase 1: 간단한 텍스트 배틀"""

    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.player_hp = 100
        self.ai_hp = 100

    def evaluate_answer(self, problem_facts, player_answer):
        """
        플레이어의 답변을 단순한 규칙으로 평가

        Example:
        문제: "A가 20년 동안 타인의 토지를 점유했다. 소유권을 취득할 수 있는가?"

        if player_answer contains "취득시효":
            and problem_facts contains "20년 점유":
            and problem_facts contains "선의성":
            then return "PASS"
        else:
            return "FAIL"
        """

        required_keywords = self._extract_required_keywords(problem_facts)

        for keyword in required_keywords:
            if keyword not in player_answer:
                return {
                    'verdict': 'FAIL',
                    'reason': f"누락된 핵심 개념: {keyword}",
                    'hint': self._get_hint(keyword)
                }

        return {
            'verdict': 'PASS',
            'explanation': "정답입니다!",
            'xp_gained': 10
        }

    def _extract_required_keywords(self, facts):
        """사실관계에서 필요한 법적 개념 추출"""
        keywords = []

        if "20년" in facts:
            keywords.append("취득시효")
        if "선의" in facts:
            keywords.append("선의성")

        return keywords

    def _get_hint(self, keyword):
        """플레이어에게 힌트 제공"""
        hints = {
            "취득시효": "민법 제197조를 확인하세요.",
            "선의성": "취득시효의 성립 요건을 다시 검토하세요."
        }
        return hints.get(keyword, "관련 조문을 찾아보세요.")
```

#### 테스트 코드

```python
# tests/test_game_logic.py

import pytest
from src.game_engine import SimpleLegalBattle
from src.knowledge_base import CivilLawBase

def setup_battle():
    kb = CivilLawBase()
    kb.load_statutes()
    return SimpleLegalBattle(kb)

def test_acquisition_by_prescription():
    """취득시효 문제 테스트"""
    battle = setup_battle()

    problem_facts = """
    A가 B의 토지를 20년 동안 공연하고 평온하게,
    소유의 의사로 점유했다.
    """

    # 정답
    player_answer = "취득시효에 의해 소유권 취득 가능 (민법 제197조)"
    result = battle.evaluate_answer(problem_facts, player_answer)
    assert result['verdict'] == 'PASS'

    # 오답
    player_answer = "소유권을 취득할 수 없다"
    result = battle.evaluate_answer(problem_facts, player_answer)
    assert result['verdict'] == 'FAIL'
    assert "취득시효" in result['reason']
```

### 1-4. 점진적 문제 난이도 증가

#### 문제 레벨 설정

| 난이도 | 특징 | 예시 |
|--------|------|------|
| ⭐ | 한 가지 개념만 포함 | "A가 20년 점유 → 취득시효?" |
| ⭐⭐ | 두 가지 조건 | "A가 선의로 20년 점유 → 취득시효?" |
| ⭐⭐⭐ | 예외 사항 포함 | "A가 무효인 계약으로 점유했다. 취득시효?" |

---

## Phase 2: 특허법의 구조 (System Architecture)

### 2-1. 특허법 데이터 모델링

#### 학습 목표
**특허 요건 완벽 이해: 신규성, 진보성, 명세서**

#### 개발 작업

```python
# src/patent_law_base.py

class PatentRequirement:
    """특허 요건의 기본 구조"""

    def __init__(self, name, definition, keywords, assessment_standards):
        self.name = name  # e.g., "신규성"
        self.definition = definition
        self.keywords = keywords
        self.assessment_standards = assessment_standards


class PatentLawBase:
    """특허법 데이터베이스"""

    def __init__(self):
        self.requirements = {
            "신규성": PatentRequirement(
                name="신규성",
                definition="선행기술에 없는 발명",
                keywords=["선행기술", "공개", "공지"],
                assessment_standards=[
                    "한국에서 공개된 선행기술",
                    "출원일 이전의 공개",
                    "문헌으로 확인 가능"
                ]
            ),
            "진보성": PatentRequirement(
                name="진보성",
                definition="선행기술로부터 용이하게 도출될 수 없는 발명",
                keywords=["교시", "암시", "동기", "기술적 효과"],
                assessment_standards=[
                    "기술분야 종사자의 지식 수준",
                    "선행기술의 교시 가능성",
                    "예측 가능성의 범위"
                ]
            )
        }

    def check_novelty(self, invention, prior_art):
        """신규성 검토"""
        for prior in prior_art:
            if self._is_identical(invention, prior):
                return False
        return True

    def check_inventive_step(self, invention, prior_arts):
        """진보성 검토"""
        # Phase 2에서는 단순 로직
        # Phase 3에서는 AI 기반으로 복잡하게

        # 규칙 1: 선행기술 1개와 완전히 다르면 진보성 있음
        for prior in prior_arts:
            if self._is_substantially_different(invention, prior):
                return True

        return False
```

### 2-2. 청구항 크래프팅 시스템

#### 개발 목표
**블록 조립 방식의 청구항 작성 프로토타입**

```python
# src/claim_builder.py

class ClaimBlock:
    """청구항을 구성하는 기본 블록"""

    def __init__(self, block_type, content):
        self.block_type = block_type  # "요소", "연결", "기능", "효과"
        self.content = content

    def validate(self):
        """각 블록의 유효성 검증"""
        if not self.content:
            raise ValueError(f"블록 {self.block_type}의 내용이 비어있습니다")


class ClaimBuilder:
    """청구항 빌더"""

    def __init__(self):
        self.blocks = []

    def add_element(self, element):
        """구성요소 추가"""
        self.blocks.append(ClaimBlock("요소", element))

    def add_connection(self, connection):
        """연결 관계 추가"""
        self.blocks.append(ClaimBlock("연결", connection))

    def add_function(self, function):
        """기능 추가"""
        self.blocks.append(ClaimBlock("기능", function))

    def validate_claim(self):
        """
        All Elements Rule: 모든 필수 요소가 포함되어 있는가?
        """
        required = {"요소", "연결", "기능"}
        present = {block.block_type for block in self.blocks}

        missing = required - present

        if missing:
            raise ValueError(f"누락된 요소: {missing}")

        return True

    def build(self):
        """청구항 생성"""
        self.validate_claim()

        claim_text = " ".join([block.content for block in self.blocks])
        return {
            'text': claim_text,
            'structure': [block.block_type for block in self.blocks],
            'validation': True
        }


# 사용 예
builder = ClaimBuilder()
builder.add_element("A 부품과 B 부품으로 구성된")
builder.add_connection("상기 A 부품은 B 부품과 연결되어")
builder.add_function("발명의 목적을 달성한다")
claim = builder.build()
```

### 2-3. 판례 검색 시스템 (기초)

#### 개발 목표
**판례 크롤링 및 기초 검색 구현**

```python
# src/precedent_crawler.py

class PrecedentCrawler:
    """판례 웹사이트에서 데이터 크롤링"""

    def __init__(self):
        self.precedents = []

    def crawl_patent_precedents(self, year_range=(2015, 2024)):
        """특허 판례 크롤링"""
        for year in range(year_range[0], year_range[1] + 1):
            # 판례검색 웹사이트 크롤링 (requests + BeautifulSoup)
            url = f"https://example.com/precedents/{year}"
            response = requests.get(url)
            # HTML 파싱...
            pass

    def parse_precedent(self, html):
        """판례 파싱"""
        return {
            'case_id': '대법원 2020다123456',
            'case_name': '특허권 침해 사건',
            'decision_date': '2020-01-15',
            'facts': '...',  # 사실관계
            'holdings': '...',  # 판시사항
            'keywords': ['특허', '침해', '손해배상']
        }

    def save_to_json(self, filename):
        """JSON으로 저장"""
        with open(f'data/{filename}', 'w') as f:
            json.dump(self.precedents, f, ensure_ascii=False, indent=2)
```

---

## Phase 3: 판례의 시각화 (Database)

### 3-1. Vector DB 설정 및 RAG 연동

#### 개발 목표
- OpenAI Embedding API로 문서 벡터화
- Pinecone 또는 Weaviate 연동
- RAG 시스템 동작

#### 개발 작업

```python
# src/vector_db.py

import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

class VectorDatabaseManager:
    """벡터 DB 관리"""

    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.index_name = "patent-law-db"

    def initialize_index(self):
        """인덱스 생성"""
        self.pc.create_index(
            name=self.index_name,
            dimension=1536,  # OpenAI embedding
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-west-2"
            )
        )

    def embed_and_store(self, documents):
        """문서를 임베딩하여 저장"""
        index = self.pc.Index(self.index_name)

        for doc in documents:
            # 임베딩 생성
            embedding = self.client.embeddings.create(
                input=doc['content'],
                model="text-embedding-3-small"
            ).data[0].embedding

            # 저장
            index.upsert(
                vectors=[(
                    doc['id'],
                    embedding,
                    {
                        'text': doc['content'],
                        'type': doc['type'],  # statute, precedent, question
                        'source': doc['source']
                    }
                )]
            )

    def semantic_search(self, query, top_k=5):
        """의미론적 검색"""
        index = self.pc.Index(self.index_name)

        query_embedding = self.client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        ).data[0].embedding

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        return results
```

### 3-2. AI 심사관 고도화 (RAG 기반)

#### 개발 목표
**LLM + RAG로 현실적인 시험 채점 시뮬레이션**

```python
# src/ai_examiner_advanced.py

from src.vector_db import VectorDatabaseManager

class AdvancedAIExaminer:
    """RAG 기반 AI 심사관"""

    def __init__(self):
        self.vector_db = VectorDatabaseManager()
        self.llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def evaluate_answer_with_rag(self, problem, player_answer):
        """
        1. 문제와 관련된 판례 검색 (RAG)
        2. LLM이 판례를 참고하여 평가
        3. 피드백 생성
        """

        # Step 1: 관련 판례 검색
        query = f"{problem['description']} {problem['facts']}"
        relevant_docs = self.vector_db.semantic_search(query, top_k=5)

        # Step 2: 프롬프트 구성
        prompt = self._build_prompt(problem, player_answer, relevant_docs)

        # Step 3: LLM 호출
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "너는 깐깐한 변리사 시험 심사관이다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        evaluation = json.loads(response.choices[0].message.content)
        return evaluation

    def _build_prompt(self, problem, answer, relevant_docs):
        """프롬프트 구성"""

        context = "\n".join([
            f"- {doc['metadata']['text']}"
            for doc in relevant_docs['matches']
        ])

        return f"""
[문제]
{problem['description']}

[사실관계]
{problem['facts']}

[학생의 답안]
{player_answer}

[참고: 관련 판례 및 법 조문]
{context}

학생의 답안을 평가하고 다음 JSON 형식으로 응답하세요:
{{
    "verdict": "정답" or "오답",
    "score": 0-100,
    "explanation": "평가 이유",
    "missing_elements": ["요소1", "요소2"],
    "correct_answer": "올바른 답변"
}}
"""
```

### 3-3. UI 및 이펙트 시스템

#### 개발 목표
**게임 느낌의 UI와 시각/음향 피드백**

```python
# src/ui_effects.py

class VictoryEffect:
    """승리 이펙트"""

    @staticmethod
    def trigger_victory():
        print("\n" + "="*50)
        print("🎉 OVERRIDE SUCCESS! 🎉")
        print("="*50)
        print("\n✓ 키워드 매칭 성공!")
        print("✓ 법적 논리 타당함!")
        print("\n[경험치 +10]")
        print("[숙련도 +5%]")
        print("\n" + "="*50 + "\n")


class DefeatEffect:
    """패배 이펙트"""

    @staticmethod
    def trigger_defeat(feedback):
        print("\n" + "-"*50)
        print("❌ 판정: 패배")
        print("-"*50)
        print(f"\n심사관의 의견:\n{feedback}")
        print("\n다시 시도하세요!")
        print("-"*50 + "\n")


class BattleUI:
    """배틀 인터페이스"""

    @staticmethod
    def display_battle_screen(problem, ai_message, player_hp, ai_hp):
        """배틀 화면 표시"""

        print("\n" + "█"*60)
        print("█ 법률 배틀 중... █".center(60))
        print("█"*60)

        print(f"\n[의뢰인 사연]")
        print(f"{problem['description']}\n")

        print(f"[심사관의 공격]")
        print(f"📋 {ai_message}\n")

        print(f"[체력]")
        print(f"플레이어 HP: {'█' * (player_hp // 10)}{'░' * (10 - player_hp // 10)} {player_hp}/100")
        print(f"AI 심사관 HP: {'█' * (ai_hp // 10)}{'░' * (10 - ai_hp // 10)} {ai_hp}/100\n")

        print("[당신의 응답을 입력하세요]")
        print("-"*60 + "\n")
```

---

## Phase 4: Final Override (시험장 배포)

### 4-1. 종합 시뮬레이션

#### 개발 목표
- 2024년 기출문제 100% 커버
- 정답률 90% 이상 달성
- 배포 준비 완료

#### 개발 작업

```python
# src/final_simulation.py

class ExamSimulation:
    """최종 시험 시뮬레이션"""

    def __init__(self):
        self.ai_examiner = AdvancedAIExaminer()
        self.exam_questions = self._load_all_questions()
        self.player_stats = {
            'total_problems': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'accuracy_rate': 0
        }

    def run_full_exam(self):
        """전체 기출문제 실시간 모의고사"""

        print("\n" + "█"*60)
        print("█ PROJECT OVERRIDE - 최종 시험 시뮬레이션 시작 █".center(60))
        print("█"*60 + "\n")

        for problem in self.exam_questions:
            result = self._run_single_problem(problem)

            if result['verdict'] == '정답':
                self.player_stats['correct_answers'] += 1
            else:
                self.player_stats['incorrect_answers'] += 1

            self.player_stats['total_problems'] += 1

        self._display_final_results()

    def _run_single_problem(self, problem):
        """개별 문제 처리"""

        BattleUI.display_problem(problem)

        player_answer = input("답안: ")

        result = self.ai_examiner.evaluate_answer_with_rag(
            problem,
            player_answer
        )

        if result['verdict'] == '정답':
            VictoryEffect.trigger_victory()
        else:
            DefeatEffect.trigger_defeat(result['explanation'])

        return result

    def _display_final_results(self):
        """최종 결과 표시"""

        accuracy = (
            self.player_stats['correct_answers'] /
            self.player_stats['total_problems'] * 100
        )

        print("\n" + "═"*60)
        print("═ 최종 성적 분석 ═".center(60))
        print("═"*60)

        print(f"\n총 문제 수: {self.player_stats['total_problems']}")
        print(f"정답: {self.player_stats['correct_answers']}")
        print(f"오답: {self.player_stats['incorrect_answers']}")
        print(f"\n정답률: {accuracy:.1f}%")

        if accuracy >= 90:
            print("\n🎓 축하합니다! 변리사 시험 합격 수준입니다!")
        elif accuracy >= 80:
            print("\n📚 조금 더 학습이 필요합니다. 오답 분석을 해보세요.")
        else:
            print("\n⚠️  더 집중적인 학습이 필요합니다.")

        print("\n" + "═"*60 + "\n")
```

### 4-2. 배포 (Human Deployment)

#### 개발 목표
**개발 중단 → 시험장에 배포**

```python
# src/deployment.py

class HumanDeployment:
    """개발자 출신 변리사 수험생을 시험장에 배포"""

    def __init__(self):
        self.ai_examiner = self._install_in_mind()
        self.legal_engine = self._compress_system()

    def _install_in_mind(self):
        """AI 심사관을 머릿속에 설치"""
        print("\n[설치 중...]")
        print("✓ 민법 로직 게이트 설치 완료")
        print("✓ 특허법 시스템 아키텍처 설치 완료")
        print("✓ 판례 데이터베이스 마이그레이션 완료")
        print("\n[설치 완료]")
        print("당신의 머릿속에 'AI 심사관'이 설치되었습니다.")
        print("이제 시험장에서 맨몸으로 싸울 준비가 되었습니다.\n")
        return "READY"

    def _compress_system(self):
        """시스템을 뇌에 압축"""
        return "COMPRESSED"

    def deploy_to_exam_room(self):
        """시험장에 배포"""
        print("\n" + "🚀 "*20)
        print("\n시험장으로 이동합니다.")
        print("당신의 무기:")
        print("  1. 체계화된 민법 이해")
        print("  2. 특허법의 논리 구조 파악")
        print("  3. 판례 100개의 사례 경험")
        print("  4. AI처럼 논리적으로 생각하는 능력")
        print("\n시험지를 펴고 펜을 들었습니다.")
        print("이제 시작하세요.")
        print("\n" + "🚀 "*20)
```

---

## 타임라인 및 이정표

### 전체 타임라인

```
Week 1-3:   Phase 1 완료 (민법 기초)
            - 텍스트 배틀 프로토타입
            - 민법 조문 50개 학습 및 코드화
            - 테스트 코드 작성

Week 4-6:   Phase 2 완료 (특허법 구조)
            - 청구항 블록 시스템 완성
            - 판례 크롤링 100개
            - 신규성/진보성 평가 로직

Week 7-10:  Phase 3 완료 (판례 시각화)
            - Vector DB 설정
            - RAG 시스템 연동
            - UI 이펙트 구현
            - 2024년 기출문제 100개 통합

Week 11-12: Phase 4 및 최종 준비
            - 최종 시뮬레이션
            - 정답률 분석
            - 취약 분야 집중 학습
            - 배포 준비
```

### 핵심 이정표 체크리스트

- [ ] Week 1: Python 기본 프로젝트 구조 완성
- [ ] Week 3: 민법 조문 50개 코드화 + 테스트 통과
- [ ] Week 6: 청구항 시스템 + 판례 100개 크롤링
- [ ] Week 10: Vector DB + RAG 완전 동작
- [ ] Week 12: 최종 모의고사 정답률 90% 이상
- [ ] 시험당일: 시험장 배포 및 합격

---

## 학습 리소스

### 필수 자료

| 자료 | 용도 |
|------|------|
| 국가법령정보센터 (law.go.kr) | 법 조문 |
| 판례검색 (glaw.scourt.go.kr) | 판례 데이터 |
| 변리사 시험 기출문제 (2015-2024) | 문제 셋 |
| 대한변리사회 교재 | 참고 자료 |

### 개발 기술 스택

| 기술 | 용도 |
|------|------|
| Python 3.11+ | 백엔드 |
| OpenAI API | LLM |
| Pinecone | Vector DB |
| Pytest | 테스트 |
| Git | 버전 관리 |

---

## 성공의 정의

```
성공 = [Code Quality] × [Legal Understanding] × [Exam Score] × [Portfolio Value]
```

- **Code Quality:** 테스트 커버리지 90% 이상
- **Legal Understanding:** 기출문제 90% 정답률
- **Exam Score:** 변리사 시험 합격
- **Portfolio Value:** AI Legal Tech 포트폴리오로 활용 가능

---

최종 목표: **개발을 하다 보니 변리사가 되어 있다.** 🚀
