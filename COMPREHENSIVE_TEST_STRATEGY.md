# 종합 테스트 전략 (Comprehensive Test Strategy)

## 📋 목표
Quality Roadmap 7단계를 모두 충족하는 완벽한 테스트 체계 구축

---

## 🎯 Phase별 구현 계획

## Phase 1: 단위 및 통합 테스트 강화 (1주)

### 1.1 Python 백엔드 테스트 확대

#### 1.1.1 API 엔드포인트 테스트
**파일:** `tests/test_api_endpoints.py` (신규)

```python
# 필수 테스트 케이스
- POST /api/claims/submit
  ✓ 정상적인 청구항 제출
  ✓ 빈 청구항 거부
  ✓ 매우 긴 청구항 처리
  ✓ 특수문자 포함 청구항

- GET /api/games/{game_id}/results
  ✓ 존재하는 게임 결과 조회
  ✓ 존재하지 않는 게임 404
  ✓ 인증 없이 접근 거부

- POST /api/games/evaluate
  ✓ LLM 평가 요청
  ✓ Ollama 평가 요청
  ✓ 평가 타임아웃 처리
  ✓ API 에러 응답 형식
```

#### 1.1.2 데이터 무결성 테스트
**파일:** `tests/test_data_integrity.py` (신규)

```python
# 필수 테스트 케이스
- 청구항 저장 후 조회
  ✓ 저장된 데이터와 조회된 데이터 동일
  ✓ 인코딩 문제 없음 (특수문자, 이모지)
  ✓ 타임스탬프 정확함

- 점수 계산 정확성
  ✓ 부동소수점 오차 < 0.001
  ✓ 점수는 항상 0.0~1.0 범위
  ✓ 합계 계산이 정확함

- 동시성 테스트
  ✓ 100개 동시 청구항 저장 후 데이터 손상 없음
  ✓ 경합 조건(race condition) 없음
```

#### 1.1.3 에러 처리 테스트
**파일:** `tests/test_error_handling.py` (신규)

```python
# 필수 테스트 케이스
- LLM API 에러 처리
  ✓ API_KEY 없을 때 적절한 에러 메시지
  ✓ API 타임아웃 → 재시도
  ✓ Rate limit → 대기 후 재시도

- Ollama 서버 에러
  ✓ 서버 다운 → 명확한 에러
  ✓ 모델 로드 실패 → 자동 재시도
  ✓ JSON 파싱 실패 → 로깅 + 대체 응답

- 데이터베이스 에러
  ✓ 연결 실패 → 재연결 시도
  ✓ 트랜잭션 롤백 → 데이터 무결성 유지
  ✓ 쿼리 타임아웃 → 적절한 응답
```

### 1.2 웹 프론트엔드 테스트 추가

#### 1.2.1 React 컴포넌트 테스트
**파일:** `web/src/__tests__/components/` (신규)

```javascript
// ClaimInputForm.test.tsx
- 입력 필드 렌더링 확인
- 제출 버튼 클릭 시 이벤트 발생
- 유효성 검증 (빈 문자열 방지)
- 로딩 상태 표시

// GameBoard.test.tsx
- 게임 상태 렌더링
- 청구항 리스트 표시
- 평가 결과 시각화
- 점수 업데이트

// ResultCard.test.tsx
- 평가 결과 렌더링
- 강점/약점 표시
- 점수 바 시각화
- 모바일 반응형 확인
```

#### 1.2.2 Hook 테스트
**파일:** `web/src/__tests__/hooks/` (신규)

```javascript
// useGame.test.ts
- 게임 초기화
- 청구항 제출
- 점수 계산
- 게임 상태 업데이트

// useAuth.test.ts
- 로그인
- 로그아웃
- 세션 유지
- 토큰 갱신
```

---

## Phase 2: E2E 및 시스템 테스트 (1주)

### 2.1 E2E 테스트 프레임워크 (Cypress)

**설정:** `web/cypress/` 디렉토리

