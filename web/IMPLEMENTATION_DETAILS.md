# React Web App - Implementation Details

Based on actual code analysis of components in `/web/src/components/`

---

## Component Architecture

### 1. WelcomeScreen.jsx (115 lines)

**Purpose**: Initial game screen for player name input and level selection

**State Management**:
```javascript
const [playerName, setPlayerName] = useState('');
const [selectedLevel, setSelectedLevel] = useState(1);
const [error, setError] = useState('');
```

**Features**:
- Player name input with validation
- Error message display when name is empty
- 3 level selection cards with descriptions
- Level configuration display (claims needed, time limit)
- Enter key support for starting game
- Error clears when player types new name

**Props**:
- `onStartGame(playerName, selectedLevel)`: Called when user clicks "게임 시작"

**Level Definitions**:
```javascript
levels = [
  { id: 1, title: '기본 청구항 작성', difficulty: 'EASY', claims: 1, time: 300, ... },
  { id: 2, title: '종속항 작성', difficulty: 'NORMAL', claims: 3, time: 600, ... },
  { id: 3, title: '복합 청구항 세트', difficulty: 'HARD', claims: 5, time: 900, ... }
]
```

**Validation**:
- Player name required (non-empty string)
- Error message: "플레이어 이름을 입력해주세요"

---

### 2. GameScreen.jsx (246 lines)

**Purpose**: Main game playing interface where users write patent claims

**State Management**:
```javascript
const [claims, setClaims] = useState(['']);        // Array of claim strings
const [currentInput, setCurrentInput] = useState('');
const [timeLeft, setTimeLeft] = useState(300);     // Seconds remaining
const [submitted, setSubmitted] = useState(false);  // Submission state
const [feedback, setFeedback] = useState([]);      // Validation feedback
const [validationResults, setValidationResults] = useState([]);  // Per-claim results
```

**Level Configuration**:
```javascript
levelConfigs = {
  1: { title: '기본 청구항 작성', required: 1, timeLimit: 300 },    // 5 min
  2: { title: '종속항 작성', required: 3, timeLimit: 600 },          // 10 min
  3: { title: '복합 청구항 세트', required: 5, timeLimit: 900 }      // 15 min
}
```

**Core Features**:

#### Timer Implementation
- Uses `setInterval` with 1-second updates
- Auto-submits when time reaches 0
- Displays in MM:SS format
- Warning styling when < 60 seconds remaining
- Cleared on unmount

#### Claim Management
- `addClaim()`: Add new textarea for additional claim
- `updateClaim(index, value)`: Update specific claim text
- `removeClaim(index)`: Remove claim (only if > 1 claim exists)
- `filledClaims`: Count of non-empty claims

#### Validation Logic
```javascript
validateClaims() {
  // For each claim:
  // - Empty → invalid: "청구항 내용이 비어있습니다"
  // - Length < 20 → invalid: "청구항이 너무 짧습니다 (최소 20자)"
  // - Length >= 20 → valid: "✅ 올바른 형식입니다"

  // Returns: { results, hasErrors }
  // results[i] = { index, valid, message }
  // hasErrors = boolean
}
```

#### Submission Logic
```javascript
handleSubmit() {
  1. Validate all claims
  2. Count claims with length >= 20 (validClaims)
  3. success = validClaims.length >= config.required && !hasErrors
  4. Set feedback messages
  5. After 2 seconds delay: onComplete(claims, success)
}
```

**UI Elements**:

| Element | Details |
|---------|---------|
| Timer | ⏱️ MM:SS format, warning class if < 60s |
| Requirement Display | "필요한 청구항: X개 \| 작성 중: Y개" |
| Tips Section | "💡 팁: 각 청구항은 기술적 특징을..." |
| Claim Textarea | Per-claim input, color-coded (valid/invalid) |
| Claim Type Label | "독립항" for first, "종속항" for others |
| Character Count | "N / 20자" with ✅ when >= 20 |
| Delete Button | Only shows when claims.length > 1 |
| Add Claim Button | Only shows when filledClaims < required |
| Submit Button | Disabled when filledClaims === 0 |
| Feedback Section | Shows during/after validation |
| Result Pending | Spinner + "평가 중..." when submitted |

**Placeholders**:
- First claim: "기본 청구항을 작성하세요 (예: 배터리 장치는...)"
- Other claims: "종속항을 작성하세요 (예: 제1항의 배터리에서...)"

**Feedback Messages** (on submission):
- Success: "✅ 모든 청구항이 요구사항을 충족했습니다!"
- Partial: "📊 제출된 청구항: X개 / Y개 필요"
- Errors: "⚠️ 일부 청구항이 검증 오류가 있습니다"

