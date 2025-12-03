import React from 'react';
import '../styles/ResultScreen.css';

function ResultScreen({ result, onRetry, onNextLevel }) {
  return (
    <div className="result-container">
      <div className="result-card">
        {result.success ? (
          <div className="success-result">
            <div className="success-icon">🎉</div>
            <h1>축하합니다!</h1>
            <p className="result-message">레벨을 성공적으로 통과했습니다</p>

            <div className="stats-section">
              <div className="stat">
                <span className="label">플레이어</span>
                <span className="value">{result.playerName}</span>
              </div>
              <div className="stat">
                <span className="label">완료한 레벨</span>
                <span className="value">Level {result.levelId}</span>
              </div>
              <div className="stat">
                <span className="label">작성한 청구항</span>
                <span className="value">{result.claims.filter((c) => c.trim()).length}개</span>
              </div>
            </div>

            <div className="claims-review">
              <h3>작성한 청구항</h3>
              {result.claims.map(
                (claim, idx) =>
                  claim.trim() && (
                    <div key={idx} className="claim-item">
                      <div className="claim-number">청구항 {idx + 1}</div>
                      <p className="claim-content">{claim}</p>
                    </div>
                  )
              )}
            </div>
          </div>
        ) : (
          <div className="failure-result">
            <div className="failure-icon">❌</div>
            <h1>아직 요구사항을 충족하지 못했습니다</h1>
            <p className="result-message">다시 시도해주세요</p>

            <div className="stats-section">
              <div className="stat">
                <span className="label">플레이어</span>
                <span className="value">{result.playerName}</span>
              </div>
              <div className="stat">
                <span className="label">레벨</span>
                <span className="value">Level {result.levelId}</span>
              </div>
              <div className="stat">
                <span className="label">작성한 청구항</span>
                <span className="value">{result.claims.filter((c) => c.trim()).length}개</span>
              </div>
            </div>

            <div className="feedback-tips">
              <h4>💡 개선 팁</h4>
              <ul>
                <li>각 청구항은 기술적 특징을 명확하게 포함해야 합니다</li>
                <li>최소 20자 이상 작성해주세요</li>
                <li>독립항과 종속항의 관계를 명확하게 표현하세요</li>
                <li>모호한 표현을 피하세요 (예: 등, 같은, 대략 등)</li>
              </ul>
            </div>
          </div>
        )}

        <div className="action-buttons">
          {onNextLevel ? (
            <>
              <button className="next-level-btn" onClick={onNextLevel}>
                다음 레벨
              </button>
              <button className="retry-btn" onClick={onRetry}>
                다시 하기
              </button>
            </>
          ) : (
            <>
              <button className="retry-btn" onClick={onRetry}>
                다시 하기
              </button>
              <button className="main-menu-btn" onClick={onRetry}>
                메인 메뉴
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default ResultScreen;
