/**
 * Game Flow E2E Tests
 *
 * 전체 게임 플로우 테스트:
 * - 게임 시작 → 청구항 입력 → 제출 → 결과 확인
 */

describe('Complete Game Flow E2E Tests', () => {
  beforeEach(() => {
    // 앱 시작 전에 localhost:3000이 실행 중인지 확인
    cy.visit('/');
  });

  describe('Welcome Screen', () => {
    it('should display welcome screen with title', () => {
      cy.contains(/특허|청구항|게임/i).should('be.visible');
    });

    it('should have player name input field', () => {
      cy.get('input[placeholder*="이름"]').should('be.visible');
    });

    it('should have level selection options', () => {
      cy.contains(/레벨|기본|종속|복합/i).should('be.visible');
      cy.get('input[type="radio"]').should('have.length.at.least', 3);
    });

    it('should have start button', () => {
      cy.contains('button', /시작|시작하기/i).should('be.visible');
    });
  });

  describe('Player can start game', () => {
    it('should start game with valid player name', () => {
      // 플레이어 이름 입력
      cy.get('input[placeholder*="이름"]').type('테스트플레이어');

      // 게임 시작
      cy.contains('button', /시작|시작하기/i).click();

      // 게임 화면 표시 확인
      cy.contains(/기본 청구항|종속항|복합/i).should('be.visible');
    });

    it('should not start game with empty name', () => {
      // 플레이어 이름 입력 없이
      cy.contains('button', /시작|시작하기/i).click();

      // 여전히 환영 화면에 있어야 함
      cy.contains(/특허|청구항|게임/i).should('be.visible');
    });

    it('should remember selected level when starting', () => {
      // 레벨 2 선택
      cy.get('input[type="radio"]').eq(1).click({ force: true });

      // 플레이어 이름 입력
      cy.get('input[placeholder*="이름"]').type('테스트');

      // 게임 시작
      cy.contains('button', /시작|시작하기/i).click();

      // 레벨 2 화면 확인
      cy.contains(/종속항|종속/i).should('be.visible');
    });
  });

  describe('Game Screen - Basic Level (Level 1)', () => {
    beforeEach(() => {
      // 게임 시작
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작|시작하기/i).click();
      cy.contains(/기본 청구항/i).should('be.visible');
    });

    it('should display game screen with timer', () => {
      // 타이머 표시 확인 (MM:SS 형식)
      cy.contains(/\d+:\d+/).should('be.visible');
    });

    it('should display claim input field', () => {
      cy.get('input[placeholder*="청구항"]').should('be.visible');
    });

    it('should display submit button', () => {
      cy.contains('button', /제출|완료/i).should('be.visible');
    });

    it('should allow entering a claim', () => {
      const claimText = '배터리는 양극, 음극, 전해질을 포함한다';
      cy.get('input[placeholder*="청구항"]').type(claimText);
      cy.get('input[placeholder*="청구항"]').should('have.value', claimText);
    });

    it('should add new claim input when add button clicked', () => {
      // 초기 입력 필드 확인
      cy.get('input[placeholder*="청구항"]').should('have.length', 1);

      // 추가 버튼 클릭 (있는 경우)
      cy.contains('button', /추가/i).click({ force: true });

      // 입력 필드 증가 확인
      cy.get('input[placeholder*="청구항"]').should('have.length', 2);
    });
  });

  describe('Claim Submission', () => {
    beforeEach(() => {
      // 게임 시작 및 기본 설정
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작|시작하기/i).click();
      cy.contains(/기본 청구항/i).should('be.visible');
    });

    it('should not submit empty claim', () => {
      // 입력 없이 제출 시도
      cy.contains('button', /제출|완료/i).click();

      // 여전히 게임 화면에 있어야 함
      cy.get('input[placeholder*="청구항"]').should('exist');
    });

    it('should submit valid claim', () => {
      const claimText = '배터리 장치는 양극과 음극을 포함한다';

      // 청구항 입력
      cy.get('input[placeholder*="청구항"]').type(claimText);

      // 제출
      cy.contains('button', /제출|완료/i).click();

      // 제출 후 상태 변화 (로딩 또는 결과 화면으로 이동)
      cy.wait(2000); // API 호출 대기

      // 결과 화면 또는 "제출 완료" 메시지
      cy.contains(/결과|제출|완료|점수/i).should('be.visible');
    });

    it('should display submission status', () => {
      const claimText = '청구항 내용: 배터리는 케이싱을 포함한다';

      cy.get('input[placeholder*="청구항"]').type(claimText);
      cy.contains('button', /제출|완료/i).click();

      // 제출 완료 상태 표시
      cy.contains(/제출완료|완료|결과/i).should('be.visible', { timeout: 5000 });
    });
  });

  describe('Results Screen', () => {
    beforeEach(() => {
      // 게임 완료까지 진행
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작|시작하기/i).click();

      const claimText = '배터리는 양극, 음극을 포함하는 에너지 저장 장치이다';
      cy.get('input[placeholder*="청구항"]').type(claimText);
      cy.contains('button', /제출|완료/i).click();

      // 결과 화면 대기
      cy.contains(/결과|점수|평가/i, { timeout: 10000 }).should('be.visible');
    });

    it('should display results screen', () => {
      cy.contains(/결과|점수/i).should('be.visible');
    });

    it('should display player score', () => {
      // 점수 표시 (0-100 범위)
      cy.contains(/점수|스코어/i).should('be.visible');
    });

    it('should display feedback for claims', () => {
      // 피드백 표시
      cy.contains(/피드백|평가|청구항/i).should('be.visible');
    });

    it('should have restart button', () => {
      cy.contains('button', /재시작|다시|처음/i).should('be.visible');
    });

    it('should have exit button', () => {
      cy.contains('button', /종료|나가기|끝내기/i).should('be.visible');
    });

    it('should restart game when restart button clicked', () => {
      cy.contains('button', /재시작|다시/i).click();

      // 환영 화면으로 돌아가야 함
      cy.contains(/특허|청구항|게임/i).should('be.visible');
      cy.get('input[placeholder*="이름"]').should('be.empty');
    });
  });

  describe('Multiple Levels', () => {
    it('should handle level 2 (dependent claims)', () => {
      // 레벨 2 선택
      cy.get('input[type="radio"]').eq(1).click({ force: true });
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 레벨 2 화면 확인
      cy.contains(/종속항|종속/i).should('be.visible');

      // 청구항 입력
      const claim1 = '배터리는 양극, 음극을 포함한다';
      cy.get('input[placeholder*="청구항"]').eq(0).type(claim1);

      // 제출
      cy.contains('button', /제출/i).click();
      cy.wait(2000);

      // 결과 확인
      cy.contains(/결과|점수/i, { timeout: 10000 }).should('be.visible');
    });

    it('should handle level 3 (complex claims)', () => {
      // 레벨 3 선택
      cy.get('input[type="radio"]').eq(2).click({ force: true });
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 레벨 3 화면 확인
      cy.contains(/복합|복합 청구항/i).should('be.visible');

      // 청구항 입력
      const claim = '배터리 시스템은 양극, 음극, 전해질을 포함하고 안전 회로를 구비한다';
      cy.get('input[placeholder*="청구항"]').type(claim);

      // 제출
      cy.contains('button', /제출/i).click();
      cy.wait(2000);

      // 결과 확인
      cy.contains(/결과|점수/i, { timeout: 10000 }).should('be.visible');
    });
  });

  describe('Edge Cases', () => {
    beforeEach(() => {
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();
      cy.contains(/기본 청구항/i).should('be.visible');
    });

    it('should handle very long claim text', () => {
      const longClaim = '배터리'.repeat(50); // 매우 긴 청구항
      cy.get('input[placeholder*="청구항"]').type(longClaim);
      cy.contains('button', /제출/i).click();

      cy.wait(2000);
      // 에러 또는 결과 화면 표시
      cy.contains(/결과|에러|오류|점수/i, { timeout: 10000 }).should('be.visible');
    });

    it('should handle special characters in claim', () => {
      const claimWithSpecialChars = '배터리 (양극), [음극], {전해질} - 에너지 저장 장치';
      cy.get('input[placeholder*="청구항"]').type(claimWithSpecialChars);
      cy.contains('button', /제출/i).click();

      cy.wait(2000);
      cy.contains(/결과|점수|평가/i, { timeout: 10000 }).should('be.visible');
    });

    it('should handle whitespace in claim', () => {
      const claimWithWhitespace = '  배터리는   양극,   음극을  포함한다  ';
      cy.get('input[placeholder*="청구항"]').type(claimWithWhitespace);
      cy.contains('button', /제출/i).click();

      cy.wait(2000);
      cy.contains(/결과|점수/i, { timeout: 10000 }).should('be.visible');
    });
  });
});