```javascript
// cypress/e2e/user-journey.cy.js
describe('사용자 전체 여정 테스트', () => {
  it('회원가입부터 점수 기록까지의 전체 플로우', () => {
    // 1. 랜딩 페이지
    cy.visit('/')
    cy.contains('PROJECT OVERRIDE').should('be.visible')

    // 2. 회원가입
    cy.contains('회원가입').click()
    cy.get('input[name="email"]').type('test@example.com')
    cy.get('input[name="password"]').type('password123')
    cy.get('button[type="submit"]').click()
    cy.contains('환영합니다').should('be.visible')

    // 3. 청구항 입력
    cy.get('textarea[name="claim"]').type(
      '배터리 장치는 양극, 음극, 전해질을 포함한다'
    )
    cy.get('button[name="submit"]').click()

    // 4. 평가 진행 확인
    cy.contains('평가 중').should('be.visible')

    // 5. 결과 확인
    cy.contains('등록 가능', { timeout: 30000 }).should('be.visible')
    cy.get('[data-testid="score"]').should('contain', '/')

    // 6. 점수 기록 확인
    cy.contains('점수 저장').click()
    cy.contains('저장되었습니다').should('be.visible')
  })
})

// cypress/e2e/game-mechanics.cy.js
describe('게임 메커니즘 테스트', () => {
  it('레벨 업 시스템이 정상 작동', () => {
    // 레벨 1 청구항 5개 완료
    for (let i = 0; i < 5; i++) {
      cy.submitClaim(`청구항 ${i + 1}`)
      cy.contains('✅', { timeout: 20000 }).should('be.visible')
    }

    // 레벨 2로 자동 진급 확인
    cy.contains('레벨 2').should('be.visible')
    cy.get('[data-testid="difficulty"]').should('contain', '어려움')
  })

  it('리더보드 순위 업데이트 확인', () => {
    cy.visit('/leaderboard')
    cy.get('[data-testid="rank-1"]').should('contain', '1위')
    cy.get('[data-testid="current-user"]').should('contain', '나')
  })
})

// cypress/e2e/error-scenarios.cy.js
describe('에러 처리 시나리오', () => {
  it('LLM API 타임아웃 시 사용자 안내', () => {
    // 네트워크 지연 시뮬레이션
    cy.intercept('POST', '/api/games/evaluate', (req) => {
      req.reply((res) => {
        res.delay(35000) // 35초 지연
      })
    })

    cy.submitClaim('청구항')
    cy.contains('평가 시간이 너무 오래 걸렸습니다', { timeout: 40000 })
      .should('be.visible')
    cy.contains('다시 시도').should('be.visible')
  })

  it('서버 에러 발생 시 안내 메시지 표시', () => {
    cy.intercept('POST', '/api/games/evaluate', { statusCode: 500 })

    cy.submitClaim('청구항')
    cy.contains('서버 오류가 발생했습니다', { timeout: 10000 })
      .should('be.visible')
  })
})
```

### 2.2 성능 테스트 (k6)

**파일:** `tests/performance/performance_tests.js`

```javascript
import http from 'k6/http'
import { check, group, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '30s', target: 20 }, // 20 users
    { duration: '1m30s', target: 100 }, // 100 users
    { duration: '30s', target: 0 }, // 0 users
  ],
}

export default function () {
  // 청구항 제출 엔드포인트 성능 테스트
  group('청구항 제출', () => {
    const res = http.post('http://localhost:5000/api/games/submit', {
      claim: '배터리 장치는 양극, 음극을 포함한다',
    })

    check(res, {
      'status is 200': (r) => r.status === 200,
      '응답 시간 < 500ms': (r) => r.timings.duration < 500,
      '응답에 claim_id 포함': (r) => r.body.includes('claim_id'),
    })
  })

  sleep(1)

  // LLM 평가 엔드포인트 성능 테스트
  group('LLM 평가', () => {
    const res = http.post('http://localhost:5000/api/games/evaluate', {
      claim_ids: ['claim_1', 'claim_2'],
    })

    check(res, {
      'status is 200': (r) => r.status === 200,
      '평가 시간 < 30s': (r) => r.timings.duration < 30000,
      '모든 청구항 평가됨': (r) => r.body.includes('all_evaluated'),
    })
  })

  sleep(2)
}
```

### 2.3 보안 스캔 (SAST)

**도구:** SonarQube + Bandit

```bash
# Python 보안 스캔
bandit -r src/ -f json -o bandit-report.json

# JavaScript 보안 스캔
npm audit
npm run lint:security

# 실행 결과:
# ❌ SQL Injection 위험 없음
# ❌ XSS 취약점 없음
# ❌ 민감 정보 노출 없음
```

---

## Phase 3: 배포 자동화 (CI/CD) (3일)

### 3.1 GitHub Actions CI 설정

**파일:** `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run pytest
        run: |
          pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: cd web && npm install

      - name: Run tests
        run: cd web && npm test -- --coverage

      - name: Build
        run: cd web && npm run build

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: |
          docker-compose up -d

      - name: Wait for services
        run: sleep 10

      - name: Run Cypress
        uses: cypress-io/github-action@v5
        with:
          working-directory: web
          start: npm start
          wait-on: http://localhost:3000

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit
        run: pip install bandit && bandit -r src/ -f json

      - name: Run npm audit
        run: cd web && npm audit
```

### 3.2 GitHub Actions CD 설정

**파일:** `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests, e2e-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t project-override:latest .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push project-override:latest

      - name: Deploy to server
        run: |
          ssh -i ${{ secrets.SSH_KEY }} user@server "docker pull project-override:latest && docker-compose up -d"

      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "배포 완료: ${{ job.status }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Project OVERRIDE 배포*\nStatus: ${{ job.status }}\nCommit: ${{ github.sha }}"
                  }
                }
              ]
            }
```

