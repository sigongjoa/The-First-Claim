import React from 'react';
import {
  useClaimValidationForGame,
  useGameTimer,
} from '../hooks';
import '../styles/GameScreen.css';

function GameScreen({ sessionData, onComplete }) {
  // 레벨별 설정
  const levelConfigs = {
    1: { title: '기본 청구항 작성', required: 1, timeLimit: 300 },
    2: { title: '종속항 작성', required: 3, timeLimit: 600 },
    3: { title: '복합 청구항 세트', required: 5, timeLimit: 900 },
  };

  const levelId = sessionData.levelId;
  const config = levelConfigs[levelId];

  // 커스텀 훅 사용
  const {
    claims,
    validationResults,
    feedback,
    submitted,
    addClaim,
    updateClaim,
    removeClaim,
    handleSubmit,
  } = useClaimValidationForGame(sessionData.sessionId);

  const {
    timeRemaining,
    isExpired,
    formatTime,
  } = useGameTimer(config.timeLimit * 1000, !submitted, () => {
    handleSubmit(claims, config.required, onComplete);
  });

  if (submitted) {
    return (
      <div className="game-container">
        <div className="result-pending">
          <div className="spinner"></div>
          <h2>평가 중...</h2>
          <p>청구항을 검증하고 있습니다</p>
        </div>
      </div>
    );
  }

  if (isExpired) {
    return (
      <div className="game-container">
        <div className="result-pending">
          <h2>⏰ 시간 초과</h2>
          <p>게임 시간이 다 되었습니다</p>
        </div>
      </div>
    );
  }

  const filledClaims = claims.filter((c) => c.trim()).length;
  const timeWarning = timeRemaining < 60000; // 60초 이하

  return (
    <div className="game-container">
      <div className="game-header">
        <div className="header-info">
          <h1>{config.title}</h1>
          <p className="player-name">플레이어: {sessionData.playerName}</p>
        </div>
        <div className={`timer ${timeWarning ? 'warning' : ''}`}>
          ⏱️ {formatTime(Math.floor(timeRemaining / 1000))}
        </div>
      </div>

      <div className="game-content">
        <div className="instructions">
          <div className="requirement">
            필요한 청구항: <strong>{config.required}개</strong> |
            작성 중: <strong>{filledClaims}개</strong>
          </div>
          <div className="tips">
            💡 팁: 각 청구항은 기술적 특징을 명확하게 포함해야 하며 최소 20자 이상이어야 합니다
          </div>
        </div>

        <div className="claims-section">
          {claims.map((claim, index) => (
            <div key={index} className="claim-input-wrapper">
              <div className="claim-header">
                <label>청구항 {index + 1}</label>
                <span className="claim-type">
                  {index === 0 ? '독립항' : '종속항'}
                </span>
              </div>

              <textarea
                value={claim}
                onChange={(e) => updateClaim(index, e.target.value)}
                placeholder={
                  index === 0
                    ? '기본 청구항을 작성하세요 (예: 배터리 장치는 양극, 음극, 전해질을 포함한다)'
                    : '종속항을 작성하세요 (예: 제1항의 배터리에서 양극은 리튬을 포함한다)'
                }
                className={`claim-textarea ${
                  validationResults[index]
                    ? validationResults[index].valid
                      ? 'valid'
                      : 'invalid'
                    : ''
                }`}
              />

              {validationResults[index] && (
                <div
                  className={`validation-feedback ${
                    validationResults[index].valid ? 'valid' : 'invalid'
                  }`}
                >
                  {validationResults[index].message}
                </div>
              )}

              <div className="claim-actions">
                <span className="char-count">
                  {claim.length} / 20자
                  {claim.length >= 20 && '✅'}
                </span>
                {claims.length > 1 && (
                  <button
                    className="delete-btn"
                    onClick={() => removeClaim(index)}
                  >
                    삭제
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {filledClaims < config.required && (
          <button className="add-claim-btn" onClick={addClaim}>
            + 청구항 추가
          </button>
        )}

        {feedback.length > 0 && (
          <div className="feedback-section">
            {feedback.map((msg, idx) => (
              <p key={idx} className="feedback-message">
                {msg}
              </p>
            ))}
          </div>
        )}
      </div>

      <div className="game-footer">
        <button
          className="submit-btn"
          onClick={() => handleSubmit(claims, config.required, onComplete)}
          disabled={filledClaims === 0}
        >
          제출
        </button>
      </div>
    </div>
  );
}

export default GameScreen;
