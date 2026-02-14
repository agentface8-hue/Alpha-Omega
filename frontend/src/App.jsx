import React, { useState } from 'react';
import { Search, Activity } from 'lucide-react';
import Terminal from './components/Terminal';
import ResultCard from './components/ResultCard';
import LiveTicker from './components/LiveTicker';
import TopStocks from './components/TopStocks';
import { playThinkingSound, playSuccessSound, playErrorSound } from './utils/sounds';

const App = () => {
  const [symbol, setSymbol] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const getTimestamp = () => {
    return new Date().toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!symbol || isLoading) return;

    setIsLoading(true);
    setLogs([]);
    setResult(null);
    setError(null);

    const steps = [
      { agent: 'The Historian', action: 'is analyzing...' },
      { agent: 'The Newsroom', action: 'is analyzing...' },
      { agent: 'The Macro-Strategist', action: 'is analyzing...' },
      { agent: 'Synthesis Engine', action: 'is analyzing...' },
      { agent: 'The Contrarian', action: 'is analyzing...' },
      { agent: 'The Executioner', action: 'is analyzing...' },
    ];

    // Stream timestamped logs with sound effects
    let stepIndex = 0;
    const interval = setInterval(() => {
      if (stepIndex < steps.length) {
        const step = steps[stepIndex];
        playThinkingSound(); // Beep on each agent step
        setLogs(prev => [...prev, {
          timestamp: getTimestamp(),
          message: `>> ${step.agent} ${step.action}`,
          type: 'info'
        }]);
        stepIndex++;
      } else {
        clearInterval(interval);
      }
    }, 800);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Unknown server error' }));
        throw new Error(`Analysis failed (${response.status})`);
      }

      const data = await response.json();

      setTimeout(() => {
        playSuccessSound(); // Success chime
        setResult(data);
        setLogs(prev => [...prev, {
          timestamp: getTimestamp(),
          message: `✓ Analysis complete. Confidence: ${(data.confidence_score * 100).toFixed(0)}%`,
          type: 'success'
        }]);
        setIsLoading(false);
      }, steps.length * 800 + 500);

    } catch (err) {
      setTimeout(() => {
        playErrorSound(); // Error buzz
        setError(err.message);
        setLogs(prev => [...prev, {
          timestamp: getTimestamp(),
          message: `ERROR: ${err.message}`,
          type: 'error'
        }]);
        setIsLoading(false);
      }, steps.length * 800 + 500);
    }
  };

  const handleTickerSelect = (ticker) => {
    setSymbol(ticker);
  };

  return (
    <div>
      {/* Live Ticker Bar */}
      <LiveTicker />

      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="header-icon">
            <Activity size={26} />
          </div>
          <div>
            <div className="header-title">ALPHA - OMEGA</div>
            <div className="header-subtitle">Council of Experts Trading System</div>
          </div>
        </div>
        <div className="system-status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>
      </header>

      {/* Main */}
      <main className="main-container">
        {/* Search */}
        <form className="search-form" onSubmit={handleAnalyze}>
          <div className="search-input-wrapper">
            <input
              type="text"
              className="search-input"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="ENTER TICKER"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="search-button"
              disabled={isLoading || !symbol}
            >
              <Search size={20} />
            </button>
          </div>
        </form>
        <div className="search-hint">Press Enter to analyze a stock symbol</div>

        {/* Two-column layout */}
        <div className="dashboard-grid">
          {/* Left: Terminal + Results */}
          <div className="dashboard-main">
            <Terminal logs={logs} />

            {error && (
              <div className="error-banner">
                <div className="error-icon">!</div>
                <span>{error}</span>
              </div>
            )}

            <ResultCard result={result} />
          </div>

          {/* Right: Top Stocks */}
          <div className="dashboard-sidebar">
            <TopStocks onSelectTicker={handleTickerSelect} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
