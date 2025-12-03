/**
 * WelcomeScreen 단위 테스트
 * 환영 화면의 개별 기능 검증
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import WelcomeScreen from '../components/WelcomeScreen';

describe('WelcomeScreen Component', () => {
  // Mock callback
  const mockOnStartGame = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Normal Cases', () => {
    test('NC1: Should render welcome screen with all elements', () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      expect(screen.getByText('🎮 청구항 작성 게임')).toBeInTheDocument();
      expect(screen.getByLabelText('플레이어 이름')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /게임 시작/i })).toBeInTheDocument();
    });

    test('NC2: Should display three levels', () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      expect(screen.getByText('기본 청구항 작성')).toBeInTheDocument();
      expect(screen.getByText('종속항 작성')).toBeInTheDocument();
      expect(screen.getByText('복합 청구항 세트')).toBeInTheDocument();
    });

    test('NC3: Should select level when clicked', async () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const level2Card = screen.getByText('종속항 작성').closest('.level-card');
      fireEvent.click(level2Card);

      await waitFor(() => {
        expect(level2Card).toHaveClass('active');
      });
    });

    test('NC4: Should update player name on input', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '테스트플레이어');

      expect(input.value).toBe('테스트플레이어');
    });

    test('NC5: Should disable start button without name', () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      expect(startBtn).toBeDisabled();
    });

    test('NC6: Should enable start button with name', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '테스트');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      expect(startBtn).not.toBeDisabled();
    });

    test('NC7: Should call onStartGame callback on button click', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      await user.type(screen.getByLabelText('플레이어 이름'), '테스트');
      await user.click(screen.getByRole('button', { name: /게임 시작/i }));

      await waitFor(() => {
        expect(mockOnStartGame).toHaveBeenCalledWith('테스트', 1);
      });
    });

    test('NC8: Should default to level 1 selection', () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const level1Card = screen.getByText('기본 청구항 작성').closest('.level-card');
      expect(level1Card).toHaveClass('active');
    });
  });

  describe('Edge Cases', () => {
    test('EC1: Should show error for empty name', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      expect(screen.getByText(/플레이어 이름을 입력해주세요/i)).toBeInTheDocument();
    });

    test('EC2: Should show error for whitespace-only name', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '   ');

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      expect(startBtn).toBeDisabled();
    });

    test('EC3: Should handle very long name (100 characters)', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const longName = 'a'.repeat(100);
      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, longName);

      expect(input.value.length).toBeLessThanOrEqual(100);
    });

    test('EC4: Should accept special characters in name', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '테스트-player_123');

      expect(input.value).toBe('테스트-player_123');
    });

    test('EC5: Should accept emoji in name', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '플레이어🎮');

      expect(input.value).toContain('🎮');
    });

    test('EC6: Should handle rapid level clicks', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const level2 = screen.getByText('종속항 작성').closest('.level-card');
      const level3 = screen.getByText('복합 청구항 세트').closest('.level-card');

      await user.click(level2);
      await user.click(level3);
      await user.click(level2);

      expect(level2).toHaveClass('active');
    });

    test('EC7: Should start game with Enter key', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '테스트');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(mockOnStartGame).toHaveBeenCalledWith('테스트', 1);
      });
    });

    test('EC8: Should clear error message after name input', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const startBtn = screen.getByRole('button', { name: /게임 시작/i });
      await user.click(startBtn);

      expect(screen.getByText(/플레이어 이름을 입력해주세요/i)).toBeInTheDocument();

      const input = screen.getByLabelText('플레이어 이름');
      await user.type(input, '테스트');

      expect(screen.queryByText(/플레이어 이름을 입력해주세요/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('ACC1: Should have proper labels for inputs', () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const input = screen.getByLabelText('플레이어 이름');
      expect(input).toBeInTheDocument();
    });

    test('ACC2: Should have descriptive button text', () => {
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      const button = screen.getByRole('button', { name: /게임 시작/i });
      expect(button).toHaveTextContent('게임 시작');
    });

    test('ACC3: Should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(<WelcomeScreen onStartGame={mockOnStartGame} />);

      await user.tab();
      expect(screen.getByLabelText('플레이어 이름')).toHaveFocus();
    });
  });
});
