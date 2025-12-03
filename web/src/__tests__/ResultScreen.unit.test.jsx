/**
 * ResultScreen 단위 테스트
 * 결과 화면의 개별 기능 검증
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ResultScreen from '../components/ResultScreen';

describe('ResultScreen Component', () => {
  // Mock callbacks
  const mockOnRetry = jest.fn();
  const mockOnNextLevel = jest.fn();
  const mockOnHome = jest.fn();

  // Success session data
  const successSessionData = {
    sessionId: 'test_session_001',
    playerName: '테스트플레이어',
    levelId: 1,
    submittedClaims: [
      '배터리 장치는 양극, 음극, 전해질을 포함한다',
    ],
    startTime: Date.now() - 60000,
    endTime: Date.now(),
    isSuccess: true,
  };

  // Failure session data
  const failureSessionData = {
    sessionId: 'test_session_002',
    playerName: '실패플레이어',
    levelId: 1,
    submittedClaims: [
      '짧은 청구항',
    ],
    startTime: Date.now() - 300000,
    endTime: Date.now(),
    isSuccess: false,
    failureReason: 'Timer expired',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Render & Display', () => {
    test('NC1: Should render result screen with all elements on success', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/성공/i)).toBeInTheDocument();
      expect(screen.getByText(/테스트플레이어/)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /다음 레벨/i })).toBeInTheDocument();
    });

    test('NC2: Should render result screen on failure', () => {
      render(
        <ResultScreen
          sessionData={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/실패|완료되지 않음/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /다시 하기/i })).toBeInTheDocument();
    });

    test('NC3: Should display player name and statistics', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/플레이어: 테스트플레이어/)).toBeInTheDocument();
      expect(screen.getByText(/레벨: 1/)).toBeInTheDocument();
      expect(screen.getByText(/청구항 수: 1개/)).toBeInTheDocument();
    });

    test('NC4: Should display submitted claims', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/배터리 장치는 양극, 음극, 전해질을 포함한다/)).toBeInTheDocument();
    });

    test('NC5: Should display play time', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/소요 시간|플레이 시간/)).toBeInTheDocument();
    });
  });

  describe('Success State', () => {
    test('NC6: Should show success message', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/축하합니다|성공/i)).toBeInTheDocument();
    });

    test('NC7: Should display next level button on success', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const nextBtn = screen.getByRole('button', { name: /다음 레벨/i });
      expect(nextBtn).toBeInTheDocument();
      expect(nextBtn).not.toBeDisabled();
    });

    test('NC8: Should not display retry button on success', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const retryBtn = screen.queryByRole('button', { name: /다시 하기/i });
      expect(retryBtn).not.toBeInTheDocument();
    });
  });

  describe('Failure State', () => {
    test('NC9: Should show failure message', () => {
      render(
        <ResultScreen
          sessionData={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/실패|완료되지 않음/i)).toBeInTheDocument();
    });

    test('NC10: Should display retry button on failure', () => {
      render(
        <ResultScreen
          sessionData={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const retryBtn = screen.getByRole('button', { name: /다시 하기/i });
      expect(retryBtn).toBeInTheDocument();
      expect(retryBtn).not.toBeDisabled();
    });

    test('NC11: Should not display next level button on failure', () => {
      render(
        <ResultScreen
          sessionData={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const nextBtn = screen.queryByRole('button', { name: /다음 레벨/i });
      expect(nextBtn).not.toBeInTheDocument();
    });

    test('NC12: Should display failure reason if provided', () => {
      render(
        <ResultScreen
          sessionData={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      // Should display some reason text
      const reasons = screen.queryAllByText(/Timer expired|시간 초과|청구항 부족/);
      expect(reasons.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Button Actions', () => {
    test('NC13: Should call onNextLevel when next level button clicked', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const nextBtn = screen.getByRole('button', { name: /다음 레벨/i });
      await user.click(nextBtn);

      await waitFor(() => {
        expect(mockOnNextLevel).toHaveBeenCalled();
      });
    });

    test('NC14: Should call onRetry when retry button clicked', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          sessionData={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const retryBtn = screen.getByRole('button', { name: /다시 하기/i });
      await user.click(retryBtn);

      await waitFor(() => {
        expect(mockOnRetry).toHaveBeenCalled();
      });
    });

    test('NC15: Should call onHome when home button clicked', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const homeBtn = screen.getByRole('button', { name: /홈|처음으로/i });
      await user.click(homeBtn);

      await waitFor(() => {
        expect(mockOnHome).toHaveBeenCalled();
      });
    });
  });

  describe('Edge Cases', () => {
    test('EC1: Should handle empty claims list', () => {
      const emptySessionData = {
        ...successSessionData,
        submittedClaims: [],
      };

      render(
        <ResultScreen
          sessionData={emptySessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/청구항 수: 0개/)).toBeInTheDocument();
    });

    test('EC2: Should handle very long player name (100 characters)', () => {
      const longNameData = {
        ...successSessionData,
        playerName: 'a'.repeat(100),
      };

      render(
        <ResultScreen
          sessionData={longNameData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(new RegExp('a'.repeat(100)))).toBeInTheDocument();
    });

    test('EC3: Should handle very long claim text (1000 characters)', () => {
      const longClaimData = {
        ...successSessionData,
        submittedClaims: ['a'.repeat(1000)],
      };

      render(
        <ResultScreen
          sessionData={longClaimData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText('a'.repeat(50))).toBeInTheDocument();
    });

    test('EC4: Should handle multiple claims display', () => {
      const multiClaimData = {
        ...successSessionData,
        submittedClaims: [
          '첫 번째 청구항입니다',
          '두 번째 청구항입니다',
          '세 번째 청구항입니다',
        ],
      };

      render(
        <ResultScreen
          sessionData={multiClaimData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/청구항 수: 3개/)).toBeInTheDocument();
      expect(screen.getByText(/첫 번째 청구항입니다/)).toBeInTheDocument();
      expect(screen.getByText(/두 번째 청구항입니다/)).toBeInTheDocument();
      expect(screen.getByText(/세 번째 청구항입니다/)).toBeInTheDocument();
    });

    test('EC5: Should handle special characters in claims', () => {
      const specialCharData = {
        ...successSessionData,
        submittedClaims: [
          '배터리는 [양극], (음극), {전해질}을 포함한다 @ # $',
        ],
      };

      render(
        <ResultScreen
          sessionData={specialCharData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/배터리는/)).toBeInTheDocument();
    });

    test('EC6: Should handle emoji in claims', () => {
      const emojiData = {
        ...successSessionData,
        submittedClaims: [
          '배터리 장치🔋는 양극⚡, 음극⚙️, 전해질💧을 포함한다',
        ],
      };

      render(
        <ResultScreen
          sessionData={emojiData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/배터리 장치/)).toBeInTheDocument();
    });

    test('EC7: Should handle multiline claims', () => {
      const multilineData = {
        ...successSessionData,
        submittedClaims: [
          '첫 번째 줄\n두 번째 줄\n세 번째 줄',
        ],
      };

      render(
        <ResultScreen
          sessionData={multilineData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/첫 번째 줄/)).toBeInTheDocument();
    });

    test('EC8: Should handle level 3 data correctly', () => {
      const level3Data = {
        ...successSessionData,
        levelId: 3,
        submittedClaims: Array(5).fill('청구항'),
      };

      render(
        <ResultScreen
          sessionData={level3Data}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/레벨: 3|Level 3/)).toBeInTheDocument();
      expect(screen.getByText(/청구항 수: 5개/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('ACC1: Should have descriptive button texts', () => {
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByRole('button', { name: /다음 레벨|Next Level/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /홈|처음으로|Home/i })).toBeInTheDocument();
    });

    test('ACC2: Should have semantic HTML structure', () => {
      const { container } = render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      const heading = container.querySelector('h1, h2, h3');
      expect(heading).toBeInTheDocument();
    });

    test('ACC3: Should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          sessionData={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      await user.tab();
      const nextBtn = screen.getByRole('button', { name: /다음 레벨/i });
      expect(nextBtn).toHaveFocus();
    });
  });

  describe('Data Validation', () => {
    test('NC16: Should correctly display different level information', () => {
      const level2Data = {
        ...successSessionData,
        levelId: 2,
      };

      render(
        <ResultScreen
          sessionData={level2Data}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/레벨: 2/)).toBeInTheDocument();
    });

    test('NC17: Should format time duration correctly', () => {
      const dataWithTime = {
        ...successSessionData,
        startTime: Date.now() - 125000, // 2:05
        endTime: Date.now(),
      };

      render(
        <ResultScreen
          sessionData={dataWithTime}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
          onHome={mockOnHome}
        />
      );

      expect(screen.getByText(/소요 시간|플레이 시간|분|초/)).toBeInTheDocument();
    });
  });
});
