import React, { useState, useEffect } from 'react';
import '../styles/GameScreen.css';

function GameScreen({ sessionData, onComplete }) {
  const [claims, setClaims] = useState(['']);
  const [currentInput, setCurrentInput] = useState('');
  const [timeLeft, setTimeLeft] = useState(300);
  const [submitted, setSubmitted] = useState(false);
  const [feedback, setFeedback] = useState([]);
  const [validationResults, setValidationResults] = useState([]);

  // 레벨별 설정
  const levelConfigs = {
    1: { title: '기본 청구항 작성', required: 1, timeLimit: 300 },
    2: { title: '종속항 작성', required: 3, timeLimit: 600 },
    3: { title: '복합 청구항 세트', required: 5, timeLimit: 900 },
  };

  const levelId = sessionData.levelId;
  const config = levelConfigs[levelId];

  useEffect(() => {
    setTimeLeft(config.timeLimit);
  }, [levelId]);

  // 타이머
  useEffect(() => {
    if (submitted) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [submitted]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const addClaim = () => {
    setClaims([...claims, '']);
    setCurrentInput('');
  };

  const updateClaim = (index, value) => {
    const newClaims = [...claims];
    newClaims[index] = value;
    setClaims(newClaims);
  };

  const removeClaim = (index) => {
    if (claims.length > 1) {
      setClaims(claims.filter((_, i) => i !== index));
    }
  };

  const validateClaims = () => {
    const results = [];
    let hasErrors = false;

    claims.forEach((claim, index) => {
      if (!claim.trim()) {
        results.push({
          index,
          valid: false,
          message: '청구항 내용이 비어있습니다',
        });
        hasErrors = true;
      } else if (claim.length < 20) {
        results.push({
          index,
          valid: false,
          message: '청구항이 너무 짧습니다 (최소 20자)',
        });
        hasErrors = true;
      } else {
        results.push({
          index,
          valid: true,
          message: '✅ 올바른 형식입니다',
        });
      }
    });

    return { results, hasErrors };
  };

  const handleSubmit = () => {
    const { results, hasErrors } = validateClaims();
    setValidationResults(results);

    const validClaims = claims.filter((c) => c.trim().length >= 20);
    const success = validClaims.length >= config.required && !hasErrors;

    if (success) {
      setFeedback(['✅ 모든 청구항이 요구사항을 충족했습니다!']);
    } else {
      const feedbackMessages = [
        `📊 제출된 청구항: ${validClaims.length}개 / ${config.required}개 필요`,
      ];

      if (hasErrors) {
        feedbackMessages.push('⚠️ 일부 청구항이 검증 오류가 있습니다');
      }

      setFeedback(feedbackMessages);
    }

    setSubmitted(true);
    setTimeout(() => {
      onComplete(claims, success);
    }, 2000);
  };

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

  const filledClaims = claims.filter((c) => c.trim()).length;

  return (
    <div className="game-container">
      <div className="game-header">
        <div className="header-info">
          <h1>{config.title}</h1>
          <p className="player-name">플레이어: {sessionData.playerName}</p>
        </div>
        <div className={`timer ${timeLeft < 60 ? 'warning' : ''}`}>
          ⏱️ {formatTime(timeLeft)}
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
          onClick={handleSubmit}
          disabled={filledClaims === 0}
        >
          제출
        </button>
      </div>
    </div>
  );
}

export default GameScreen;
