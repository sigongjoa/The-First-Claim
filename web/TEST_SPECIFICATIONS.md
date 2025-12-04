# React 웹 게임 테스트 명세서

## 1. 테스트 전략

### 테스트 종류별 분류

1. **단위 테스트 (Unit Tests)**: 개별 컴포넌트의 기능 검증
2. **통합 테스트 (Integration Tests)**: 컴포넌트 간의 상호작용 검증
3. **E2E 테스트 (End-to-End Tests)**: 전체 게임 플로우 검증
4. **엣지 케이스 테스트**: 예외 상황 검증

### 테스트 도구

- **React Testing Library**: 컴포넌트 렌더링 및 상호작용
- **Jest**: 단위 및 통합 테스트
- **Cypress** (선택): E2E 테스트

---

## 2. 단위 테스트 (Unit Tests)

### WelcomeScreen 컴포넌트

#### 2.1 정상 케이스

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| 1 | render_welcome_screen | 환영 화면 렌더링 | ✓ 제목, 입력 필드, 레벨 버튼 표시 |
| 2 | display_three_levels | 3개 레벨 표시 | ✓ EASY, NORMAL, HARD 레벨 모두 표시 |
| 3 | select_level | 레벨 선택 | ✓ 선택된 레벨 강조 표시 |
| 4 | input_player_name | 플레이어 이름 입력 | ✓ 입력값 state 업데이트 |
| 5 | disable_start_without_name | 이름 없으면 비활성화 | ✓ START 버튼 비활성화 |
| 6 | enable_start_with_name | 이름 입력 후 활성화 | ✓ START 버튼 활성화 |
| 7 | start_game_callback | 게임 시작 콜백 | ✓ onStartGame 호출됨 |
| 8 | default_level_selection | 기본 레벨 1 선택 | ✓ Level 1이 기본 선택됨 |

#### 2.2 엣지 케이스

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| E1 | empty_name_input | 빈 이름 | ✓ 에러 메시지 표시 |
| E2 | whitespace_only_name | 공백만 입력 | ✓ 에러 메시지 표시 |
| E3 | very_long_name | 매우 긴 이름 (100자) | ✓ 입력 제한 또는 자르기 |
| E4 | special_characters_in_name | 특수문자 입력 | ✓ 정상 처리 또는 검증 |
| E5 | name_with_emoji | 이모지 입력 | ✓ 정상 처리 또는 검증 |
| E6 | rapid_level_clicks | 빠른 클릭 | ✓ 안정적 동작 |
| E7 | keyboard_enter_start | Enter 키로 시작 | ✓ 게임 시작 |

---

### GameScreen 컴포넌트

#### 3.1 정상 케이스

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| 1 | render_game_screen | 게임 화면 렌더링 | ✓ 타이머, 입력 필드, 제출 버튼 표시 |
| 2 | timer_countdown | 타이머 카운트다운 | ✓ 1초마다 감소 |
| 3 | input_claim | 청구항 입력 | ✓ 입력값 state 업데이트 |
| 4 | add_claim | 청구항 추가 | ✓ 새 입력 필드 추가 |
| 5 | remove_claim | 청구항 삭제 | ✓ 입력 필드 삭제 |
| 6 | validate_short_claim | 20자 미만 검증 | ✓ 오류 메시지 표시 |
| 7 | validate_long_claim | 20자 이상 유효성 | ✓ 유효 상태 표시 |
| 8 | character_counter | 문자 수 카운팅 | ✓ 실시간 카운트 표시 |
| 9 | submit_valid_claims | 유효한 청구항 제출 | ✓ onComplete 콜백 실행 |
| 10 | level_1_validation | Level 1 (1개 필요) | ✓ 1개 이상 필요 |
| 11 | level_2_validation | Level 2 (3개 필요) | ✓ 3개 이상 필요 |
| 12 | level_3_validation | Level 3 (5개 필요) | ✓ 5개 이상 필요 |
| 13 | timer_expiry | 타이머 만료 | ✓ 자동 제출 실행 |

#### 3.2 엣지 케이스

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| E1 | exactly_20_characters | 정확히 20자 | ✓ 유효 (통과) |
| E2 | exactly_19_characters | 정확히 19자 | ✓ 무효 (실패) |
| E3 | only_spaces | 공백만 입력 | ✓ 무효 처리 |
| E4 | special_chars_only | 특수문자만 입력 | ✓ 문자수 카운트 (유효/무효는 규칙) |
| E5 | multiline_input | 줄바꿈 포함 | ✓ 정상 처리 |
| E6 | very_long_claim | 1000자 이상 | ✓ 정상 처리 또는 제한 |
| E7 | rapid_add_delete | 빠른 추가/삭제 | ✓ 안정적 동작 |
| E8 | delete_last_claim | 마지막 청구항만 남음 | ✓ 삭제 버튼 비활성화 |
| E9 | timer_zero_during_input | 입력 중 타이머 0 | ✓ 강제 제출 |
| E10 | rapid_submission | 빠른 연속 제출 | ✓ 중복 제출 방지 |
| E11 | browser_paste | 붙여넣기 동작 | ✓ 정상 입력 |
| E12 | drag_and_drop | 드래그 앤 드롭 | ✓ 정상 입력 또는 무시 |
| E13 | maximum_claims_level_3 | Level 3에서 10개 입력 | ✓ 최대 5개만 필요 |