**Props**:
- `sessionData`: { sessionId, playerName, levelId, submittedClaims, startTime }
- `onComplete(claims, success)`: Called after 2-second delay post-submission

---

### 3. ResultScreen.jsx (101 lines)

**Purpose**: Display game results and navigation options

**Props**:
- `result`: { success, playerName, levelId, claims }
- `onRetry()`: Reset game and return to welcome
- `onNextLevel()`: Null if last level, otherwise function to advance

**State Rendering**:

#### Success Path (success === true)
- Icon: 🎉
- Title: "축하합니다!"
- Message: "레벨을 성공적으로 통과했습니다"
- Stats Display:
  - 플레이어: {playerName}
  - 완료한 레벨: Level {levelId}
  - 작성한 청구항: {count}개 (only non-empty claims)
- Claims Review Section: Shows all submitted claims
- Buttons:
  - "다음 레벨" (if onNextLevel provided)
  - "다시 하기"

#### Failure Path (success === false)
- Icon: ❌
- Title: "아직 요구사항을 충족하지 못했습니다"
- Message: "다시 시도해주세요"
- Stats Display:
  - 플레이어: {playerName}
  - 레벨: Level {levelId}
  - 작성한 청구항: {count}개
- Tips Section (💡 개선 팁):
  - 각 청구항은 기술적 특징을 명확하게 포함해야 합니다
  - 최소 20자 이상 작성해주세요
  - 독립항과 종속항의 관계를 명확하게 표현하세요
  - 모호한 표현을 피하세요 (예: 등, 같은, 대략 등)
- Buttons:
  - "다시 하기"
  - "메인 메뉴"

**Button Logic**:
```javascript
if (onNextLevel) {
  // Success: Show "다음 레벨" and "다시 하기"
} else {
  // Failure or last level: Show "다시 하기" and "메인 메뉴"
}
```

---

### 4. App.jsx (79 lines)

**Purpose**: Main app component managing game state and screen navigation

**State Management**:
```javascript
const [gameState, setGameState] = useState('welcome');  // 'welcome' | 'playing' | 'result'
const [playerName, setPlayerName] = useState('');
const [currentLevel, setCurrentLevel] = useState(1);
const [sessionData, setSessionData] = useState(null);
const [gameResult, setGameResult] = useState(null);
```

**Game Flow**:

```
START (App mounts)
  ↓
gameState = 'welcome'
  ↓ (user clicks "게임 시작")
handleStartGame(playerName, level)
  ├─ setPlayerName(name)
  ├─ setCurrentLevel(level)
  ├─ setSessionData({ sessionId, playerName, levelId, ... })
  └─ setGameState('playing')
  ↓
gameState = 'playing'
  ↓ (user submits or timer ends)
handleGameComplete(claims, success)
  ├─ setGameResult({ claims, success, playerName, levelId })
  └─ setGameState('result')
  ↓
gameState = 'result'
  ↓ (user clicks button)
EITHER:
  ├─ handleRetry()
  │   ├─ setGameState('welcome')
  │   ├─ Reset all state variables
  │   └─ Back to start
  └─ handleNextLevel()
      ├─ if currentLevel < 3: handleStartGame(playerName, currentLevel + 1)
      └─ else: handleRetry() (after level 3)
```

**Next Level Logic**:
- On success and currentLevel < 3:
  - Show "다음 레벨" button
  - handleNextLevel() starts new game with incremented level
  - Player name is preserved
- After Level 3 completion:
  - onNextLevel = null (not passed to ResultScreen)
  - Only "다시 하기" and "메인 메뉴" shown
  - handleNextLevel() returns to welcome

**Screen Rendering Logic**:
```javascript
render() {
  if (gameState === 'welcome') ⟶ <WelcomeScreen />
  else if (gameState === 'playing' && sessionData) ⟶ <GameScreen />
  else if (gameState === 'result' && gameResult) ⟶ <ResultScreen />
}
```

---

## Data Flow Diagram

```
WelcomeScreen
    │
    │ onStartGame(playerName, level)
    ↓
App.handleStartGame()
    │ creates sessionData
    ↓
GameScreen
    │ receives sessionData
    │ user writes claims
    │ user submits or timer ends
    │ onComplete(claims, success)
    ↓
App.handleGameComplete()
    │ creates gameResult
    ↓
ResultScreen
    │ receives result, onRetry, onNextLevel
    │ if success:
    │   ├─ handleNextLevel() → new GameScreen with level+1
    │   └─ or handleRetry() → back to WelcomeScreen
    │ if failure:
    │   └─ handleRetry() → back to WelcomeScreen
    ↓
Back to WelcomeScreen
```

