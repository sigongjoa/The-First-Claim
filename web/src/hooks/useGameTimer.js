/**
 * useGameTimer Hook - 게임 타이머 관리 로직
 *
 * 게임의 시간 제한, 카운트다운을 관리합니다.
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * 게임 타이머를 관리하는 커스텀 훅
 *
 * @param {number} duration - 초 단위 게임 시간
 * @param {boolean} isRunning - 타이머 실행 여부
 * @param {Function} onExpire - 시간 만료 콜백
 * @returns {Object} 타이머 상태 및 메서드
 */
export function useGameTimer(duration, isRunning = true, onExpire = null) {
  const [timeRemaining, setTimeRemaining] = useState(duration);
  const [isExpired, setIsExpired] = useState(false);
  const [pausedTime, setPausedTime] = useState(null);

  // 타이머 효과
  useEffect(() => {
    // 만료된 경우 타이머 중단
    if (isExpired) return;

    // 실행 중이지 않으면 중단
    if (!isRunning) return;

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        const newTime = prev - 1;

        // 시간 만료
        if (newTime <= 0) {
          setIsExpired(true);
          clearInterval(interval);

          if (onExpire) {
            onExpire();
          }

          return 0;
        }

        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, isExpired, onExpire]);

  /**
   * 타이머 일시정지
   */
  const pause = useCallback(() => {
    setPausedTime(timeRemaining);
  }, [timeRemaining]);

  /**
   * 타이머 재개
   */
  const resume = useCallback(() => {
    setPausedTime(null);
  }, []);

  /**
   * 타이머 리셋
   */
  const reset = useCallback((newDuration = duration) => {
    setTimeRemaining(newDuration);
    setIsExpired(false);
    setPausedTime(null);
  }, [duration]);

  /**
   * 타이머 추가 시간
   *
   * @param {number} seconds - 추가할 초
   */
  const addTime = useCallback((seconds) => {
    setTimeRemaining((prev) => Math.min(prev + seconds, duration));
  }, [duration]);

  /**
   * 시간을 사람이 읽을 수 있는 형식으로 변환
   *
   * @param {number} seconds - 초 단위 시간
   * @returns {string} "MM:SS" 형식의 시간 문자열
   */
  const formatTime = useCallback((seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  /**
   * 남은 시간의 비율 계산 (0.0 ~ 1.0)
   *
   * @returns {number} 남은 시간의 비율
   */
  const getProgress = useCallback(() => {
    return timeRemaining / duration;
  }, [timeRemaining, duration]);

  /**
   * 시간이 부족한지 확인 (10% 미만)
   *
   * @returns {boolean}
   */
  const isTimeRunningLow = useCallback(() => {
    return getProgress() < 0.1;
  }, [getProgress]);

  /**
   * 시간이 위험한지 확인 (5% 미만)
   *
   * @returns {boolean}
   */
  const isTimeCritical = useCallback(() => {
    return getProgress() < 0.05;
  }, [getProgress]);

  return {
    timeRemaining: pausedTime !== null ? pausedTime : timeRemaining,
    isExpired,
    isPaused: pausedTime !== null,
    pause,
    resume,
    reset,
    addTime,
    formatTime,
    getProgress,
    isTimeRunningLow,
    isTimeCritical,
  };
}

/**
 * 시간 경과를 백분율로 표현하는 훅
 *
 * @param {number} startTime - 시작 시간 (Unix timestamp ms)
 * @param {number} duration - 총 시간 (ms)
 * @returns {Object} 경과 시간 정보
 */
export function useElapsedTime(startTime, duration) {
  const [elapsed, setElapsed] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!startTime) return;

    const timer = setInterval(() => {
      const now = Date.now();
      const newElapsed = now - startTime;
      const newProgress = Math.min(newElapsed / duration, 1.0);

      setElapsed(newElapsed);
      setProgress(newProgress);
    }, 100);

    return () => clearInterval(timer);
  }, [startTime, duration]);

  return {
    elapsed,
    progress,
    isComplete: progress >= 1.0,
  };
}

/**
 * 스톱워치 기능 (시간 카운트업)
 *
 * @param {boolean} isRunning - 스톱워치 실행 여부
 * @returns {Object} 스톱워치 상태 및 메서드
 */
export function useStopwatch(isRunning = true) {
  const [elapsed, setElapsed] = useState(0);
  const [isActive, setIsActive] = useState(isRunning);

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isActive]);

  const start = useCallback(() => {
    setIsActive(true);
  }, []);

  const stop = useCallback(() => {
    setIsActive(false);
  }, []);

  const reset = useCallback(() => {
    setElapsed(0);
    setIsActive(false);
  }, []);

  const formatTime = useCallback((seconds) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, '0')}:${secs
        .toString()
        .padStart(2, '0')}`;
    }

    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  return {
    elapsed,
    isActive,
    start,
    stop,
    reset,
    formatTime,
    getFormattedTime: () => formatTime(elapsed),
  };
}
