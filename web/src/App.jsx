import React, { useState, useEffect } from 'react';
import './App.css';
import WelcomeScreen from './components/WelcomeScreen';
import GameScreen from './components/GameScreen';
import ResultScreen from './components/ResultScreen';

function App() {
  const [gameState, setGameState] = useState('welcome'); // welcome, playing, result
  const [playerName, setPlayerName] = useState('');
  const [currentLevel, setCurrentLevel] = useState(1);
  const [sessionData, setSessionData] = useState(null);
  const [gameResult, setGameResult] = useState(null);

  const handleStartGame = (name, level) => {
    setPlayerName(name);
    setCurrentLevel(level);

    // 게임 데이터 초기화
    const sessionId = `session_${Date.now()}`;
    setSessionData({
      sessionId,
      playerName: name,
      levelId: level,
      submittedClaims: [],
      startTime: Date.now(),
    });

    setGameState('playing');
  };

  const handleGameComplete = (claims, success) => {
    setGameResult({
      claims,
      success,
      playerName,
      levelId: currentLevel,
    });
    setGameState('result');
  };

  const handleRetry = () => {
    setGameState('welcome');
    setPlayerName('');
    setCurrentLevel(1);
    setSessionData(null);
    setGameResult(null);
  };

  const handleNextLevel = () => {
    if (currentLevel < 3) {
      handleStartGame(playerName, currentLevel + 1);
    } else {
      handleRetry();
    }
  };

  return (
    <div className="app">
      {gameState === 'welcome' && (
        <WelcomeScreen onStartGame={handleStartGame} />
      )}
      {gameState === 'playing' && sessionData && (
        <GameScreen
          sessionData={sessionData}
          onComplete={handleGameComplete}
        />
      )}
      {gameState === 'result' && gameResult && (
        <ResultScreen
          result={gameResult}
          onRetry={handleRetry}
          onNextLevel={gameResult.success && currentLevel < 3 ? handleNextLevel : null}
        />
      )}
    </div>
  );
}

export default App;
