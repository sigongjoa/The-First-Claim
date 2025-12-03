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

  // Success result data (actual component prop format)
  const successSessionData = {
    success: true,
    playerName: '테스트플레이어',
    levelId: 1,
    claims: [
      '배터리 장치는 양극, 음극, 전해질을 포함한다',
    ],
  };

  // Failure result data (actual component prop format)
  const failureSessionData = {
    success: false,
    playerName: '실패플레이어',
    levelId: 1,
    claims: [
      '짧은 청구항',
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Render & Display', () => {
    test('NC1: Should render result screen with all elements on success', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/축하합니다/i)).toBeInTheDocument();
      expect(screen.getByText(/테스트플레이어/)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /다음 레벨/i })).toBeInTheDocument();
    });

    test('NC2: Should render result screen on failure', () => {
      render(
        <ResultScreen
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      expect(screen.getByText(/아직 요구사항을 충족하지 못했습니다/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /다시 하기/i })).toBeInTheDocument();
    });

    test('NC3: Should display player name and statistics', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/플레이어/)).toBeInTheDocument();
      expect(screen.getByText(/테스트플레이어/)).toBeInTheDocument();
      expect(screen.getByText(/완료한 레벨/)).toBeInTheDocument();
      expect(screen.getByText(/Level 1/)).toBeInTheDocument();
    });

    test('NC4: Should display submitted claims', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/배터리 장치는 양극, 음극, 전해질을 포함한다/)).toBeInTheDocument();
    });

    test('NC5: Should display claims count', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/작성한 청구항/)).toBeInTheDocument();
    });
  });

  describe('Success State', () => {
    test('NC6: Should show success message', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/축하합니다/i)).toBeInTheDocument();
    });

    test('NC7: Should display next level button on success', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      const nextBtn = screen.getByRole('button', { name: /다음 레벨/i });
      expect(nextBtn).toBeInTheDocument();
      expect(nextBtn).not.toBeDisabled();
    });

    test('NC8: Should display retry button on success', () => {
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      // Actual implementation shows "다시 하기" button in success state
      const retryBtn = screen.getByRole('button', { name: /다시 하기/i });
      expect(retryBtn).toBeInTheDocument();
    });
  });

  describe('Failure State', () => {
    test('NC9: Should show failure message', () => {
      render(
        <ResultScreen
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      expect(screen.getByText(/아직 요구사항을 충족하지 못했습니다/i)).toBeInTheDocument();
    });

    test('NC10: Should display retry button on failure', () => {
      render(
        <ResultScreen
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      const retryBtn = screen.getByRole('button', { name: /다시 하기/i });
      expect(retryBtn).toBeInTheDocument();
      expect(retryBtn).not.toBeDisabled();
    });

    test('NC11: Should not display next level button on failure', () => {
      render(
        <ResultScreen
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      const nextBtn = screen.queryByRole('button', { name: /다음 레벨/i });
      expect(nextBtn).not.toBeInTheDocument();
    });

    test('NC12: Should display failure tips', () => {
      render(
        <ResultScreen
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      // Should display improvement tips
      expect(screen.getByText(/개선 팁/i)).toBeInTheDocument();
      expect(screen.getByText(/기술적 특징/i)).toBeInTheDocument();
    });
  });

  describe('Button Actions', () => {
    test('NC13: Should call onNextLevel when next level button clicked', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
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
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      const retryBtn = screen.getByRole('button', { name: /다시 하기/i });
      await user.click(retryBtn);

      await waitFor(() => {
        expect(mockOnRetry).toHaveBeenCalled();
      });
    });

    test('NC15: Should display main menu button on failure', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          result={failureSessionData}
          onRetry={mockOnRetry}
          onNextLevel={null}
        />
      );

      const menuBtn = screen.getByRole('button', { name: /메인 메뉴/i });
      expect(menuBtn).toBeInTheDocument();
      await user.click(menuBtn);

      await waitFor(() => {
        expect(mockOnRetry).toHaveBeenCalled();
      });
    });
  });

  describe('Edge Cases', () => {
    test('EC1: Should handle empty claims list', () => {
      const emptySessionData = {
        ...successSessionData,
        claims: [],
      };

      render(
        <ResultScreen
          result={emptySessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/작성한 청구항/)).toBeInTheDocument();
    });

    test('EC2: Should handle very long player name (100 characters)', () => {
      const longNameData = {
        ...successSessionData,
        playerName: 'a'.repeat(100),
      };

      render(
        <ResultScreen
          result={longNameData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(new RegExp('a'.repeat(100)))).toBeInTheDocument();
    });

    test('EC3: Should handle very long claim text (1000 characters)', () => {
      const longClaimData = {
        ...successSessionData,
        claims: ['a'.repeat(1000)],
      };

      render(
        <ResultScreen
          result={longClaimData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText('a'.repeat(50))).toBeInTheDocument();
    });

    test('EC4: Should handle multiple claims display', () => {
      const multiClaimData = {
        ...successSessionData,
        claims: [
          '첫 번째 청구항입니다',
          '두 번째 청구항입니다',
          '세 번째 청구항입니다',
        ],
      };

      render(
        <ResultScreen
          result={multiClaimData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
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
        claims: [
          '배터리는 [양극], (음극), {전해질}을 포함한다 @ # $',
        ],
      };

      render(
        <ResultScreen
          result={specialCharData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/배터리는/)).toBeInTheDocument();
    });

    test('EC6: Should handle emoji in claims', () => {
      const emojiData = {
        ...successSessionData,
        claims: [
          '배터리 장치🔋는 양극⚡, 음극⚙️, 전해질💧을 포함한다',
        ],
      };

      render(
        <ResultScreen
          result={emojiData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/배터리 장치/)).toBeInTheDocument();
    });

    test('EC7: Should handle multiline claims', () => {
      const multilineData = {
        ...successSessionData,
        claims: [
          '첫 번째 줄\n두 번째 줄\n세 번째 줄',
        ],
      };

      render(
        <ResultScreen
          result={multilineData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
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
          result={level3Data}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
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
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByRole('button', { name: /다음 레벨|Next Level/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /홈|처음으로|Home/i })).toBeInTheDocument();
    });

    test('ACC2: Should have semantic HTML structure', () => {
      const { container } = render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      const heading = container.querySelector('h1, h2, h3');
      expect(heading).toBeInTheDocument();
    });

    test('ACC3: Should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(
        <ResultScreen
          result={successSessionData}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
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
          result={level2Data}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
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
          result={dataWithTime}
          onRetry={mockOnRetry}
          onNextLevel={mockOnNextLevel}
        />
      );

      expect(screen.getByText(/소요 시간|플레이 시간|분|초/)).toBeInTheDocument();
    });
  });
});
