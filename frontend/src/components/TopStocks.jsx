import React, { useState, useEffect } from 'react';

// Agent avatar definitions
const AGENTS = {
    historian: { emoji: '📊', name: 'Historian', color: '#3b82f6' },
    newsroom: { emoji: '📰', name: 'Newsroom', color: '#8b5cf6' },
    macro: { emoji: '🌍', name: 'Macro-Strategist', color: '#06b6d4' },
    synthesis: { emoji: '🧠', name: 'Synthesis Engine', color: '#f59e0b' },
    contrarian: { emoji: '⚔️', name: 'Contrarian', color: '#ef4444' },
    executioner: { emoji: '⚡', name: 'Executioner', color: '#22c55e' },
};

// Top performing stocks (simulated real-time data)
const STOCK_DATA = [
    { symbol: 'NVDA', name: 'NVIDIA Corp', price: 878.35, change: +4.72 },
    { symbol: 'AAPL', name: 'Apple Inc', price: 185.92, change: +1.23 },
    { symbol: 'MSFT', name: 'Microsoft', price: 415.60, change: +2.15 },
    { symbol: 'GOOGL', name: 'Alphabet', price: 141.80, change: -0.45 },
    { symbol: 'AMZN', name: 'Amazon', price: 178.25, change: +3.18 },
    { symbol: 'META', name: 'Meta Platforms', price: 484.10, change: +1.95 },
    { symbol: 'TSLA', name: 'Tesla Inc', price: 193.57, change: -2.31 },
    { symbol: 'PLTR', name: 'Palantir', price: 24.85, change: +5.42 },
];

const TopStocks = ({ onSelectTicker }) => {
    const [stocks, setStocks] = useState(STOCK_DATA);

    // Simulate live price updates
    useEffect(() => {
        const interval = setInterval(() => {
            setStocks(prev => prev.map(stock => {
                const fluctuation = (Math.random() - 0.48) * 2;
                const newPrice = +(stock.price + fluctuation).toFixed(2);
                const newChange = +(stock.change + (Math.random() - 0.5) * 0.3).toFixed(2);
                return { ...stock, price: newPrice, change: newChange };
            }));
        }, 4000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="top-stocks">
            <div className="widget-header">
                <span className="widget-icon">🔥</span>
                <span className="widget-title">TOP MOVERS</span>
            </div>
            <div className="stocks-grid">
                {stocks.map(stock => (
                    <div
                        key={stock.symbol}
                        className="stock-card"
                        onClick={() => onSelectTicker && onSelectTicker(stock.symbol)}
                        title={`Analyze ${stock.symbol}`}
                    >
                        <div className="stock-symbol">{stock.symbol}</div>
                        <div className="stock-price">${stock.price.toFixed(2)}</div>
                        <div className={`stock-change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                            {stock.change >= 0 ? '▲' : '▼'} {Math.abs(stock.change).toFixed(2)}%
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export { AGENTS };
export default TopStocks;
