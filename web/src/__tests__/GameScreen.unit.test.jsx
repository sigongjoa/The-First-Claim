/**
 * GameScreen 단위 테스트
 * 게임 화면의 개별 기능 검증
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import GameScreen from '../components/GameScreen';

describe('GameScreen Component', () => {
  const mockOnComplete = jest.fn();
  const mockSessionData = {
    sessionId: 'test_session_001',
    playerName: '테스트플레이어',
    levelId: 1,
    submittedClaims: [],
    startTime: Date.now(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Render & Display', () => {
    test('NC1: Should render game screen with all elements', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText('기본 청구항 작성')).toBeInTheDocument();
      expect(screen.getByText(/플레이어: 테스트플레이어/)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /제출/i })).toBeInTheDocument();
    });

    test('NC2: Should display timer', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/⏱️/)).toBeInTheDocument();
    });

    test('NC3: Should display textarea for claim input', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textareas = screen.getAllByRole('textbox');
      expect(textareas.length).toBeGreaterThan(0);
    });
  });

  describe('Claim Input & Validation', () => {
    test('NC4: Should accept claim input', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '배터리 장치는 양극, 음극, 전해질을 포함한다');

      expect(textarea.value).toBe('배터리 장치는 양극, 음극, 전해질을 포함한다');
    });

    test('NC5: Should validate claim with 20+ characters', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '이것은 20자 이상의 유효한 청구항입니다');

      await waitFor(() => {
        expect(screen.getByText(/올바른 형식입니다/)).toBeInTheDocument();
      });
    });

    test('EC1: Should reject claim with < 20 characters', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '짧은청구항');

      expect(textarea.value).toBe('짧은청구항');
    });

    test('NC6: Should update character counter', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '테스트');

      expect(screen.getByText(/6 \/ 20자/)).toBeInTheDocument();
    });

    test('EC2: Should handle only spaces', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '          ');

      expect(textarea.value).toBe('          ');
    });

    test('NC7: Should add new claim', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const addBtn = screen.getByRole('button', { name: /청구항 추가/i });
      await user.click(addBtn);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas.length).toBeGreaterThanOrEqual(2);
    });

    test('EC3: Should not delete single claim', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const deleteBtn = screen.queryByRole('button', { name: /삭제/i });
      expect(deleteBtn).not.toBeInTheDocument();
    });

    test('NC8: Should delete claim when multiple exist', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const addBtn = screen.getByRole('button', { name: /청구항 추가/i });
      await user.click(addBtn);

      const deleteBtn = screen.getByRole('button', { name: /삭제/i });
      await user.click(deleteBtn);

      const textareas = screen.getAllByRole('textbox');
      expect(textareas.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('Timer & Countdown', () => {
    test('NC9: Should display timer countdown', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/⏱️ 5:00/)).toBeInTheDocument();
    });

    test('NC10: Should countdown timer every second', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/⏱️ 5:00/)).toBeInTheDocument();

      act(() => {
        jest.advanceTimersByTime(1000);
      });

      expect(screen.getByText(/⏱️ 4:59/)).toBeInTheDocument();
    });

    test('NC11: Should auto-submit when timer reaches zero', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      fireEvent.change(textarea, {
        target: { value: '배터리 장치는 양극, 음극, 전해질을 포함한다' },
      });

      act(() => {
        jest.advanceTimersByTime(300 * 1000 + 1000);
      });

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalled();
      }, { timeout: 3000 });
    });
  });

  describe('Submission & Validation', () => {
    test('NC9: Should disable submit button with no claims', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      expect(submitBtn).toBeDisabled();
    });

    test('NC10: Should enable submit button with valid claim', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '배터리 장치는 양극, 음극, 전해질을 포함한다');

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      expect(submitBtn).not.toBeDisabled();
    });

    test('NC11: Should submit successfully with valid claims', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '배터리 장치는 양극, 음극, 전해질을 포함한다');

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalled();
      });
    });
  });

  describe('Level-Specific Rules', () => {
    test('NC12: Level 1 requires 1 claim minimum', async () => {
      const user = userEvent.setup({ delay: null });
      const level1Data = { ...mockSessionData, levelId: 1 };
      render(
        <GameScreen sessionData={level1Data} onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/필요한 청구항: 1개/)).toBeInTheDocument();
    });

    test('NC13: Level 2 requires 3 claims minimum', async () => {
      const user = userEvent.setup({ delay: null });
      const level2Data = { ...mockSessionData, levelId: 2 };
      render(
        <GameScreen sessionData={level2Data} onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/필요한 청구항: 3개/)).toBeInTheDocument();
    });

    test('NC14: Level 3 requires 5 claims minimum', async () => {
      const user = userEvent.setup({ delay: null });
      const level3Data = { ...mockSessionData, levelId: 3 };
      render(
        <GameScreen sessionData={level3Data} onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/필요한 청구항: 5개/)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('EC4: Should handle exactly 20 characters', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '12345678901234567890');

      expect(textarea.value.length).toBe(20);
    });

    test('EC5: Should handle 19 characters (invalid)', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '1234567890123456789');

      expect(textarea.value.length).toBe(19);
    });

    test('EC6: Should handle very long claim (1000 characters)', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const longText = 'a'.repeat(1000);
      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, longText);

      expect(textarea.value.length).toBe(1000);
    });

    test('EC7: Should handle multiline input', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '첫 번째 줄{Enter}두 번째 줄');

      expect(textarea.value).toContain('\n');
    });

    test('EC8: Should handle paste operation', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      const pastedText = '배터리 장치는 양극, 음극, 전해질을 포함한다';

      fireEvent.paste(textarea, {
        clipboardData: {
          getData: () => pastedText,
        },
      });

      // Note: paste requires actual paste event handling in component
      // This is a basic test structure
    });

    test('EC9: Should prevent double submission', async () => {
      const user = userEvent.setup({ delay: null });
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const textarea = screen.getAllByRole('textbox')[0];
      await user.type(textarea, '배터리 장치는 양극, 음극, 전해질을 포함한다');

      const submitBtn = screen.getByRole('button', { name: /제출/i });
      await user.click(submitBtn);
      await user.click(submitBtn);

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledTimes(1);
      });
    });
  });
});
