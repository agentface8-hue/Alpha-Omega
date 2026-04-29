import React, { useState, useEffect, useRef } from 'react';
import { RefreshCw } from 'lucide-react';

const PAD = { l:62, r:12, t:18, b:32 };

function priceToY(price, minP, maxP, h) {
  return PAD.t + (1 - (price - minP) / (maxP - minP)) * (h - PAD.t - PAD.b);
}
function idxToX(i, total, w) {
  const plotW = w - PAD.l - PAD.r;
  return PAD.l + (i + 0.5) * (plotW / total);
}

const ChartPanel = ({ symbol, tradeParams }) => {
  const [data, setData]       = useState(null);
  const [interval, setIv]     = useState('1d');
  const [chartType, setType]  = useState('candle');
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [dims, setDims]       = useState({ w:800, h:340 });
  const wrapRef = useRef(null);

  useEffect(() => {
    const ro = new ResizeObserver(entries => {
      const w = entries[0].contentRect.width;
      if (w > 0) setDims({ w, h: Math.max(280, Math.round(w * 0.42)) });
    });
    if (wrapRef.current) ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  useEffect(() => { if (symbol) fetchChart(); }, [symbol, interval]);

  const fetchChart = async () => {
    setLoading(true); setError(null); setData(null);
    try {
      const base = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const res  = await fetch(`${base}/api/chart/${symbol}?interval=${interval}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData(await res.json());
    } catch (e) { setError(e.message); }
    setLoading(false);
  };

  const renderSVG = () => {
    if (!data?.candles?.length) return null;
    const { candles, sr_levels = [], channel } = data;
    const { w, h } = dims;
    const tp = tradeParams;

    const allPrices = candles.flatMap(c => [c.h, c.l]);
    if (tp) { allPrices.push(tp.entry_low, tp.entry_high, tp.sl, tp.tp1); }
    if (channel) { allPrices.push(...channel.upper, ...channel.lower); }
    sr_levels.forEach(s => allPrices.push(s.level));

    const rawMin = Math.min(...allPrices);
    const rawMax = Math.max(...allPrices);
    const pad    = (rawMax - rawMin) * 0.06;
    const minP   = rawMin - pad;
    const maxP   = rawMax + pad;

    const cw   = Math.max(2, (w - PAD.l - PAD.r) / candles.length - 1);
    const py   = p => priceToY(p, minP, maxP, h);
    const ix   = (i) => idxToX(i, candles.length, w);
    const n    = candles.length - 1;

    // Y-axis price ticks
    const ticks = [];
    const step  = (maxP - minP) / 6;
    for (let i = 0; i <= 6; i++) {
      const p = minP + i * step;
      const y = py(p);
      ticks.push({ p, y });
    }

    // X-axis date labels (every ~10 candles)
    const dateLabels = [];
    const every = Math.max(1, Math.round(candles.length / 6));
    candles.forEach((c, i) => {
      if (i % every === 0) dateLabels.push({ i, t: c.t.slice(5) });
    });

    return (
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ display:'block' }}>
        {/* Background */}
        <rect x={PAD.l} y={PAD.t} width={w - PAD.l - PAD.r} height={h - PAD.t - PAD.b}
          fill="#050810" rx="2" />

        {/* Grid lines */}
        {ticks.map(({ p, y }) => (
          <g key={p}>
            <line x1={PAD.l} y1={y} x2={w - PAD.r} y2={y} stroke="#1a2535" strokeWidth="0.5" />
            <text x={PAD.l - 4} y={y + 4} textAnchor="end" fontSize="9" fill="#3a5060" fontFamily="monospace">
              {p.toFixed(0)}
            </text>
          </g>
        ))}

        {/* Date labels */}
        {dateLabels.map(({ i, t }) => (
          <text key={i} x={ix(i)} y={h - 6} textAnchor="middle" fontSize="8" fill="#3a5060" fontFamily="monospace">{t}</text>
        ))}

        {/* Channel lines */}
        {channel && (
          <g opacity="0.5">
            <line x1={PAD.l} y1={py(channel.upper[0])} x2={w - PAD.r} y2={py(channel.upper[1])} stroke="#7c3aed" strokeWidth="1" strokeDasharray="4 3" />
            <line x1={PAD.l} y1={py(channel.mid[0])}   x2={w - PAD.r} y2={py(channel.mid[1])}   stroke="#7c3aed" strokeWidth="0.6" strokeDasharray="2 4" />
            <line x1={PAD.l} y1={py(channel.lower[0])} x2={w - PAD.r} y2={py(channel.lower[1])} stroke="#7c3aed" strokeWidth="1" strokeDasharray="4 3" />
          </g>
        )}

        {/* S/R levels */}
        {sr_levels.map((s, i) => {
          const c = s.type === 'resistance' ? '#ff4466' : '#00ff88';
          return (
            <g key={i}>
              <line x1={PAD.l} y1={py(s.level)} x2={w - PAD.r} y2={py(s.level)}
                stroke={c} strokeWidth="0.7" strokeDasharray="5 4" opacity="0.5" />
              <text x={w - PAD.r + 2} y={py(s.level) + 3} fontSize="7" fill={c} fontFamily="monospace">{s.level}</text>
            </g>
          );
        })}

        {/* Entry zone + SL + TP1 markers */}
        {tp && (
          <g>
            {/* Entry zone band */}
            <rect x={PAD.l} y={py(tp.entry_high)} width={w - PAD.l - PAD.r}
              height={Math.abs(py(tp.entry_low) - py(tp.entry_high))}
              fill="rgba(0,255,136,0.07)" stroke="rgba(0,255,136,0.3)" strokeWidth="0.5" />
            {/* SL line */}
            <line x1={PAD.l} y1={py(tp.sl)} x2={w - PAD.r} y2={py(tp.sl)}
              stroke="#ff4466" strokeWidth="1.2" strokeDasharray="6 3" />
            <text x={PAD.l + 4} y={py(tp.sl) - 3} fontSize="8" fill="#ff4466" fontFamily="sans-serif">
              SL ${tp.sl} {tp.sl_note ? `(${tp.sl_note})` : ''}
            </text>
            {/* Entry label */}
            <text x={PAD.l + 4} y={py(tp.entry_low) + 10} fontSize="8" fill="#00ff88" fontFamily="sans-serif">
              Entry ${tp.entry_low}–${tp.entry_high}
            </text>
          </g>
        )}

        {/* Candles or Line */}
        {chartType === 'candle' ? candles.map((c, i) => {
          const x   = ix(i);
          const isG = c.c >= c.o;
          const col = isG ? '#00ff88' : '#ff4466';
          const top = py(Math.max(c.o, c.c));
          const bot = py(Math.min(c.o, c.c));
          const bh  = Math.max(1, bot - top);
          return (
            <g key={i}>
              <line x1={x} y1={py(c.h)} x2={x} y2={py(c.l)} stroke={col} strokeWidth="0.8" />
              <rect x={x - cw/2} y={top} width={cw} height={bh} fill={col} opacity="0.85" />
            </g>
          );
        }) : (
          <polyline
            points={candles.map((c, i) => `${ix(i)},${py(c.c)}`).join(' ')}
            fill="none" stroke="#00d4ff" strokeWidth="1.5" />
        )}

        {/* Axis border */}
        <line x1={PAD.l} y1={PAD.t} x2={PAD.l} y2={h - PAD.b} stroke="#1a2535" strokeWidth="1" />
        <line x1={PAD.l} y1={h - PAD.b} x2={w - PAD.r} y2={h - PAD.b} stroke="#1a2535" strokeWidth="1" />
      </svg>
    );
  };

  const btnStyle = (active) => ({
    background: active ? '#1a2535' : 'transparent',
    color: active ? '#00d4ff' : '#4a6070',
    border: `1px solid ${active ? '#1a2535' : '#0d1420'}`,
    borderRadius: 4, padding: '3px 9px', fontSize: 10,
    fontWeight: 'bold', cursor: 'pointer', fontFamily: 'sans-serif'
  });

  return (
    <div ref={wrapRef} style={{ background:'#080c14', border:'1px solid #1a2535', borderRadius:10,
      marginTop:14, overflow:'hidden', fontFamily:"'Courier New',monospace" }}>

      {/* Header bar */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between',
        borderBottom:'1px solid #1a2535', padding:'8px 14px', background:'#0a0f18' }}>
        <span style={{ color:'#00d4ff', fontSize:11, fontWeight:'bold', letterSpacing:1 }}>
          📊 {symbol || '—'} CHART
        </span>
        <div style={{ display:'flex', gap:6, alignItems:'center' }}>
          <button style={btnStyle(interval==='1d')} onClick={() => setIv('1d')}>1D</button>
          <button style={btnStyle(interval==='1w')} onClick={() => setIv('1w')}>1W</button>
          <div style={{ width:1, height:14, background:'#1a2535' }} />
          <button style={btnStyle(chartType==='candle')} onClick={() => setType('candle')}>Candles</button>
          <button style={btnStyle(chartType==='line')}   onClick={() => setType('line')}>Line</button>
          <button onClick={fetchChart} style={{ background:'transparent', border:'none',
            color:'#4a6070', cursor:'pointer', padding:'2px 4px' }}>
            <RefreshCw size={12} />
          </button>
        </div>
      </div>

      {/* Chart area */}
      <div style={{ padding:'8px 4px 4px' }}>
        {loading && <div style={{ color:'#4a6070', fontSize:11, padding:20, textAlign:'center', fontFamily:'sans-serif' }}>Loading chart...</div>}
        {error   && <div style={{ color:'#ff4466', fontSize:11, padding:20, textAlign:'center', fontFamily:'sans-serif' }}>⚠ {error}</div>}
        {!loading && !error && renderSVG()}
      </div>

      {/* Legend */}
      {tradeParams && (
        <div style={{ borderTop:'1px solid #1a2535', padding:'6px 14px', display:'flex', gap:16, flexWrap:'wrap' }}>
          {[['Entry zone','rgba(0,255,136,0.4)'],['SL','#ff4466'],['Channel','#7c3aed'],['S/R','#94a3b8']].map(([lbl,c])=>(
            <div key={lbl} style={{ display:'flex', alignItems:'center', gap:5 }}>
              <div style={{ width:18, height:2, background:c, borderRadius:1 }} />
              <span style={{ color:'#4a6070', fontSize:9, fontFamily:'sans-serif' }}>{lbl}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChartPanel;
