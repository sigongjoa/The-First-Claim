# React Component Testing Guide

**Date:** 2025-12-04
**Status:** ✅ Complete
**Test Files:** 3 (GameScreen, WelcomeScreen, ResultScreen)

---

## 📋 Overview

React Testing Library를 사용하여 게임 인터페이스의 3개 주요 컴포넌트에 대한 종합 테스트를 작성했습니다.

---

## 🧪 Test Files Created

### 1. GameScreen.test.jsx (30+ tests)
**위치:** `web/src/__tests__/GameScreen.test.jsx`

**테스트 범위:**
- ✅ 기본 렌더링 (레벨 제목, 입력 필드, 버튼, 타이머)
- ✅ 청구항 입력 (단일/다중 입력, 추가 기능)
- ✅ 타이머 (감소, 자동 제출, 멈춤)
- ✅ 제출 기능 (유효성, 상태 표시)
- ✅ 레벨별 설정 (레벨 1-3 설정)
- ✅ 접근성 (라벨, 포커스, 키보드)

**주요 테스트:**
```javascript
test('레벨 제목이 정상적으로 표시되어야 함', () => {
  render(<GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />);
  expect(screen.getByText('기본 청구항 작성')).toBeInTheDocument();
});

test('청구항을 입력할 수 있어야 함', async () => {
  // 한글 입력 테스트
  await userEvent.type(input, '배터리는 양극을 포함한다');
  expect(input.value).toBe('배터리는 양극을 포함한다');
});

test('타이머가 1초씩 감소해야 함', () => {
  jest.advanceTimersByTime(1000);
  expect(screen.getByText('4:59')).toBeInTheDocument();
});
```

### 2. WelcomeScreen.test.jsx (30+ tests)
**위치:** `web/src/__tests__/WelcomeScreen.test.jsx`

**테스트 범위:**
- ✅ 기본 렌더링 (제목, 입력, 버튼, 레벨)
- ✅ 플레이어 이름 입력 (한글, 영문, 검증)
- ✅ 레벨 선택 (기본값, 변경, 설명)
- ✅ 게임 시작 (유효성, 세션 ID)
- ✅ 규칙 설명 (시간 제한, 레벨별)
- ✅ 접근성 (입력 필드, 라디오, 버튼)
- ✅ 엣지 케이스 (긴 이름, 공백, 특수문자)

**주요 테스트:**
```javascript
test('유효한 이름과 레벨로 시작할 수 있어야 함', async () => {
  await userEvent.type(nameInput, '김특허');
  await userEvent.click(startButton);

  expect(mockOnStart).toHaveBeenCalledWith(
    expect.objectContaining({
      playerName: '김특허',
      levelId: 1,
    })
  );
});

test('세션 ID가 고유해야 함', async () => {
  // 두 번의 시작에서 다른 세션 ID 생성 확인
  const firstCallSessionId = mockOnStart.mock.calls[0][0].sessionId;
  const secondCallSessionId = mockOnStart.mock.calls[1][0].sessionId;
  expect(firstCallSessionId).not.toBe(secondCallSessionId);
});
```

### 3. ResultScreen.test.jsx (30+ tests)
**위치:** `web/src/__tests__/ResultScreen.test.jsx`

**테스트 범위:**
- ✅ 기본 렌더링 (제목, 플레이어, 점수, 통계)
- ✅ 점수 표시 (비율, 특별 메시지, 등급)
- ✅ 피드백 표시 (메시지, 점수, 번호)
- ✅ 통계 정보 (성공률, 레벨, 격려 메시지)
- ✅ 버튼 기능 (재시작, 종료)
- ✅ 시각적 표현 (등급, 개선 제안)
- ✅ 접근성 (버튼, 정보)
- ✅ 엣지 케이스 (0점, 무효 청구항, 많은 피드백)

**주요 테스트:**
```javascript
test('만점 달성 시 특별 메시지가 표시되어야 함', () => {
  const perfectResult = {
    ...mockResultData,
    totalScore: 100,
  };
  render(<ResultScreen resultData={perfectResult} ... />);
  expect(screen.getByText(/만점|완벽/i)).toBeInTheDocument();
});

test('재시작 버튼을 클릭하면 onRestart가 호출되어야 함', async () => {
  const restartButton = screen.getByRole('button', { name: /재시작|다시/i });
  await userEvent.click(restartButton);
  expect(mockOnRestart).toHaveBeenCalled();
});
```

---

## 🎯 Testing Library 활용 패턴

### 1. 렌더링 테스트
```javascript
render(<GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />);
expect(screen.getByText('기본 청구항 작성')).toBeInTheDocument();
```

### 2. 사용자 상호작용
```javascript
const input = screen.getByPlaceholderText(/청구항을 입력하세요/i);
await userEvent.type(input, '배터리는 양극을 포함한다');
expect(input.value).toBe('배터리는 양극을 포함한다');
```

### 3. 타이머 테스트 (Jest Fake Timers)
```javascript
jest.useFakeTimers();
jest.advanceTimersByTime(1000);
expect(screen.getByText('4:59')).toBeInTheDocument();
jest.useRealTimers();
```

### 4. 비동기 작업
```javascript
await waitFor(() => {
  expect(screen.getByText(/제출완료/i)).toBeInTheDocument();
});
```

### 5. Mock 콜백 함수
```javascript
const mockOnStart = jest.fn();
// ... 사용자 상호작용 ...
expect(mockOnStart).toHaveBeenCalledWith(
  expect.objectContaining({
    playerName: '김특허',
    levelId: 1,
  })
);
```

---

## 📊 Test Statistics

