/**
 * useGameSession Hook - 게임 세션 관리 로직
 *
 * 게임 세션의 생성, 로드, 상태 관리를 담당합니다.
 */

import { useState, useCallback, useEffect } from 'react';
import { API_BASE_URL } from '../config/api.config';

/**
 * 게임 세션을 관리하는 커스텀 훅
 *
 * @param {string} sessionId - 게임 세션 ID
 * @returns {Object} 게임 세션 상태 및 메서드
 */
export function useGameSession(sessionId) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 세션 로드
  useEffect(() => {
    async function loadSession() {
      if (!sessionId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/game/session/${sessionId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`세션 로드 실패: ${response.statusText}`);
        }

        const data = await response.json();
        setSession(data);
        setError(null);
      } catch (err) {
        console.error('세션 로드 오류:', err);
        setError(err.message);
        setSession(null);
      } finally {
        setLoading(false);
      }
    }

    loadSession();
  }, [sessionId]);

  /**
   * 세션 상태 업데이트
   *
   * @param {Object} updates - 업데이트할 필드
   * @returns {Promise<void>}
   */
  const updateSession = useCallback(
    async (updates) => {
      if (!sessionId) return;

      try {
        const response = await fetch(`${API_BASE_URL}/api/game/session/${sessionId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updates),
        });

        if (!response.ok) {
          throw new Error('세션 업데이트 실패');
        }

        const updatedData = await response.json();
        setSession(updatedData);
        return updatedData;
      } catch (err) {
        console.error('세션 업데이트 오류:', err);
        setError(err.message);
        throw err;
      }
    },
    [sessionId]
  );

  /**
   * 세션 제거/종료
   *
   * @returns {Promise<void>}
   */
  const deleteSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/game/session/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('세션 삭제 실패');
      }

      setSession(null);
    } catch (err) {
      console.error('세션 삭제 오류:', err);
      setError(err.message);
      throw err;
    }
  }, [sessionId]);

  /**
   * 세션 새로고침
   *
   * @returns {Promise<void>}
   */
  const refreshSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/game/session/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('세션 새로고침 실패');
      }

      const data = await response.json();
      setSession(data);
      setError(null);
    } catch (err) {
      console.error('세션 새로고침 오류:', err);
      setError(err.message);
    }
  }, [sessionId]);

  return {
    session,
    loading,
    error,
    updateSession,
    deleteSession,
    refreshSession,
  };
}

/**
 * 새 게임 세션 생성 훅
 *
 * @returns {Object} 세션 생성 함수 및 상태
 */
export function useCreateGameSession() {
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  /**
   * 새 게임 세션 생성
   *
   * @param {string} playerName - 플레이어 이름
   * @param {number} levelId - 레벨 ID
   * @returns {Promise<Object>} 생성된 세션 데이터
   */
  const createSession = useCallback(async (playerName, levelId) => {
    try {
      setCreating(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/game/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_name: playerName,
          level_id: levelId,
        }),
      });

      if (!response.ok) {
        throw new Error(`세션 생성 실패: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('세션 생성 오류:', err);
      setError(err.message);
      throw err;
    } finally {
      setCreating(false);
    }
  }, []);

  return { createSession, creating, error };
}
