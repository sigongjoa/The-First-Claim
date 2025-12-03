import React, { useState } from 'react';
import '../styles/WelcomeScreen.css';

function WelcomeScreen({ onStartGame }) {
  const [playerName, setPlayerName] = useState('');
  const [selectedLevel, setSelectedLevel] = useState(1);
  const [error, setError] = useState('');

  const levels = [
    {
      id: 1,
      title: '기본 청구항 작성',
      difficulty: 'EASY',
      claims: 1,
      time: 300,
      description: '간단한 독립항을 작성하세요',
    },
    {
      id: 2,
      title: '종속항 작성',
      difficulty: 'NORMAL',
      claims: 3,
      time: 600,
      description: '독립항을 기반으로 종속항을 작성하세요',
    },
    {
      id: 3,
      title: '복합 청구항 세트',
      difficulty: 'HARD',
      claims: 5,
      time: 900,
      description: '여러 독립항과 종속항을 포함한 청구항 세트를 작성하세요',
    },
  ];

  const handleStart = () => {
    if (!playerName.trim()) {
      setError('플레이어 이름을 입력해주세요');
      return;
    }
    onStartGame(playerName, selectedLevel);
  };

  return (
    <div className="welcome-container">
      <div className="welcome-card">
        <div className="welcome-header">
          <h1>🎮 청구항 작성 게임</h1>
          <p className="tagline">PROJECT OVERRIDE</p>
          <p className="subtitle">법을 읽는 사용자가 아니라, 법을 설계하는 창조자가 된다</p>
        </div>

        <div className="welcome-content">
          <div className="input-section">
            <label htmlFor="playerName">플레이어 이름</label>
            <input
              id="playerName"
              type="text"
              value={playerName}
              onChange={(e) => {
                setPlayerName(e.target.value);
                setError('');
              }}
              placeholder="이름을 입력하세요"
              onKeyPress={(e) => e.key === 'Enter' && handleStart()}
            />
            {error && <p className="error-message">{error}</p>}
          </div>

          <div className="level-section">
            <h2>레벨 선택</h2>
            <div className="level-grid">
              {levels.map((level) => (
                <div
                  key={level.id}
                  className={`level-card ${selectedLevel === level.id ? 'active' : ''}`}
                  onClick={() => setSelectedLevel(level.id)}
                >
                  <div className="level-header">
                    <h3>{level.title}</h3>
                    <span className={`difficulty ${level.difficulty.toLowerCase()}`}>
                      {level.difficulty}
                    </span>
                  </div>
                  <p className="description">{level.description}</p>
                  <div className="level-stats">
                    <div className="stat">
                      <span className="label">필요 청구항:</span>
                      <span className="value">{level.claims}개</span>
                    </div>
                    <div className="stat">
                      <span className="label">시간 제한:</span>
                      <span className="value">{level.time}초</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button className="start-button" onClick={handleStart}>
            게임 시작
          </button>
        </div>

        <div className="welcome-footer">
          <p>변리사 시험을 위한 TDD 학습 플랫폼</p>
        </div>
      </div>
    </div>
  );
}

export default WelcomeScreen;