---

## Key Implementation Details

### Timing & Delays
- GameScreen timer: 1-second interval, auto-submit at 0
- GameScreen submit: 2-second delay before onComplete() called
- ResultScreen: No delays, instant button response

### Validation
- **Minimum length**: 20 characters (claims < 20 are invalid)
- **Empty claims**: Treated as invalid, skipped from count
- **Success condition**:
  - validClaims.length >= config.required AND
  - No validation errors

### UI/UX Details
- Disabled submit button when no claims filled
- Add button hidden when filledClaims >= required
- Delete button hidden when only 1 claim exists
- Character count updates in real-time
- Validation styling (green for valid, red for invalid)
- Timer warning color when < 60 seconds

### State Persistence
- Player name preserved when advancing to next level
- Claims NOT preserved (fresh start per level)
- Session IDs unique per game session
- All state reset on "다시 하기" or "메인 메뉴"

---

## Testing Considerations

Based on actual component implementation:

### WelcomeScreen Tests Should Verify
- ✅ Input value updates
- ✅ Error message display/clearing
- ✅ Level selection click handling
- ✅ Enter key submission
- ✅ onStartGame callback invocation with correct params

### GameScreen Tests Should Verify
- ✅ Timer countdown (real interval in actual code)
- ✅ Auto-submit when timer reaches 0
- ✅ Claim addition/removal
- ✅ Character count display
- ✅ Validation logic for each claim
- ✅ Submit button disabled state
- ✅ 2-second delay before onComplete
- ✅ Feedback messages based on validation results

### ResultScreen Tests Should Verify
- ✅ Success vs failure rendering
- ✅ Stats display (player, level, claim count)
- ✅ Claims display filtering empty ones
- ✅ Button conditional rendering (onNextLevel)
- ✅ Callback invocations

### App Integration Tests Should Verify
- ✅ Screen transitions (welcome → playing → result)
- ✅ State preservation across screens
- ✅ Level progression (1 → 2 → 3 → welcome)
- ✅ Retry functionality
- ✅ sessionData creation and usage

---

## Actual vs Test Specifications

### Discrepancies Found

**1. Button Labels** (from ResultScreen.jsx:78-91)
- **Actual**: "다시 하기" + "메인 메뉴" (not "홈")
- **Test Expected**: /홈|처음으로|Home/i
- **Fix**: Update tests to expect actual labels

**2. ResultScreen Props** (from ResultScreen.jsx:4)
- **Actual**: `result` (single object), `onRetry`, `onNextLevel`
- **Test Expected**: `sessionData`, `onRetry`, `onNextLevel`, `onHome`
- **Fix**: Update mock props in tests

**3. Failure State Navigation** (from ResultScreen.jsx:85-93)
- **Actual**: Shows "다시 하기" + "메인 메뉴" when onNextLevel is null
- **Test Expected**: Different button labels
- **Fix**: Update test expectations

**4. Submit Button State** (from GameScreen.jsx:237)
- **Actual**: disabled={filledClaims === 0}
- **Test Expected**: disabled when no claims (correct ✅)

**5. Timer Implementation** (from GameScreen.jsx:30)
- **Actual**: Real setInterval (not Jest fake timers easily mockable)
- **Test**: Must account for actual async timer behavior

**6. Next Level Button** (from App.jsx:72)
- **Actual**: onNextLevel prop is null when currentLevel >= 3 or failure
- **Test Expected**: Button should not render when null
- **Fix**: Tests correctly expect conditional rendering

---

## Summary of Implementation Facts

| Aspect | Value |
|--------|-------|
| Number of Components | 3 (WelcomeScreen, GameScreen, ResultScreen) |
| Main App Component | App.jsx (79 lines) |
| Total Component Code | ~540 lines |
| State Management Method | React Hooks (useState) |
| Styling Method | External CSS files in styles/ |
| Timer Implementation | setInterval (1-second interval) |
| Validation Strategy | Per-claim length checking (20+ chars) |
| Level Count | 3 (EASY, NORMAL, HARD) |
| Submit Delay | 2 seconds before result screen |
| Button State Management | Conditional disabled/onClick |
| Props Patterns | Callbacks passed from parent to child |

---

**Generated**: December 3, 2025
**Based On**: Actual component code analysis
**Status**: Accurate implementation documentation ✅
