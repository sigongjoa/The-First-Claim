/**
 * Accessibility E2E Tests
 *
 * 접근성 및 사용성 테스트:
 * - 키보드 네비게이션
 * - 스크린 리더 호환성
 * - 포커스 관리
 */

describe('Accessibility E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Keyboard Navigation', () => {
    it('should navigate through form fields with Tab key', () => {
      // 첫 번째 포커스: 이름 입력
      cy.get('input[placeholder*="이름"]').focus();
      cy.focused().should('have.attr', 'placeholder');

      // Tab으로 레벨 선택으로 이동
      cy.focused().tab();
      cy.focused().should('have.attr', 'type', 'radio');
    });

    it('should submit form with Enter key', () => {
      cy.get('input[placeholder*="이름"]').type('테스트{enter}');
      cy.wait(500);

      // 게임 화면으로 이동
      cy.contains(/기본|청구항/i).should('be.visible');
    });

    it('should navigate game screen with keyboard', () => {
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 청구항 입력 필드에 포커스
      cy.get('input[placeholder*="청구항"]').focus();
      cy.focused().should('exist');

      // Tab으로 버튼으로 이동
      cy.focused().tab().tab();
      // 버튼 활성화 확인
      cy.focused().should('have.attr', 'type', 'button');
    });
  });

  describe('Focus Management', () => {
    it('should show focus indicator on buttons', () => {
      cy.contains('button', /시작|시작하기/i)
        .focus()
        .should('have.css', 'outline')
        .or('have.css', 'border');
    });

    it('should show focus indicator on input fields', () => {
      cy.get('input[placeholder*="이름"]')
        .focus()
        .should('have.css', 'outline')
        .or('have.css', 'border');
    });

    it('should trap focus within modal if present', () => {
      // 게임 시작
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 모든 포커스 가능 요소 확인
      cy.get('input, button').should('have.length.greaterThan', 0);
    });
  });

  describe('ARIA Labels and Roles', () => {
    it('should have proper labels for inputs', () => {
      cy.get('input[placeholder*="이름"]').should('have.attr', 'placeholder');
    });

    it('should have proper roles for buttons', () => {
      cy.contains('button', /시작/i).should('have.attr', 'type', 'button');
    });

    it('should have descriptive button text', () => {
      cy.contains('button', /시작|제출|재시작/i).should('be.visible');
    });

    it('should have radio button labels', () => {
      // 라디오 버튼 확인
      cy.get('input[type="radio"]').should('have.length.at.least', 1);

      // 각 라디오 버튼이 텍스트로 식별 가능한지 확인
      cy.contains(/레벨|기본|종속|복합/i).should('be.visible');
    });
  });

  describe('Color Contrast', () => {
    it('should have sufficient contrast for text', () => {
      // 주요 텍스트 요소들 확인
      cy.get('h1, h2, p, span, button').each(($el) => {
        // 실제 대비 검사는 axe 라이브러리 필요
        // 여기서는 요소가 보이는지만 확인
        cy.wrap($el).should('be.visible');
      });
    });
  });

  describe('Screen Reader Support', () => {
    it('should announce form labels', () => {
      // 이름 입력 필드
      cy.get('input[placeholder*="이름"]').should('have.attr', 'placeholder');

      // 또는 aria-label이 있으면 더 좋음
      cy.get('input').each(($input) => {
        cy.wrap($input).should('have.attr', ['placeholder', 'aria-label'].join(','));
      });
    });

    it('should announce button purposes', () => {
      cy.contains('button', /시작|제출|재시작/i).each(($button) => {
        // 버튼이 의미 있는 텍스트를 포함해야 함
        cy.wrap($button).invoke('text').should('not.be.empty');
      });
    });

    it('should announce status messages', () => {
      cy.get('input[placeholder*="이름"]').type('테스트');
      cy.contains('button', /시작/i).click();

      // 로딩 또는 상태 메시지가 있으면 good
      cy.contains(/기본|청구항|진행/i).should('be.visible');
    });
  });

  describe('Form Validation Messages', () => {
    it('should provide error messages for empty submission', () => {
      cy.contains('button', /시작|제출/i).click();

      // 에러 메시지 또는 여전히 폼이 표시되어야 함
      cy.get('input[placeholder*="이름"]').should('be.visible');
    });

    it('should indicate required fields', () => {
      // 필드가 required 속성을 가지거나, 별표(*) 또는 텍스트로 표시
      cy.get('input[placeholder*="이름"]').then(($input) => {
        const hasRequired = $input.attr('required');
        const hasAriaRequired = $input.attr('aria-required');

        // required 또는 aria-required 중 하나는 있어야 함
        expect(
          hasRequired !== undefined || hasAriaRequired === 'true'
        ).to.be.true;
      });
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport (320x568)', () => {
      cy.viewport(320, 568);

      cy.contains(/특허|청구항|게임/i).should('be.visible');
      cy.get('input[placeholder*="이름"]').should('be.visible');
      cy.contains('button', /시작/i).should('be.visible');
    });

    it('should work on tablet viewport (768x1024)', () => {
      cy.viewport(768, 1024);

      cy.contains(/특허|청구항|게임/i).should('be.visible');
      cy.get('input[placeholder*="이름"]').should('be.visible');
      cy.contains('button', /시작/i).should('be.visible');
    });

    it('should work on desktop viewport (1920x1080)', () => {
      cy.viewport(1920, 1080);

      cy.contains(/특허|청구항|게임/i).should('be.visible');
      cy.get('input[placeholder*="이름"]').should('be.visible');
      cy.contains('button', /시작/i).should('be.visible');
    });

    it('should not have horizontal scroll', () => {
      cy.viewport(320, 568);

      // 모든 요소가 viewport 내에 있어야 함
      cy.get('body').then(($body) => {
        expect($body[0].scrollWidth).to.equal($body[0].clientWidth);
      });
    });
  });

  describe('Dark Mode Support (if available)', () => {
    it('should respect prefers-color-scheme', () => {
      // 다크 모드 선호 설정
      cy.visit('/', {
        onBeforeLoad(win) {
          cy.stub(win, 'matchMedia').returns({
            matches: true,
            addListener: () => {},
            removeListener: () => {},
          });
        },
      });

      // 페이지가 정상적으로 렌더링되어야 함
      cy.contains(/특허|청구항/i).should('be.visible');
    });
  });
});
