/**
 * useClaimValidationForGame Hook - 게임 화면용 청구항 검증 로직
 *
 * 청구항 관리, 검증, 제출 기능을 제공합니다.
 */

import { useState, useCallback } from 'react';
import { API_BASE_URL } from '../config/api.config';

/**
 * 게임 화면에서 청구항 관리 및 검증
 *
 * @param {string} sessionId - 게임 세션 ID
 * @returns {Object} 청구항 관리 상태 및 메서드
 */
export function useClaimValidationForGame(sessionId) {
  const [claims, setClaims] = useState(['']);
  const [validationResults, setValidationResults] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * 청구항 추가
   */
  const addClaim = useCallback(() => {
    setClaims([...claims, '']);
  }, [claims]);

  /**
   * 청구항 수정
   */
  const updateClaim = useCallback((index, value) => {
    const newClaims = [...claims];
    newClaims[index] = value;
    setClaims(newClaims);
  }, [claims]);

  /**
   * 청구항 삭제
   */
  const removeClaim = useCallback((index) => {
    if (claims.length > 1) {
      setClaims(claims.filter((_, i) => i !== index));
    }
  }, [claims]);

  /**
   * 개별 청구항 검증 (클라이언트 측)
   */
  const validateSingleClaim = useCallback((claimText) => {
    if (!claimText.trim()) {
      return {
        valid: false,
        message: '청구항 내용이 비어있습니다',
      };
    }

    if (claimText.length < 20) {
      return {
        valid: false,
        message: `청구항이 너무 짧습니다 (현재: ${claimText.length}자, 최소: 20자)`,
      };
    }

    if (claimText.length > 1000) {
      return {
        valid: false,
        message: `청구항이 너무 깁니다 (현재: ${claimText.length}자, 최대: 1000자)`,
      };
    }

    // 기술용어 확인
    const techKeywords = [
      '장치',
      '부',
      '기',
      '시스템',
      '방법',
      '수단',
      '구성',
      '포함',
      '특징',
    ];
    const hasTechTerms = techKeywords.some((keyword) =>
      claimText.includes(keyword)
    );

    if (!hasTechTerms) {
      return {
        valid: true,
        message: '✅ 올바른 형식입니다 (⚠️ 기술용어 권장)',
        warning: true,
      };
    }

    return {
      valid: true,
      message: '✅ 올바른 형식입니다',
    };
  }, []);

  /**
   * 모든 청구항 검증
   */
  const validateAllClaims = useCallback(() => {
    const results = claims.map((claim, index) => ({
      index,
      ...validateSingleClaim(claim),
    }));

    const hasErrors = results.some((r) => !r.valid);
    setValidationResults(results);

    return { results, hasErrors };
  }, [claims, validateSingleClaim]);

  /**
   * 청구항 제출 및 평가
   */
  const handleSubmit = useCallback(
    async (claimsToSubmit, requiredCount, onComplete) => {
      try {
        setIsLoading(true);
        const { results, hasErrors } = validateAllClaims();

        setValidationResults(results);

        const validClaims = claimsToSubmit.filter(
          (c) => c.trim().length >= 20
        );
        const success = validClaims.length >= requiredCount && !hasErrors;

        if (success) {
          setFeedback(['✅ 모든 청구항이 요구사항을 충족했습니다!']);
        } else {
          const feedbackMessages = [
            `📊 제출된 청구항: ${validClaims.length}개 / ${requiredCount}개 필요`,
          ];

          if (hasErrors) {
            feedbackMessages.push('⚠️ 일부 청구항이 검증 오류가 있습니다');
          }

          setFeedback(feedbackMessages);
        }

        setSubmitted(true);

        // 서버에 제출
        if (sessionId && validClaims.length > 0) {
          for (const claim of validClaims) {
            try {
              await fetch(
                `${API_BASE_URL}/api/game/session/${sessionId}/submit`,
                {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    claim: claim,
                  }),
                }
              );
            } catch (error) {
              console.error('청구항 제출 오류:', error);
            }
          }
        }

        // 완료 콜백 (2초 후)
        setTimeout(() => {
          if (onComplete) {
            onComplete(claimsToSubmit, success);
          }
        }, 2000);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, validateAllClaims]
  );

  return {
    claims,
    validationResults,
    feedback,
    submitted,
    isLoading,
    addClaim,
    updateClaim,
    removeClaim,
    validateSingleClaim,
    validateAllClaims,
    handleSubmit,
  };
}