---

### ResultScreen 컴포넌트

#### 4.1 정상 케이스

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| 1 | display_success_result | 성공 결과 표시 | ✓ 축하 메시지, 통과 아이콘 |
| 2 | display_failure_result | 실패 결과 표시 | ✓ 실패 메시지, 재시도 옵션 |
| 3 | show_submitted_claims | 제출된 청구항 표시 | ✓ 모든 청구항 나열 |
| 4 | show_player_stats | 플레이어 통계 | ✓ 이름, 레벨, 청구항 수 |
| 5 | next_level_button | 다음 레벨 버튼 | ✓ 성공 시에만 표시 (Level < 3) |
| 6 | retry_button | 다시 하기 버튼 | ✓ 항상 표시 |
| 7 | final_level_no_next | 최종 레벨 다음 버튼 | ✓ Level 3에서는 다음 버튼 없음 |
| 8 | show_improvement_tips | 개선 팁 표시 | ✓ 실패 시 팁 표시 |

#### 4.2 엣지 케이스

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| E1 | empty_claims_array | 빈 청구항 배열 | ✓ 정상 처리 |
| E2 | very_long_claim_display | 매우 긴 청구항 표시 | ✓ 줄바꿈 처리, 스크롤 가능 |
| E3 | many_claims_scroll | 많은 청구항 (20개) | ✓ 스크롤바 표시, 모두 보임 |
| E4 | special_chars_display | 특수문자 포함 청구항 | ✓ 정상 표시 |
| E5 | emoji_in_claims | 이모지 포함 청구항 | ✓ 정상 표시 |

---

## 3. 통합 테스트 (Integration Tests)

### 3.1 화면 전환 통합 테스트

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| 1 | welcome_to_game_flow | Welcome → Game 전환 | ✓ 게임 화면으로 정상 전환 |
| 2 | game_to_result_flow | Game → Result 전환 | ✓ 결과 화면으로 정상 전환 |
| 3 | result_to_game_flow | Result → Game (다시) | ✓ 같은 레벨 재시작 |
| 4 | result_to_next_level | Result → Game (다음) | ✓ 다음 레벨로 진행 |
| 5 | result_to_welcome | Result → Welcome | ✓ 메인 화면으로 복귀 |
| 6 | complete_level_sequence | Level 1 → 2 → 3 | ✓ 모든 레벨 순차 진행 |

### 3.2 데이터 흐름 통합 테스트

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| 1 | player_name_persistence | 입력한 이름 유지 | ✓ Result 화면에 이름 표시 |
| 2 | level_persistence | 선택한 레벨 유지 | ✓ Game/Result 화면에 레벨 정보 표시 |
| 3 | claims_data_flow | 입력 청구항 → 결과 | ✓ 모든 청구항이 결과 화면에 표시 |
| 4 | level_validation_rules | 레벨별 검증 규칙 | ✓ 각 레벨의 필요 청구항 수 검증 |

### 3.3 시간 초과 통합 테스트

| # | 테스트 명 | 설명 | 예상 결과 |
|----|----------|------|---------|
| 1 | timer_reaches_zero | 타이머 만료 | ✓ 자동 제출, Result 화면 표시 |
| 2 | timer_accurate | 타이머 정확도 (±1초) | ✓ 목표 시간과 ±1초 차이 |
| 3 | timer_level_1 | Level 1 타이머 (300초) | ✓ 정확히 300초 카운트 |
| 4 | timer_level_2 | Level 2 타이머 (600초) | ✓ 정확히 600초 카운트 |
| 5 | timer_level_3 | Level 3 타이머 (900초) | ✓ 정확히 900초 카운트 |

---

## 4. E2E 테스트 (End-to-End)

### 4.1 기본 게임 플로우

