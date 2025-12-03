# PROJECT OVERRIDE - React Web Game

청구항 작성 게임의 React 웹 인터페이스입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd web
npm install
```

### 2. 개발 서버 실행

```bash
npm start
```

브라우저에서 http://localhost:3000 으로 이동합니다.

### 3. 프로덕션 빌드

```bash
npm run build
```

## 📁 프로젝트 구조

```
web/
├── public/
│   └── index.html          # HTML 진입점
├── src/
│   ├── components/
│   │   ├── WelcomeScreen.jsx    # 환영 화면
│   │   ├── GameScreen.jsx       # 게임 플레이 화면
│   │   └── ResultScreen.jsx     # 결과 화면
│   ├── styles/
│   │   ├── WelcomeScreen.css    # 환영 스타일
│   │   ├── GameScreen.css       # 게임 스타일
│   │   └── ResultScreen.css     # 결과 스타일
│   ├── App.jsx              # 메인 앱 컴포넌트
│   ├── App.css              # 앱 스타일
│   ├── index.js             # 진입점
│   └── index.css            # 전역 스타일
├── package.json             # 프로젝트 메타데이터
└── README.md               # 이 파일
```

## 🎮 게임 기능

### 3단계 난이도

1. **레벨 1: 기본 청구항 작성** (EASY)
   - 필요: 1개의 청구항
   - 시간: 300초 (5분)
   - 목표: 간단한 독립항 작성

2. **레벨 2: 종속항 작성** (NORMAL)
   - 필요: 3개의 청구항
   - 시간: 600초 (10분)
   - 목표: 독립항과 종속항의 관계 표현

3. **레벨 3: 복합 청구항 세트** (HARD)
   - 필요: 5개의 청구항
   - 시간: 900초 (15분)
   - 목표: 복잡한 청구항 세트 작성

### 검증 규칙

- 최소 20자 이상
- 기술적 특징 명시
- 명확한 표현
- 종속항의 올바른 참조

## 📚 컴포넌트 설명

### WelcomeScreen
사용자 이름을 입력받고 레벨을 선택하는 화면입니다.
- 플레이어 이름 입력
- 3단계 레벨 선택
- 각 레벨의 요구사항 표시

### GameScreen
청구항을 작성하고 검증받는 게임 화면입니다.
- 청구항 입력 필드
- 실시간 문자 수 카운팅
- 타이머 (시간 제한)
- 검증 결과 피드백
- 청구항 추가/삭제 기능

### ResultScreen
게임 결과를 표시하는 화면입니다.
- 성공/실패 상태
- 작성한 청구항 복습
- 통계 (플레이어명, 레벨, 청구항 수)
- 개선 팁 (실패 시)
- 다음 레벨 진행 또는 재시도 버튼

## 🎨 디자인 특징

### 색상 팔레트
- 주색상: Purple (#667eea, #764ba2)
- 성공: Green (#2ecc71)
- 경고: Yellow (#f39c12)
- 실패: Red (#e74c3c)

### 애니메이션
- 화면 전환: Fade In / Slide Up
- 버튼: Hover 효과, 탭 피드백
- 타이머: 경고 상태에서 Pulse 애니메이션

### 반응형 디자인
- 모바일 (< 600px)
- 태블릿 (600px - 1024px)
- 데스크톱 (> 1024px)

## 📦 의존성

- **React 18.2**: UI 라이브러리
- **React DOM 18.2**: React DOM 렌더링
- **React Scripts 5.0**: Create React App 스크립트
- **Axios 1.6**: HTTP 클라이언트 (향후 백엔드 통합용)
- **TypeScript 4.9**: 타입 체크 (선택사항)

## 🔧 사용자 정의

### 레벨 추가하기
`GameScreen.jsx`의 `levelConfigs` 객체를 수정합니다:

```javascript
const levelConfigs = {
  1: { title: '...', required: 1, timeLimit: 300 },
  2: { title: '...', required: 3, timeLimit: 600 },
  3: { title: '...', required: 5, timeLimit: 900 },
  4: { title: '...', required: 7, timeLimit: 1200 }, // 새로운 레벨
};
```

### 검증 규칙 변경
`GameScreen.jsx`의 `validateClaims()` 함수를 수정합니다.

### 스타일 커스터마이징
`src/styles/` 폴더의 CSS 파일들을 수정합니다.

## 🌐 향후 기능 (Roadmap)

- [ ] 백엔드 API 통합 (Python FastAPI)
- [ ] 플레이어 진행 상황 저장 (데이터베이스)
- [ ] 리더보드 (점수 순위)
- [ ] 배지 및 성취 시스템
- [ ] 실시간 협력 모드
- [ ] 모바일 앱 (React Native)
- [ ] 다국어 지원 (i18n)

## 📝 라이선스

PROJECT OVERRIDE - Test-Driven Legal Engine

## 👨‍💻 개발

문의사항이나 버그 보고는 프로젝트 저장소를 참고하세요.

---

**생성 날짜**: 2025년 12월 3일
**React 버전**: 18.2.0
**상태**: 개발 중
