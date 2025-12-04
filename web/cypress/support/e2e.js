// cypress/support/e2e.js
// Support file for E2E tests

// Disable uncaught exception handling for controlled testing
Cypress.on('uncaught:exception', (err, runnable) => {
  // Ignore ResizeObserver errors which are non-critical
  if (err.message.includes('ResizeObserver loop limit exceeded')) {
    return false;
  }
  // Let other errors fail the test
  return true;
});

// Custom command to fill input with Korean text
Cypress.Commands.add('typeKorean', (selector, text) => {
  cy.get(selector).then(($input) => {
    $input.val(text);
    cy.get(selector).trigger('change').trigger('blur');
  });
});

// Custom command to submit claim
Cypress.Commands.add('submitClaim', (claimText) => {
  cy.typeKorean('input[placeholder*="청구항"]', claimText);
  cy.contains('button', /제출|완료/i).click();
});

// Custom command to wait for game screen
Cypress.Commands.add('waitForGameScreen', () => {
  cy.contains(/기본|종속|복합/).should('be.visible');
});

// Custom command to wait for results screen
Cypress.Commands.add('waitForResultsScreen', () => {
  cy.contains(/결과|점수/i).should('be.visible');
});
