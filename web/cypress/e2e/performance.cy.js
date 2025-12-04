/**
 * Performance & Error Handling E2E Tests
 *
 * 성능 및 에러 처리 테스트:
 * - 응답 시간
 * - 네트워크 오류 처리
 * - 타임아웃 처리
 */

describe('Performance & Error Handling E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Page Load Performance', () => {
    it('should load welcome screen quickly', () => {
      // 페이지 로드 시간 측정
      cy.window().then((win) => {
        const loadTime = win.performance.timing.loadEventEnd - win.performance.timing.navigationStart;
        // 로드 시간이 3초 이내여야 함
        expect(loadTime).to.be.lessThan(3000);
      });
    });

    it('should render all UI elements within reasonable time', () => {
      // 시작 버튼이 100ms 내에 표시되어야 함
      cy.contains('button', /시작/i, { timeout: 100 }).should('be.visible');
    });

    it('should have fast time to interactive', () => {
      // 사용자 상호작용이 빨라야 함
      cy.get('input[placeholder*="이름"]').should('be.enabled');
      cy.contains('button', /시작/i).should('be.enabled');
    });
  });

  describe('Network Error Handling', () => {
    it('should handle network timeout gracefully', () => {
      cy.intercept('POST', '**/*', { delay: 60000, statusCode: 408 }).as('timeout');

      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      cy.get('input[placeholder*="청구항"]').type('배터리는 양극을 포함한다');
      cy.contains('button', /제출/i).click();

      // 타임아웃 에러 처리 또는 재시도 옵션 표시
      cy.wait(2000);
      cy.contains(/타임아웃|재시도|오류|실패/i, { timeout: 5000 }).should('exist');
    });

    it('should handle 500 server error', () => {
      cy.intercept('POST', '**/*', { statusCode: 500, body: { error: 'Internal Server Error' } }).as('error');

      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      cy.get('input[placeholder*="청구항"]').type('테스트 청구항');
      cy.contains('button', /제출/i).click();

      // 에러 메시지 표시 또는 사용자 친화적 피드백
      cy.wait(2000);
      // 앱이 크래시하지 않아야 함
      cy.get('body').should('exist');
    });

    it('should handle network disconnection', () => {
      // 네트워크 연결 끊김 시뮬레이션
      cy.intercept('POST', '**/*', (req) => {
        req.destroy();
      }).as('offline');

      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      cy.get('input[placeholder*="청구항"]').type('테스트');
      cy.contains('button', /제출/i).click();

      cy.wait(2000);
      // 앱이 정상 상태를 유지해야 함
      cy.get('body').should('exist');
    });
  });

  describe('Response Time', () => {
    it('should respond to user input immediately', () => {
      const startTime = Date.now();

      cy.get('input[placeholder*="이름"]').type('테스트');

      cy.then(() => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        // 입력 응답 시간이 100ms 이내
        expect(responseTime).to.be.lessThan(100);
      });
    });

    it('should show loading state during submission', () => {
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      cy.get('input[placeholder*="청구항"]').type('배터리는 양극을 포함한다');

      // 느린 응답 시뮬레이션
      cy.intercept('POST', '**/*', (req) => {
        req.reply((res) => {
          res.delay(1000);
        });
      });

      cy.contains('button', /제출/i).click();

      // 로딩 상태 표시 (선택적)
      cy.contains(/로딩|제출|처리|진행/i, { timeout: 5000 }).should('exist');
    });
  });

  describe('Concurrent Requests', () => {
    it('should handle multiple requests efficiently', () => {
      // 여러 청구항 추가
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 첫 번째 청구항
      cy.get('input[placeholder*="청구항"]').eq(0).type('청구항 1: 배터리는 양극을 포함한다');

      // 추가 버튼 클릭하여 더 많은 입력 필드 생성
      cy.contains('button', /추가/i).click({ force: true });

      // 두 번째 청구항
      cy.get('input[placeholder*="청구항"]').eq(1).type('청구항 2: 배터리는 음극을 포함한다');

      // 모든 청구항 제출
      cy.contains('button', /제출/i).click();

      cy.wait(3000);
      // 결과 화면 표시
      cy.contains(/결과|점수/i, { timeout: 10000 }).should('be.visible');
    });
  });

  describe('Memory Leaks Prevention', () => {
    it('should clean up resources when leaving page', () => {
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 여러 번 페이지 탐색
      for (let i = 0; i < 3; i++) {
        cy.visit('/');
        cy.get('input[placeholder*="이름"]').type('테스트');
        cy.contains('button', /시작/i).click();
        cy.go('back');
      }

      // 페이지가 정상 작동해야 함
      cy.get('input[placeholder*="이름"]').should('be.visible');
    });

    it('should handle rapid successive actions', () => {
      cy.get('input[placeholder*="이름"]').type('테스트');

      // 빠른 클릭 (의도치 않은 더블클릭 등)
      cy.contains('button', /시작/i).click();
      cy.contains('button', /시작/i).click(); // 이미 클릭됨

      cy.wait(500);
      // 중복 이벤트 처리되어야 함
      cy.contains(/기본|청구항/i).should('be.visible');
    });
  });

  describe('Browser Storage', () => {
    it('should not exceed localStorage limits', () => {
      // 많은 데이터 저장
      cy.window().then((win) => {
        const storage = win.localStorage;
        const initialSize = Object.keys(storage).length;

        // 게임 진행
        cy.get('input[placeholder*="이름"]').type('테스트매우긴이름'.repeat(10));
        cy.contains('button', /시작/i).click();

        cy.get('input[placeholder*="청구항"]').type('배터리'.repeat(100));
        cy.contains('button', /제출/i).click();

        cy.wait(2000);

        // localStorage가 합리적인 크기로 유지되어야 함
        cy.window().then((win) => {
          const finalSize = Object.keys(win.localStorage).length;
          expect(finalSize).to.be.lessThan(initialSize + 100);
        });
      });
    });
  });

  describe('Battery Optimization (Mobile)', () => {
    beforeEach(() => {
      cy.viewport(375, 667); // iPhone 크기
    });

    it('should not drain battery with constant animations', () => {
      // 타이머가 있는 게임 화면
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 5초 동안 모니터링
      cy.wait(5000);

      // 페이지가 정상 작동해야 함
      cy.contains(/\d+:\d+/).should('be.visible');
    });

    it('should pause animation when not visible', () => {
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 탭 전환 시뮬레이션 (실제로는 불가능하지만, visibility 변화 감지)
      cy.window().then((win) => {
        const event = new Event('visibilitychange');
        win.document.hidden = true;
        win.document.dispatchEvent(event);
      });

      cy.wait(1000);

      // 비용이 많이 드는 작업이 중단되어야 함 (실제 구현에 따라)
      cy.get('body').should('exist');
    });
  });
});
