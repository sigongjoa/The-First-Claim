import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import WelcomeScreen from '../components/WelcomeScreen';

describe('WelcomeScreen Component', () => {
  const mockOnStart = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('기본 렌더링', () => {
    test('환영 메시지가 표시되어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(
        screen.getByText(/특허 청구항 작성 게임/i)
      ).toBeInTheDocument();
    });

    test('플레이어 이름 입력 필드가 있어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(screen.getByPlaceholderText(/이름을 입력하세요/i)).toBeInTheDocument();
    });

    test('시작 버튼이 표시되어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(screen.getByRole('button', { name: /시작/i })).toBeInTheDocument();
    });

    test('레벨 선택 옵션이 있어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(screen.getByText(/레벨 1/i)).toBeInTheDocument();
      expect(screen.getByText(/레벨 2/i)).toBeInTheDocument();
      expect(screen.getByText(/레벨 3/i)).toBeInTheDocument();
    });
  });

  describe('플레이어 이름 입력', () => {
    test('플레이어 이름을 입력할 수 있어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '김특허');

      expect(nameInput.value).toBe('김특허');
    });

    test('빈 이름으로는 시작할 수 없어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const startButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(startButton);

      expect(mockOnStart).not.toHaveBeenCalled();
    });

    test('한글 이름이 정상 입력되어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '이순신');

      expect(nameInput.value).toBe('이순신');
    });

    test('영문 이름도 입력 가능해야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, 'John Doe');

      expect(nameInput.value).toBe('John Doe');
    });
  });

  describe('레벨 선택', () => {
    test('기본 선택 레벨은 1이어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const level1Radio = screen.getByRole('radio', { name: /기본/i });
      expect(level1Radio).toBeChecked();
    });

    test('레벨을 변경할 수 있어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const level2Radio = screen.getByRole('radio', { name: /종속항/i });
      await userEvent.click(level2Radio);

      expect(level2Radio).toBeChecked();
    });

    test('각 레벨의 설명이 표시되어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(screen.getByText(/기본 청구항 작성/i)).toBeInTheDocument();
      expect(screen.getByText(/종속항 작성/i)).toBeInTheDocument();
      expect(screen.getByText(/복합 청구항/i)).toBeInTheDocument();
    });
  });

  describe('게임 시작', () => {
    test('유효한 이름과 레벨로 시작할 수 있어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '김특허');

      const startButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(startButton);

      expect(mockOnStart).toHaveBeenCalledWith(
        expect.objectContaining({
          playerName: '김특허',
          levelId: 1,
        })
      );
    });

    test('선택한 레벨이 전달되어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '김특허');

      const level3Radio = screen.getByRole('radio', { name: /복합/i });
      await userEvent.click(level3Radio);

      const startButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(startButton);

      expect(mockOnStart).toHaveBeenCalledWith(
        expect.objectContaining({
          playerName: '김특허',
          levelId: 3,
        })
      );
    });

    test('시작 시 세션 ID가 생성되어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '김특허');

      const startButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(startButton);

      expect(mockOnStart).toHaveBeenCalledWith(
        expect.objectContaining({
          sessionId: expect.any(String),
        })
      );
    });

    test('세션 ID가 고유해야 함', async () => {
      const { rerender } = render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '김특허');

      const startButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(startButton);

      const firstCallSessionId = mockOnStart.mock.calls[0][0].sessionId;

      mockOnStart.mockClear();

      rerender(<WelcomeScreen onStart={mockOnStart} />);

      const newNameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(newNameInput, '이순신');

      const newStartButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(newStartButton);

      const secondCallSessionId = mockOnStart.mock.calls[0][0].sessionId;

      expect(firstCallSessionId).not.toBe(secondCallSessionId);
    });
  });

  describe('규칙 설명', () => {
    test('게임 규칙이 표시되어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(screen.getByText(/규칙/i)).toBeInTheDocument();
    });

    test('각 레벨별 시간 제한이 설명되어야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      expect(screen.getByText(/5분|300초/i)).toBeInTheDocument();
      expect(screen.getByText(/10분|600초/i)).toBeInTheDocument();
      expect(screen.getByText(/15분|900초/i)).toBeInTheDocument();
    });
  });

  describe('접근성', () => {
    test('모든 입력 필드가 접근 가능해야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      expect(nameInput).toBeVisible();
      expect(nameInput).not.toBeDisabled();
    });

    test('모든 라디오 버튼이 접근 가능해야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const radioButtons = screen.getAllByRole('radio');
      radioButtons.forEach((radio) => {
        expect(radio).toBeVisible();
        expect(radio).not.toBeDisabled();
      });
    });

    test('시작 버튼이 명확한 텍스트를 가져야 함', () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const startButton = screen.getByRole('button', { name: /시작/i });
      expect(startButton).toHaveAccessibleName();
    });
  });

  describe('엣지 케이스', () => {
    test('매우 긴 이름이 입력 가능해야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const longName = '김'.repeat(50);
      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, longName);

      expect(nameInput.value.length).toBeGreaterThan(0);
    });

    test('공백만 입력되면 시작할 수 없어야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, '   ');

      const startButton = screen.getByRole('button', { name: /시작/i });
      await userEvent.click(startButton);

      expect(mockOnStart).not.toHaveBeenCalled();
    });

    test('특수 문자가 포함된 이름이 입력 가능해야 함', async () => {
      render(<WelcomeScreen onStart={mockOnStart} />);

      const nameInput = screen.getByPlaceholderText(/이름을 입력하세요/i);
      await userEvent.type(nameInput, 'Mr. Kim-特');

      expect(nameInput.value).toContain('Mr. Kim');
    });
  });
});
