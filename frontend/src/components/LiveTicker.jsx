import React, { useState, useEffect } from 'react';

const LIVE_ASSETS = [
    { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', icon: '₿', basePrice: 67250 },
    { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', icon: 'Ξ', basePrice: 3480 },
    { id: 'gold', symbol: 'XAU', name: 'Gold', icon: '🥇', basePrice: 2340 },
    { id: 'eurusd', symbol: 'EUR/USD', name: 'Euro', icon: '€', basePrice: 1.0842 },
    { id: 'gbpusd', symbol: 'GBP/USD', name: 'Pound', icon: '£', basePrice: 1.2635 },
    { id: 'usdjpy', symbol: 'USD/JPY', name: 'Yen', icon: '¥', basePrice: 150.32 },
];

const LiveTicker = () => {
    const [assets, setAssets] = useState(
        LIVE_ASSETS.map(a => ({
            ...a,
            price: a.basePrice,
            change: (Math.random() - 0.4) * 3,
            flash: null,
        }))
    );

    useEffect(() => {
        const interval = setInterval(() => {
            setAssets(prev => prev.map(asset => {
                const isSmallPrice = asset.basePrice < 10;
                const volatility = isSmallPrice ? 0.001 : asset.basePrice * 0.0005;
                const delta = (Math.random() - 0.48) * volatility;
                const newPrice = asset.price + delta;
                const newChange = ((newPrice - asset.basePrice) / asset.basePrice) * 100;
                const flash = delta > 0 ? 'flash-green' : delta < 0 ? 'flash-red' : null;

                return {
                    ...asset,
                    price: newPrice,
                    change: newChange,
                    flash,
                };
            }));
        }, 2500);
        return () => clearInterval(interval);
    }, []);

    // Clear flash after animation
    useEffect(() => {
        const timeout = setTimeout(() => {
            setAssets(prev => prev.map(a => ({ ...a, flash: null })));
        }, 600);
        return () => clearTimeout(timeout);
    }, [assets]);

    const formatPrice = (asset) => {
        if (asset.basePrice > 1000) return asset.price.toFixed(2);
        if (asset.basePrice > 100) return asset.price.toFixed(2);
        if (asset.basePrice > 10) return asset.price.toFixed(2);
        return asset.price.toFixed(4);
    };

    return (
        <div className="live-ticker">
            <div className="ticker-track">
                {assets.map(asset => (
                    <div key={asset.id} className={`ticker-item ${asset.flash || ''}`}>
                        <span className="ticker-icon">{asset.icon}</span>
                        <span className="ticker-symbol">{asset.symbol}</span>
                        <span className="ticker-price">{formatPrice(asset)}</span>
                        <span className={`ticker-change ${asset.change >= 0 ? 'positive' : 'negative'}`}>
                            {asset.change >= 0 ? '+' : ''}{asset.change.toFixed(2)}%
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LiveTicker;