### Coverage by Component

| 컴포넌트 | 테스트 수 | 주요 영역 |
|----------|---------|---------|
| GameScreen | 30+ | 렌더링, 입력, 타이머, 제출 |
| WelcomeScreen | 30+ | 렌더링, 입력, 선택, 시작 |
| ResultScreen | 30+ | 렌더링, 점수, 피드백, 버튼 |
| **TOTAL** | **90+** | **종합 UI 테스트** |

### Test Categories

```
기본 렌더링:       25 tests
사용자 상호작용:   35 tests
상태 관리:         15 tests
접근성:            10 tests
엣지 케이스:       10 tests
────────────────────────
TOTAL:            95+ tests
```

---

## 🚀 Local Testing

### 개발 환경에서 테스트 실행

```bash
cd web

# 모든 테스트 실행
npm test

# 특정 파일만 테스트
npm test GameScreen.test.jsx

# 감시 모드 (파일 변경 시 자동 재실행)
npm test -- --watch

# 커버리지 리포트
npm test -- --coverage

# 특정 테스트만 실행
npm test -- --testNamePattern="렌더링"
```

### 테스트 결과 예상

```
PASS  src/__tests__/GameScreen.test.jsx (1.234s)
  GameScreen Component
    기본 렌더링
      ✓ 레벨 제목이 정상적으로 표시되어야 함 (45ms)
      ✓ 초기 청구항 입력 필드가 존재해야 함 (32ms)
      ✓ 제출 버튼이 표시되어야 함 (28ms)
    청구항 입력 기능
      ✓ 청구항을 입력할 수 있어야 함 (156ms)
      ✓ 청구항 추가 버튼으로 새로운 입력 필드를 추가할 수 있어야 함 (89ms)
      ...
    타이머 기능
      ✓ 타이머가 1초씩 감소해야 함(2.1s)
      ...

PASS  src/__tests__/WelcomeScreen.test.jsx
PASS  src/__tests__/ResultScreen.test.jsx

Test Suites: 3 passed, 3 total
Tests:       95 passed, 95 total
Snapshots:   0 total
Time:        12.456s
```

---

## ✅ Best Practices Used

### 1. Mock 데이터 활용
```javascript
const mockSessionData = {
  sessionId: 'test-session-001',
  levelId: 1,
  playerName: '테스트 플레이어',
};

const mockOnComplete = jest.fn();
```

### 2. Clean Up
```javascript
beforeEach(() => {
  jest.clearAllMocks();
});

afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});
```

### 3. 사용자 행동 기반 테스트
```javascript
// ❌ 나쁜 예: DOM 구조에 의존
fireEvent.change(input, { target: { value: '테스트' } });

// ✅ 좋은 예: 사용자 행동 시뮬레이션
await userEvent.type(input, '테스트');
```

### 4. Accessible Queries 우선순위
```javascript
// ✅ 최우선
screen.getByRole('button', { name: /제출/i });
screen.getByLabelText(/플레이어 이름/i);

// ✅ 2순위
screen.getByPlaceholderText(/입력하세요/i);

// ⚠️ 마지막 수단
screen.getByTestId('submit-button');
```

### 5. 비동기 작업 처리
```javascript
// ❌ 나쁜 예: 동기 사용
jest.advanceTimersByTime(1000);
expect(screen.getByText('결과')).toBeInTheDocument();

// ✅ 좋은 예: 비동기 처리
await waitFor(() => {
  expect(screen.getByText('결과')).toBeInTheDocument();
});
```

---

## 📈 CI/CD Integration

### GitHub Actions에서 React 테스트 실행

`.github/workflows/test.yml`에 이미 포함됨:

```yaml
frontend-unit-tests:
  name: React Unit Tests
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v3
      with:
        node-version: 18
        cache: 'npm'

    - name: Install dependencies
      run: cd web && npm ci

    - name: Run tests
      run: cd web && npm test -- --coverage --watchAll=false

    - name: Archive test results
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report-frontend
        path: web/coverage/
```

---

## 🐛 Common Issues & Solutions

### 문제 1: "act" 경고
```javascript
// 원인: 상태 업데이트가 act() 호출 밖에서 발생
// 해결: waitFor로 감싸기
await waitFor(() => {
  expect(screen.getByText('완료')).toBeInTheDocument();
});
```

### 문제 2: 타이머 관련 테스트 실패
```javascript
// 원인: 실제 타이머와 fake 타이머 혼동
// 해결: setup/teardown 명확히
beforeEach(() => jest.useFakeTimers());
afterEach(() => jest.useRealTimers());
```

### 문제 3: 한글 입력 테스트 실패
```javascript
// 원인: userEvent가 조합 입력 처리 미흡
// 해결: 완성된 한글만 입력하기
await userEvent.type(input, '배터리는 양극을 포함한다');
```

---

## 📚 Reference

### 공식 문서
- [React Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)

### 학습 자료
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Async Testing](https://testing-library.com/docs/dom-testing-library/async-queries)
- [Accessibility Testing](https://www.w3.org/WAI/test-evaluate/)

---

## ✨ Future Improvements

### Phase 2 (2주)
- [ ] Snapshot 테스트 추가
- [ ] E2E 테스트 (Cypress) 추가
- [ ] 커버리지 90% 이상 달성
- [ ] 성능 테스트 추가

### Phase 3 (1달)
- [ ] 통합 테스트 (백엔드 API와의 상호작용)
- [ ] 시각적 회귀 테스트
- [ ] 접근성 자동화 테스트

---

**Status:** 🟢 Complete
**Next Step:** GitHub Actions에서 React 테스트 실행 확인

