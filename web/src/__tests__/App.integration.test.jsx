/**
 * App 통합 테스트
 * 전체 게임 흐름 및 화면 전환 검증
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import App from '../App';

describe('App Integration Tests', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Welcome Screen Navigation', () => {
    test('INT1: Should render welcome screen on initial load', () => {
      render(<App />);

      expect(screen.getByText(/청구항 작성 게임/)).toBeInTheDocument();
      expect(screen.getByLabelText(/플레이어 이름/)).toBeInTheDocument();
    });

    test('INT2: Should navigate from Welcome to Game screen', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Fill in player name
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트플레이어');

      // Click start button
      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // Check if GameScreen is rendered
      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성|게임 화면/)).toBeInTheDocument();
      });
    });

    test('INT3: Should pass correct level to game screen', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Select Level 2
      const level2Card = screen.getByText('종속항 작성').closest('.level-card') ||
                         screen.getByText('종속항 작성').closest('div');
      if (level2Card) {
        await user.click(level2Card);
      }

      // Fill in player name
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      // Click start button
      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // Check if Level 2 requirement is shown
      await waitFor(() => {
        expect(screen.getByText(/필요한 청구항: 3개/)).toBeInTheDocument();
      });
    });
  });

  describe('Game Screen Interaction', () => {
    test('INT4: Should enter game screen and submit valid claim', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Start game
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // Wait for game screen
      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성|게임 화면/)).toBeInTheDocument();
      });

      // Enter a claim
      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '배터리 장치는 양극, 음극, 전해질을 포함한다');

      // Submit
      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // Should navigate to result screen
      await waitFor(() => {
        expect(screen.getByText(/성공|실패|결과/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('INT5: Should prevent submission with invalid claim', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Start game
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // Wait for game screen
      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성|게임 화면/)).toBeInTheDocument();
      });

      // Try to submit empty form
      const submitBtn = screen.getByRole('button', { name: /제출/i });
      expect(submitBtn).toBeDisabled();
    });

    test('INT6: Should handle timer auto-submission', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Start game
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // Wait for game screen
      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성|게임 화면/)).toBeInTheDocument();
      });

      // Add a claim
      const textarea = screen.getAllByRole('textbox')[0];
      fireEvent.change(textarea, {
        target: { value: '배터리 장치는 양극, 음극, 전해질을 포함한다' },
      });

      // Advance timer to end (5 minutes = 300 seconds)
      act(() => {
        jest.advanceTimersByTime(300 * 1000 + 1000);
      });

      // Should auto-submit and show result
      await waitFor(() => {
        expect(screen.getByText(/성공|실패|결과/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Complete Game Flow - Level 1', () => {
    test('INT7: Should complete full Level 1 game from start to finish', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // ===== WELCOME SCREEN =====
      expect(screen.getByText(/청구항 작성 게임/)).toBeInTheDocument();

      // Enter player name
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, 'Level1플레이어');

      // Click start
      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // ===== GAME SCREEN =====
      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성|게임 화면/)).toBeInTheDocument();
      });

      // Verify level 1 requirements
      expect(screen.getByText(/필요한 청구항: 1개/)).toBeInTheDocument();

      // Enter claim
      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], '배터리 장치는 양극, 음극, 전해질을 포함한다');

      // Submit
      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // ===== RESULT SCREEN =====
      await waitFor(() => {
        expect(screen.getByText(/성공|결과/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify player name appears in result
      expect(screen.getByText(/Level1플레이어/)).toBeInTheDocument();

      // Verify claim appears
      expect(screen.getByText(/배터리 장치/)).toBeInTheDocument();

      // Should have next level button
      expect(screen.getByRole('button', { name: /다음 레벨/i })).toBeInTheDocument();
    });
  });

  describe('Complete Game Flow - Level 2', () => {
    test('INT8: Should complete full Level 2 game with multiple claims', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // ===== WELCOME SCREEN =====
      // Select Level 2
      const level2Card = screen.getByText('종속항 작성').closest('.level-card') ||
                         screen.getByText('종속항 작성').closest('div');
      if (level2Card) {
        await user.click(level2Card);
      }

      // Enter player name
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, 'Level2플레이어');

      // Click start
      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // ===== GAME SCREEN =====
      await waitFor(() => {
        expect(screen.getByText(/종속항 작성|게임 화면/)).toBeInTheDocument();
      });

      // Verify level 2 requirements
      expect(screen.getByText(/필요한 청구항: 3개/)).toBeInTheDocument();

      // Add 3 claims
      let textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], '배터리 장치는 양극, 음극, 전해질을 포함한다');

      // Add second claim
      const addBtn = screen.getByRole('button', { name: /청구항 추가/i });
      await user.click(addBtn);

      textareas = screen.getAllByRole('textbox');
      await user.type(textareas[1], '제1항의 배터리에서 양극은 리튬을 포함한다');

      // Add third claim
      await user.click(addBtn);

      textareas = screen.getAllByRole('textbox');
      await user.type(textareas[2], '제1항의 배터리에서 음극은 흑연을 포함한다');

      // Submit
      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // ===== RESULT SCREEN =====
      await waitFor(() => {
        expect(screen.getByText(/성공|결과/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify all claims appear
      expect(screen.getByText(/청구항 수: 3개/)).toBeInTheDocument();
      expect(screen.getByText(/배터리 장치/)).toBeInTheDocument();
      expect(screen.getByText(/제1항의 배터리/)).toBeInTheDocument();
    });
  });

  describe('Retry and Navigation', () => {
    test('INT9: Should navigate to next level from result screen', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Complete Level 1
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성/)).toBeInTheDocument();
      });

      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], '배터리 장치는 양극, 음극, 전해질을 포함한다');

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // Wait for result
      await waitFor(() => {
        expect(screen.getByText(/성공|결과/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Click next level
      const nextBtn = screen.getByRole('button', { name: /다음 레벨/i });
      await user.click(nextBtn);

      // Should now be on Level 2
      await waitFor(() => {
        expect(screen.getByText(/필요한 청구항: 3개/)).toBeInTheDocument();
      });
    });

    test('INT10: Should return to home screen', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Complete a game
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성/)).toBeInTheDocument();
      });

      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], '배터리 장치는 양극, 음극, 전해질을 포함한다');

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // Wait for result
      await waitFor(() => {
        expect(screen.getByText(/성공|결과/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Click home button
      const homeBtn = screen.getByRole('button', { name: /홈|처음으로/i });
      await user.click(homeBtn);

      // Should be back at welcome screen
      await waitFor(() => {
        expect(screen.getByText(/청구항 작성 게임/)).toBeInTheDocument();
        expect(screen.getByLabelText(/플레이어 이름/)).toBeInTheDocument();
      });
    });
  });

  describe('State Management', () => {
    test('INT11: Should maintain player data throughout game', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Set player name in welcome
      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '데이터테스트플레이어');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      // Verify name in game screen
      await waitFor(() => {
        expect(screen.getByText(/데이터테스트플레이어/)).toBeInTheDocument();
      });

      // Submit game
      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], '배터리 장치는 양극, 음극, 전해질을 포함한다');

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // Verify name in result screen
      await waitFor(() => {
        expect(screen.getByText(/데이터테스트플레이어/)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('INT12: Should correctly track and display submitted claims', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성/)).toBeInTheDocument();
      });

      // Enter specific claim
      const claim = '배터리 장치는 양극, 음극, 전해질을 포함한다';
      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], claim);

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      // Verify exact claim appears in result
      await waitFor(() => {
        expect(screen.getByText(new RegExp(claim.substring(0, 10)))).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Error Handling', () => {
    test('INT13: Should handle missing player name gracefully', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Try to start without name
      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      expect(startBtn).toBeDisabled();

      // Verify still on welcome screen
      expect(screen.getByText(/청구항 작성 게임/)).toBeInTheDocument();
    });

    test('INT14: Should handle insufficient claims for level', async () => {
      const user = userEvent.setup({ delay: null });
      render(<App />);

      // Select Level 2
      const level2Card = screen.getByText('종속항 작성').closest('.level-card') ||
                         screen.getByText('종속항 작성').closest('div');
      if (level2Card) {
        await user.click(level2Card);
      }

      const nameInput = screen.getByLabelText(/플레이어 이름/);
      await user.type(nameInput, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      await waitFor(() => {
        expect(screen.getByText(/필요한 청구항: 3개/)).toBeInTheDocument();
      });

      // Try to submit with only 1 claim
      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], '배터리 장치는 양극, 음극, 전해질을 포함한다');

      // Submit button should still work but game should track failure
      const submitBtn = screen.getByRole('button', { name: /제출/i });
      expect(submitBtn).not.toBeDisabled();
    });
  });

  describe('Accessibility Throughout Flow', () => {
    test('INT15: Should maintain keyboard navigation throughout game', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Tab to name input
      await user.tab();
      expect(screen.getByLabelText(/플레이어 이름/)).toHaveFocus();

      // Enter name and start
      await user.keyboard('테스트');
      await user.tab(); // Navigate to button
      expect(screen.getByRole('button', { name: /게임 시작/i })).toHaveFocus();
      await user.keyboard('{Enter}');

      // Should proceed to game screen
      await waitFor(() => {
        expect(screen.getByText(/기본 청구항 작성|게임 화면/)).toBeInTheDocument();
      });
    });
  });
});