| # | 시나리오 | 단계 | 예상 결과 |
|----|----------|------|---------|
| 1 | 게임 완료 (Level 1) | 1. 이름 입력 → 2. Level 1 선택 → 3. 청구항 1개 입력 → 4. 제출 → 5. 성공 결과 확인 | ✓ 모든 단계 정상 완료 |
| 2 | 게임 완료 (Level 2) | 1. 이름 입력 → 2. Level 2 선택 → 3. 청구항 3개 입력 → 4. 제출 → 5. 성공 결과 확인 | ✓ 모든 단계 정상 완료 |
| 3 | 게임 완료 (Level 3) | 1. 이름 입력 → 2. Level 3 선택 → 3. 청구항 5개 입력 → 4. 제출 → 5. 성공 결과 확인 | ✓ 모든 단계 정상 완료 |
| 4 | 게임 실패 (불충분한 청구항) | 1. Level 2 선택 → 2. 청구항 2개만 입력 → 3. 제출 → 4. 실패 결과 확인 | ✓ 실패 화면 표시, 재시도 옵션 |
| 5 | 게임 실패 (너무 짧은 청구항) | 1. 청구항 "짧음" (5자) 입력 → 2. 제출 → 3. 실패 결과 | ✓ 실패 화면 표시 |
| 6 | 타이머 만료 중 게임 | 1. Level 1 시작 → 2. 5분 대기 → 3. 자동 제출 → 4. Result 화면 | ✓ 자동 제출 작동 |
| 7 | 레벨 진행 (1→2→3) | 1. Level 1 통과 → 2. "다음 레벨" 클릭 → 3. Level 2 시작 → 4. 통과 → 5. Level 3 | ✓ 순차 진행 정상 |
| 8 | 재시도 (같은 레벨) | 1. Level 1 실패 → 2. "다시 하기" → 3. 같은 Level 1 재시작 | ✓ 같은 레벨 재시작 |
| 9 | 메인으로 돌아가기 | 1. Game → Result → "메인 메뉴" → Welcome | ✓ Welcome 화면으로 복귀 |
| 10 | 여러 플레이어 연속 게임 | 1. Player A로 Level 1 완료 → 2. 메인으로 → 3. Player B로 다시 시작 | ✓ 각각 독립적으로 진행 |

---

## 5. 사용 케이스 (Use Cases)

### 5.1 정상 사용 케이스

| UC | 제목 | 사용자 | 입력 | 예상 출력 |
|----|-----|--------|------|---------|
| UC1 | 게임 시작 | 신규 사용자 | 이름 + 레벨 선택 | 게임 화면 표시 |
| UC2 | 청구항 작성 | 플레이어 | 청구항 텍스트 | 입력값 저장, 문자 수 표시 |
| UC3 | 검증 확인 | 플레이어 | 제출 버튼 | 검증 결과 피드백 |
| UC4 | 성공 확인 | 플레이어 | 유효한 청구항 | 축하 메시지, 다음 레벨 버튼 |
| UC5 | 실패 처리 | 플레이어 | 무효한 청구항 | 실패 메시지, 재시도 옵션 |
| UC6 | 레벨 진행 | 플레이어 | 다음 레벨 버튼 | 다음 레벨 게임 시작 |
| UC7 | 게임 재시작 | 플레이어 | 다시 하기 버튼 | 같은 레벨 재시작 |
| UC8 | 메인 복귀 | 플레이어 | 메인 메뉴 버튼 | Welcome 화면 |

### 5.2 예외 사용 케이스

| UC | 제목 | 사용자 | 입력 | 예상 출력 |
|----|-----|--------|------|---------|
| UC-E1 | 이름 미입력 | 사용자 | 빈 이름 + 시작 | 에러 메시지, 게임 미시작 |
| UC-E2 | 타임아웃 | 플레이어 | 입력 중 시간 초과 | 자동 제출, 결과 표시 |
| UC-E3 | 빠른 재제출 | 사용자 | 제출 버튼 더블클릭 | 중복 제출 방지 |
| UC-E4 | 브라우저 뒤로가기 | 사용자 | 뒤로 버튼 | 이전 상태 복구 또는 메인으로 |

---

## 6. 테스트 커버리지 목표

| 항목 | 목표 | 현황 |
|------|------|------|
| 단위 테스트 | 80% 이상 | - |
| 통합 테스트 | 모든 주요 흐름 | - |
| E2E 테스트 | 모든 사용 시나리오 | - |
| 엣지 케이스 | 40+ 케이스 | - |

---

## 7. 테스트 실행 명령어

```bash
# 단위 테스트만
npm test -- --testPathPattern="unit"

# 통합 테스트만
npm test -- --testPathPattern="integration"

# E2E 테스트만
npm run test:e2e

# 모든 테스트
npm test

# 커버리지 리포트
npm test -- --coverage

# 특정 테스트 파일
npm test -- GameScreen.test.jsx
```

---

**테스트 파일 위치**: `web/src/__tests__/`

**마지막 업데이트**: 2025년 12월 3일
