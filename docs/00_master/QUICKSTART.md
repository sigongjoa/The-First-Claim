# 🚀 QUICKSTART - 5분 안에 시작하기

**PROJECT: OVERRIDE를 빠르게 시작하는 완벽한 가이드입니다.**

## 📋 필수 요구사항

- Python 3.12+ (`python --version`)
- Ollama 설치됨 (로컬 LLM)
- 기본 터미널 명령어 이해

## 1️⃣ 저장소 클론 (1분)

```bash
git clone https://github.com/sigongjoa/The-First-Claim.git
cd The-First-Claim
```

## 2️⃣ 의존성 설치 (2분)

```bash
pip install -r requirements.txt
```

**문제 발생 시:**
```bash
pip install --break-system-packages -r requirements.txt
```

## 3️⃣ Ollama 시작 (별도 터미널에서)

```bash
# Ollama 서버 시작
ollama serve

# 새 터미널에서 모델 확인 (선택사항)
ollama pull nomic-embed-text
ollama pull mistral  # 또는 다른 모델
```

⚠️ **중요**: Ollama가 반드시 실행 중이어야 합니다!

## 4️⃣ 애플리케이션 시작 (1분)

```bash
python src/main.py
```

🎉 **완료!** API가 http://localhost:8000 에서 실행 중입니다.

---

## 🧪 테스트 실행 (1분)

```bash
# 모든 테스트
pytest tests/ -v

# 빠른 테스트 (스트레스 테스트 제외)
pytest tests/ -k "not stress" -v

# 특정 파일만
pytest tests/test_game.py -v
```

---

## 📡 API 테스트

### 헬스 체크
```bash
curl http://localhost:8000/api/health
```

### 게임 세션 생성
```bash
curl -X POST http://localhost:8000/api/game/session \
  -H "Content-Type: application/json" \
  -d '{"player_name": "테스트", "level_id": 1}'
```

### 의미론적 검색
```bash
curl "http://localhost:8000/api/search?query=취득시효&top_k=5"
```

---

## 📁 중요한 파일/폴더

```
The-First-Claim/
├── src/
│   ├── main.py              ← 애플리케이션 시작점
│   ├── api/server.py        ← API 엔드포인트
│   └── game/engine.py       ← 게임 로직
├── tests/                   ← 테스트 스위트
├── docs/                    ← 문서
└── requirements.txt         ← 의존성
```

---

## ✅ 문제 해결

### "ModuleNotFoundError: No module named..."
→ `pip install --break-system-packages -r requirements.txt`

### "Connection refused" (Ollama)
→ Ollama가 실행 중인지 확인하세요: `ollama serve`

### 테스트 실패
→ Ollama가 실행 중인지 확인 후 `pytest tests/test_api_server.py -v` 실행

---

## 📚 다음 단계

✅ **기본 이해**
- [메인 README.md](../../README.md) 읽기

✅ **더 깊이 있게**
- [프로젝트 개요](../01_overview/01_project_overview.md)
- [기술 아키텍처](../02_architecture/01_technical_architecture.md)

✅ **개발 시작**
- [웹 설정 가이드](../03_implementation/02_web_setup.md)
- [테스팅 가이드](../04_testing/02_testing_guide.md)

✅ **전체 문서 보기**
- [문서 인덱스](../INDEX.md)

---

## 💡 유용한 명령어

```bash
# 코드 포맷팅
black src/ tests/

# 타입 체크
mypy src/

# 린트 검사
flake8 src/ tests/

# 전체 품질 검사
black src/ && mypy src/ && flake8 src/
```

---

**더 자세한 정보는 [문서 인덱스](../INDEX.md)를 확인하세요!**

**마지막 업데이트**: 2025-12-08
