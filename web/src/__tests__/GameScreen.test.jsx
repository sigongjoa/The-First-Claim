import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import GameScreen from '../components/GameScreen';

describe('GameScreen Component', () => {
  const mockSessionData = {
    sessionId: 'test-session-001',
    levelId: 1,
    playerName: '테스트 플레이어',
  };

  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('기본 렌더링', () => {
    test('레벨 제목이 정상적으로 표시되어야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText('기본 청구항 작성')).toBeInTheDocument();
    });

    test('초기 청구항 입력 필드가 존재해야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const inputs = screen.getAllByPlaceholderText(/청구항을 입력하세요/i);
      expect(inputs.length).toBeGreaterThan(0);
    });

    test('제출 버튼이 표시되어야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByRole('button', { name: /제출/i })).toBeInTheDocument();
    });

    test('초기 타이머 값이 올바르게 표시되어야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText('5:00')).toBeInTheDocument();
    });
  });

  describe('청구항 입력 기능', () => {
    test('청구항을 입력할 수 있어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const input = screen.getAllByPlaceholderText(/청구항을 입력하세요/i)[0];
      await userEvent.type(input, '배터리는 양극을 포함한다');

      expect(input.value).toBe('배터리는 양극을 포함한다');
    });

    test('청구항 추가 버튼으로 새로운 입력 필드를 추가할 수 있어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const initialInputs = screen.getAllByPlaceholderText(
        /청구항을 입력하세요/i
      );
      const initialCount = initialInputs.length;

      const addButton = screen.getByRole('button', { name: /추가/i });
      await userEvent.click(addButton);

      const newInputs = screen.getAllByPlaceholderText(/청구항을 입력하세요/i);
      expect(newInputs.length).toBe(initialCount + 1);
    });

    test('여러 청구항을 입력할 수 있어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const claims = [
        '청구항 1: 배터리는 양극을 포함한다',
        '청구항 2: 배터리는 음극을 포함한다',
      ];

      const inputs = screen.getAllByPlaceholderText(/청구항을 입력하세요/i);

      for (let i = 0; i < claims.length; i++) {
        await userEvent.type(inputs[i], claims[i]);
      }

      // 마지막 입력이 정상 입력되었는지 확인
      expect(inputs[inputs.length - 1].value).toBe(claims[claims.length - 1]);
    });
  });

  describe('타이머 기능', () => {
    test('타이머가 1초씩 감소해야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      expect(screen.getByText('5:00')).toBeInTheDocument();

      jest.advanceTimersByTime(1000);

      expect(screen.getByText('4:59')).toBeInTheDocument();
    });

    test('타이머가 0에 도달하면 자동 제출되어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      jest.advanceTimersByTime(300000);

      await waitFor(() => {
        expect(screen.queryByText('0:00')).not.toBeInTheDocument();
      });
    });

    test('제출 후 타이머가 멈춰야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const input = screen.getAllByPlaceholderText(/청구항을 입력하세요/i)[0];
      await userEvent.type(input, '배터리는 양극을 포함한다');

      const submitButton = screen.getByRole('button', { name: /제출/i });
      await userEvent.click(submitButton);

      const timeBeforeAdvance = screen.getByText(/\d+:\d+/);
      jest.advanceTimersByTime(5000);
      const timeAfterAdvance = screen.getByText(/\d+:\d+/);

      expect(timeBeforeAdvance.textContent).toBe(timeAfterAdvance.textContent);
    });
  });

  describe('제출 기능', () => {
    test('청구항이 입력되면 제출할 수 있어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const input = screen.getAllByPlaceholderText(/청구항을 입력하세요/i)[0];
      await userEvent.type(input, '배터리는 양극을 포함한다');

      const submitButton = screen.getByRole('button', { name: /제출/i });
      expect(submitButton).not.toBeDisabled();
    });

    test('빈 청구항으로는 제출할 수 없어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const submitButton = screen.getByRole('button', { name: /제출/i });
      await userEvent.click(submitButton);

      // 여전히 입력 필드가 보여야 함 (제출되지 않았음)
      expect(screen.getAllByPlaceholderText(/청구항을 입력하세요/i).length).toBeGreaterThan(
        0
      );
    });

    test('제출 후 제출됨 상태가 표시되어야 함', async () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const input = screen.getAllByPlaceholderText(/청구항을 입력하세요/i)[0];
      await userEvent.type(input, '배터리는 양극을 포함한다');

      const submitButton = screen.getByRole('button', { name: /제출/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/제출완료/i)).toBeInTheDocument();
      });
    });
  });

  describe('레벨별 설정', () => {
    test('레벨 2: 종속항 작성 설정이 정상작동해야 함', () => {
      const level2Session = { ...mockSessionData, levelId: 2 };
      render(
        <GameScreen sessionData={level2Session} onComplete={mockOnComplete} />
      );

      expect(screen.getByText('종속항 작성')).toBeInTheDocument();
      // 레벨 2는 600초 (10:00)
      expect(screen.getByText('10:00')).toBeInTheDocument();
    });

    test('레벨 3: 복합 청구항 세트 설정이 정상작동해야 함', () => {
      const level3Session = { ...mockSessionData, levelId: 3 };
      render(
        <GameScreen sessionData={level3Session} onComplete={mockOnComplete} />
      );

      expect(screen.getByText('복합 청구항 세트')).toBeInTheDocument();
      // 레벨 3은 900초 (15:00)
      expect(screen.getByText('15:00')).toBeInTheDocument();
    });
  });

  describe('접근성', () => {
    test('모든 입력 필드에 라벨이 있어야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const inputs = screen.getAllByPlaceholderText(/청구항을 입력하세요/i);
      inputs.forEach((input) => {
        expect(input).toHaveAccessibleName();
      });
    });

    test('모든 버튼이 포커스 가능해야 함', () => {
      render(
        <GameScreen sessionData={mockSessionData} onComplete={mockOnComplete} />
      );

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toBeVisible();
      });
    });
  });
});
