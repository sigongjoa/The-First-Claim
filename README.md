# PROJECT: OVERRIDE - 특허 청구항 검증 게임 (Patent Claim Validation Game)

**한국 변리사 시험 대비를 위한 인터랙티브 학습 게임**

## 🎮 프로젝트 개요

PROJECT: OVERRIDE는 한국 특허청 변리사 시험 제1차 시험 대비를 위한 혁신적인 인터랙티브 게임 기반 학습 플랫폼입니다. 특허법 및 민법 지식을 게임을 통해 습득하고, 청구항 검증 및 법률 배틀을 통해 실무 능력을 강화합니다.

### 핵심 기능
- **🎯 청구항 검증**: 특허 청구항의 유효성을 AI 기반으로 검증
- **⚖️ 법률 배틀**: 법률 지식을 기반으로 한 인터랙티브 배틀 시스템
- **📚 의미론적 검색**: RAG(Retrieval-Augmented Generation) 기반 법률 조문 검색
- **🤖 로컬 LLM**: Ollama 기반 로컬 LLM으로 API 비용 최소화
- **🔄 세션 관리**: 스레드 안전 세션 관리 및 영속성

## 📋 프로젝트 구조

```
The-First-Claim/
├── README.md                 # 메인 문서 (이 파일)
├── docs/                     # 문서 폴더
│   ├── 00_master/           # 마스터 문서
│   ├── 01_overview/         # 프로젝트 개요
│   ├── 02_architecture/     # 기술 아키텍처
│   ├── 03_implementation/   # 구현 가이드
│   ├── 04_testing/          # 테스트 문서
│   ├── 05_learning/         # 학습 자료
│   └── 06_reference/        # 참고 자료
├── src/                      # 소스 코드
│   ├── api/                 # FastAPI 서버
│   ├── dsl/                 # DSL 엔진
│   ├── game/                # 게임 로직
│   ├── knowledge_base/      # 지식 베이스
│   ├── storage/             # 세션 저장소
│   ├── monitoring/          # 모니터링
│   └── utils/               # 유틸리티
├── tests/                    # 테스트 (489개)
└── requirements.txt          # 의존성
```

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.12+
- Ollama (로컬 LLM)

### 설치
```bash
git clone https://github.com/sigongjoa/The-First-Claim.git
cd The-First-Claim
pip install -r requirements.txt
ollama serve  # 별도 터미널에서
python src/main.py
```

## 📊 현재 상태
- **테스트**: 474/489 passing (96.9%)
- **Phase**: C.4 완료 (고급 테스팅)
- **코드 품질**: A (MyPy, Black, Flake8)

## 📚 문서 구조

### 마스터 가이드
- [QUICKSTART.md](docs/00_master/QUICKSTART.md) - 5분 시작 가이드

### 프로젝트 이해
- [프로젝트 개요](docs/01_overview/)
- [기술 아키텍처](docs/02_architecture/)

### 개발
- [구현 가이드](docs/03_implementation/)
- [테스트 가이드](docs/04_testing/)

### 학습
- [학습 자료](docs/05_learning/)

### 참고
- [참고 자료](docs/06_reference/)

## 🔧 기술 스택

| 영역 | 기술 |
|------|------|
| **API** | FastAPI, Pydantic |
| **데이터** | ChromaDB, SQLAlchemy |
| **LLM** | Ollama (로컬) |
| **테스트** | pytest, hypothesis, mutmut |
| **품질** | MyPy, Black, Flake8 |

## 🧪 테스트 실행

```bash
pytest tests/ -v           # 모든 테스트
pytest tests/test_game.py  # 특정 파일
pytest --cov=src          # 커버리지
```

## 📖 상세 문서

전체 문서는 [docs/ 폴더](docs/)를 참고하세요.

---
**상태**: 🟢 활발한 개발 중 | **마지막 업데이트**: 2025-12-08