---

## Phase 4: 모니터링 및 운영 (3일)

### 4.1 에러 트래킹 (Sentry)

**통합:** `src/utils/sentry_setup.py`

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-sentry-key@sentry.io/project-id",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)

# 사용법
try:
    evaluate_claim(claim)
except Exception as e:
    sentry_sdk.capture_exception(e)
    # 동시에 Slack 알림
    notify_slack(f"청구항 평가 실패: {e}")
```

### 4.2 성능 모니터링 (Prometheus + Grafana)

**메트릭 정의:**

```python
from prometheus_client import Counter, Histogram, Gauge

# 청구항 평가 카운터
claims_evaluated_counter = Counter(
    'claims_evaluated_total',
    'Total claims evaluated',
    ['status']  # 'success', 'failed'
)

# 평가 시간 히스토그램
evaluation_duration = Histogram(
    'claim_evaluation_duration_seconds',
    'Time spent evaluating claims',
    buckets=(1, 5, 10, 20, 30, 60)
)

# 활성 사용자 게이지
active_users = Gauge(
    'active_users',
    'Number of active users'
)
```

### 4.3 로그 수집 (ELK Stack)

**구성:**
- **Elasticsearch**: 로그 저장소
- **Logstash**: 로그 처리
- **Kibana**: 시각화

---

## Phase 5: 문서화 (1주)

### 5.1 API 문서 (Swagger/OpenAPI)

**파일:** `docs/api.yaml`

```yaml
openapi: 3.0.0
info:
  title: Project OVERRIDE API
  version: 1.0.0

paths:
  /api/claims/submit:
    post:
      summary: 청구항 제출
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                claim:
                  type: string
                  example: "배터리 장치는 양극, 음극을 포함한다"
      responses:
        '200':
          description: 청구항 제출 성공
          content:
            application/json:
              schema:
                type: object
                properties:
                  claim_id:
                    type: string
                  status:
                    type: string
        '400':
          description: 유효하지 않은 입력
        '500':
          description: 서버 오류
```

### 5.2 사용자 가이드

**파일:** `docs/USER_GUIDE.md`

- 회원가입 및 로그인
- 청구항 작성 팁
- 게임 진행 방법
- 평가 결과 해석
- FAQ

### 5.3 개발자 문서

**파일:** `docs/DEVELOPER_GUIDE.md`

- 개발 환경 설정
- 아키텍처 개요
- API 엔드포인트
- 데이터베이스 스키마
- 배포 절차

---

## 📊 테스트 커버리지 목표

| 영역 | 현재 | 목표 | 방법 |
|------|------|------|------|
| Python 백엔드 | 60% | 85% | 추가 통합 테스트 |
| React 컴포넌트 | 10% | 80% | Jest + RTL |
| E2E 시나리오 | 0% | 100% | Cypress |
| API 엔드포인트 | 30% | 95% | pytest + requests |
| 보안 | 0% | 100% | Bandit + SonarQube |

---

## 📋 구현 일정

```
Week 1: Phase 1 (단위/통합 테스트)
  - Mon: Python API 테스트 작성 (15개)
  - Tue: React 컴포넌트 테스트 (10개)
  - Wed: 에러 처리 테스트 (20개)
  - Thu-Fri: 리뷰 및 개선

Week 2: Phase 2 (E2E/시스템)
  - Mon: Cypress E2E 테스트 (10개 시나리오)
  - Tue: 성능 테스트 (k6)
  - Wed: 보안 스캔 (SAST)
  - Thu-Fri: 리뷰 및 개선

Week 3: Phase 3 (CI/CD)
  - Mon-Tue: GitHub Actions 설정
  - Wed: Docker 및 배포 스크립트
  - Thu-Fri: 배포 자동화 테스트

Week 4: Phase 4 & 5 (모니터링 + 문서)
  - Mon-Tue: Sentry + Prometheus 설정
  - Wed-Thu: API 문서 + 사용자 가이드
  - Fri: 최종 테스트 및 배포
```

---

## ✅ 완성 체크리스트

### 단계별 완료 기준

- [ ] Phase 1: 새로운 테스트 50개 이상 추가
- [ ] Phase 2: E2E 10개 시나리오 + 성능 테스트 통과
- [ ] Phase 3: CI/CD 파이프라인 모든 테스트 자동 실행
- [ ] Phase 4: 에러 발생 시 1분 이내 알림
- [ ] Phase 5: 모든 API와 기능에 문서 작성

### 최종 목표

```
✅ 테스트 커버리지: 85% 이상
✅ 자동화 테스트 성공률: 95% 이상
✅ 배포 자동화: 100% 완료
✅ 모니터링: 실시간 에러 감지
✅ 문서화: 신입도 설정 가능
```

