/**
 * useClaimValidation Hook - 청구항 검증 및 제출 로직
 *
 * 청구항의 검증, 평가 제출을 담당합니다.
 */

import { useState, useCallback } from 'react';
import { API_BASE_URL } from '../config/api.config';

/**
 * 청구항 검증 및 제출을 관리하는 커스텀 훅
 *
 * @param {string} sessionId - 게임 세션 ID
 * @returns {Object} 검증/제출 상태 및 메서드
 */
export function useClaimValidation(sessionId) {
  const [validating, setValidating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  /**
   * 청구항 제출 및 평가
   *
   * @param {string} claimText - 청구항 텍스트
   * @returns {Promise<Object>} 평가 결과
   */
  const submitClaim = useCallback(
    async (claimText) => {
      if (!sessionId) {
        throw new Error('세션 ID가 없습니다');
      }

      if (!claimText || claimText.trim().length === 0) {
        throw new Error('청구항 텍스트가 비어있습니다');
      }

      try {
        setSubmitting(true);
        setError(null);

        const response = await fetch(
          `${API_BASE_URL}/api/game/session/${sessionId}/submit`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              claim: claimText,
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData.detail || `청구항 제출 실패: ${response.statusText}`
          );
        }

        const data = await response.json();
        setResult(data);
        return data;
      } catch (err) {
        console.error('청구항 제출 오류:', err);
        setError(err.message);
        throw err;
      } finally {
        setSubmitting(false);
      }
    },
    [sessionId]
  );

  /**
   * 청구항 기본 검증 (클라이언트 측)
   *
   * @param {string} claimText - 청구항 텍스트
   * @returns {Object} 검증 결과
   */
  const validateClaim = useCallback((claimText) => {
    const errors = [];
    const warnings = [];

    // 필수 검증
    if (!claimText || claimText.trim().length === 0) {
      errors.push('청구항이 비어있습니다');
      return { valid: false, errors, warnings };
    }

    // 길이 검증
    const trimmed = claimText.trim();
    if (trimmed.length < 20) {
      errors.push(`청구항이 너무 짧습니다 (현재: ${trimmed.length}자, 최소: 20자)`);
    }

    if (trimmed.length > 1000) {
      errors.push(`청구항이 너무 깁니다 (현재: ${trimmed.length}자, 최대: 1000자)`);
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
      trimmed.includes(keyword)
    );

    if (!hasTechTerms) {
      warnings.push(
        '기술 용어가 부족할 수 있습니다 (장치, 구성, 특징 등 포함 권장)'
      );
    }

    // "청구항" 형식 확인
    if (!trimmed.startsWith('청구항')) {
      warnings.push('청구항 형식이 표준 형식과 다릅니다');
    }

    const valid = errors.length === 0;
    return { valid, errors, warnings };
  }, []);

  /**
   * 여러 청구항 일괄 검증
   *
   * @param {string[]} claims - 청구항 텍스트 배열
   * @returns {Object[]} 각 청구항의 검증 결과
   */
  const validateClaims = useCallback((claims) => {
    return claims.map((claim, index) => ({
      index,
      ...validateClaim(claim),
    }));
  }, [validateClaim]);

  /**
   * 청구항 평가 (서버)
   *
   * @param {string} claimText - 청구항 텍스트
   * @returns {Promise<Object>} 평가 결과
   */
  const evaluateClaim = useCallback(
    async (claimText) => {
      // 먼저 클라이언트 측 검증
      const clientValidation = validateClaim(claimText);
      if (!clientValidation.valid) {
        throw new Error(clientValidation.errors.join(', '));
      }

      try {
        setValidating(true);
        setError(null);

        // 서버에 평가 요청
        return await submitClaim(claimText);
      } finally {
        setValidating(false);
      }
    },
    [submitClaim, validateClaim]
  );

  return {
    submitClaim,
    evaluateClaim,
    validateClaim,
    validateClaims,
    validating,
    submitting,
    result,
    error,
    isLoading: validating || submitting,
  };
}

/**
 * 청구항 검증 결과를 사용자 친화적으로 포맷하는 유틸리티
 *
 * @param {Object} validationResult - 검증 결과
 * @returns {string} 포맷된 피드백 텍스트
 */
export function formatValidationResult(validationResult) {
  const { valid, errors, warnings } = validationResult;

  if (valid && warnings.length === 0) {
    return '✅ 청구항이 유효합니다';
  }

  let message = '';

  if (errors.length > 0) {
    message += `❌ ${errors.join(', ')}`;
  }

  if (warnings.length > 0) {
    if (message) message += '\n';
    message += `⚠️ ${warnings.join(', ')}`;
  }

  return message;
}
