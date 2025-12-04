import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ResultScreen from '../components/ResultScreen';

describe('ResultScreen Component', () => {
  const mockOnRestart = jest.fn();
  const mockOnExit = jest.fn();

  const mockResultData = {
    playerName: '김특허',
    levelId: 1,
    totalScore: 85,
    maxScore: 100,
    claimsSubmitted: 3,
    validClaims: 2,
    feedback: [
      {
        claimNumber: 1,
        message: '명확성: 우수',
        score: 90,
      },
      {
        claimNumber: 2,
        message: '명확성: 보통',
        score: 80,
      },
      {
        claimNumber: 3,
        message: '명확성: 미흡',
        score: 75,
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('기본 렌더링', () => {
    test('결과 화면이 렌더링되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/결과/i)).toBeInTheDocument();
    });

    test('플레이어 이름이 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/김특허/)).toBeInTheDocument();
    });

    test('총점수가 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/85|점수/i)).toBeInTheDocument();
    });

    test('제출한 청구항 수가 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/3/)).toBeInTheDocument();
    });
  });

  describe('점수 표시', () => {
    test('점수 비율이 올바르게 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      const percentage = (mockResultData.totalScore / mockResultData.maxScore) * 100;
      expect(screen.getByText(new RegExp(percentage))).toBeInTheDocument();
    });

    test('만점 달성 시 특별 메시지가 표시되어야 함', () => {
      const perfectResult = {
        ...mockResultData,
        totalScore: 100,
      };

      render(
        <ResultScreen
          resultData={perfectResult}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/만점|완벽/i)).toBeInTheDocument();
    });

    test('점수 레벨별 메시지가 표시되어야 함', () => {
      const lowResult = {
        ...mockResultData,
        totalScore: 40,
      };

      render(
        <ResultScreen
          resultData={lowResult}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/미흡|부족/i)).toBeInTheDocument();
    });
  });

  describe('피드백 표시', () => {
    test('각 청구항별 피드백이 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      mockResultData.feedback.forEach((item) => {
        expect(
          screen.getByText(new RegExp(item.message, 'i'))
        ).toBeInTheDocument();
      });
    });

    test('각 청구항의 점수가 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      mockResultData.feedback.forEach((item) => {
        expect(screen.getByText(new RegExp(item.score))).toBeInTheDocument();
      });
    });

    test('청구항 번호가 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      mockResultData.feedback.forEach((item) => {
        expect(
          screen.getByText(new RegExp(`청구항.*${item.claimNumber}`))
        ).toBeInTheDocument();
      });
    });

    test('피드백이 없을 때 처리되어야 함', () => {
      const noFeedbackResult = {
        ...mockResultData,
        feedback: [],
      };

      render(
        <ResultScreen
          resultData={noFeedbackResult}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.queryByText(/청구항/)).not.toBeInTheDocument();
    });
  });

  describe('통계 정보', () => {
    test('제출 현황이 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      const successRate =
        (mockResultData.validClaims / mockResultData.claimsSubmitted) * 100;
      expect(screen.getByText(new RegExp(successRate))).toBeInTheDocument();
    });

    test('레벨 정보가 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/레벨 1|기본 청구항/i)).toBeInTheDocument();
    });

    test('높은 점수에 대한 격려 메시지가 표시되어야 함', () => {
      const goodResult = {
        ...mockResultData,
        totalScore: 90,
      };

      render(
        <ResultScreen
          resultData={goodResult}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/우수|좋음|훌륭/i)).toBeInTheDocument();
    });
  });

  describe('버튼 기능', () => {
    test('재시작 버튼이 있어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(
        screen.getByRole('button', { name: /재시작|다시/i })
      ).toBeInTheDocument();
    });

    test('종료 버튼이 있어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(
        screen.getByRole('button', { name: /종료|나가기/i })
      ).toBeInTheDocument();
    });

    test('재시작 버튼을 클릭하면 onRestart가 호출되어야 함', async () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      const restartButton = screen.getByRole('button', {
        name: /재시작|다시/i,
      });
      await userEvent.click(restartButton);

      expect(mockOnRestart).toHaveBeenCalled();
    });

    test('종료 버튼을 클릭하면 onExit이 호출되어야 함', async () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      const exitButton = screen.getByRole('button', {
        name: /종료|나가기/i,
      });
      await userEvent.click(exitButton);

      expect(mockOnExit).toHaveBeenCalled();
    });
  });

  describe('시각적 표현', () => {
    test('점수에 따른 등급이 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/B|중상/i)).toBeInTheDocument();
    });

    test('개선 제안이 있어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/개선|피드백|제안/i)).toBeInTheDocument();
    });
  });

  describe('접근성', () => {
    test('모든 버튼이 접근 가능해야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toBeVisible();
        expect(button).toHaveAccessibleName();
      });
    });

    test('점수 정보가 명확하게 표시되어야 함', () => {
      render(
        <ResultScreen
          resultData={mockResultData}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/점수|총점/i)).toBeInTheDocument();
    });
  });

  describe('엣지 케이스', () => {
    test('0점 결과가 처리되어야 함', () => {
      const zeroResult = {
        ...mockResultData,
        totalScore: 0,
      };

      render(
        <ResultScreen
          resultData={zeroResult}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/0|점수/)).toBeInTheDocument();
    });

    test('유효한 청구항이 0개일 때 처리되어야 함', () => {
      const invalidResult = {
        ...mockResultData,
        validClaims: 0,
        claimsSubmitted: 3,
      };

      render(
        <ResultScreen
          resultData={invalidResult}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/0\/3/)).toBeInTheDocument();
    });

    test('매우 많은 피드백이 스크롤 가능해야 함', () => {
      const manyFeedback = {
        ...mockResultData,
        feedback: Array.from({ length: 20 }, (_, i) => ({
          claimNumber: i + 1,
          message: `피드백 ${i + 1}`,
          score: 80 + Math.random() * 20,
        })),
      };

      render(
        <ResultScreen
          resultData={manyFeedback}
          onRestart={mockOnRestart}
          onExit={mockOnExit}
        />
      );

      expect(screen.getByText(/피드백 1/)).toBeInTheDocument();
      expect(screen.getByText(/피드백 20/)).toBeInTheDocument();
    });
  });
});
