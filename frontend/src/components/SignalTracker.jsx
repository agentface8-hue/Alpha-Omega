import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, X, TrendingUp, TrendingDown, Target } from 'lucide-react';

const pnlColor = v => v > 0 ? "#00ff88" : v < 0 ? "#ff4466" : "#94a3b8";
const statusColor = s => {
  if (s === "OPEN") return "#00d4ff";
  if (s === "TP3_HIT" || s === "TP2_HIT") return "#00ff88";
  if (s === "STOPPED_OUT") return "#ff4466";
  return "#fbbf24";
};
const statusLabel = s => {
  if (s === "OPEN") return "OPEN";
  if (s === "TP3_HIT") return "TP3 ✓";
  if (s === "STOPPED_OUT") return "STOPPED";
  if (s === "TIMEOUT") return "TIMEOUT";
  if (s === "MANUAL_CLOSE") return "CLOSED";
  return s;
};

const SignalTracker = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [tab, setTab] = useState('active');
  const [turboTicker, setTurboTicker] = useState('');
  const [turboLoading, setTurboLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [countdown, setCountdown] = useState(30);
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

  const fetchSignals = async (refresh = false) => {
    if (refresh) setRefreshing(true); else setLoading(true);
    try {
      const endpoint = refresh ? '/api/signals/check' : '/api/signals';
      const method = refresh ? 'POST' : 'GET';
      const res = await fetch(`${apiUrl}${endpoint}`, { method });
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
    setRefreshing(false);
  };

  const closeSignal = async (id) => {
    await fetch(`${apiUrl}/api/signals/close/${id}`, { method: 'POST' });
    fetchSignals();
  };

  const clearAll = async () => {
    if (!confirm('Clear ALL signals? This cannot be undone.')) return;
    await fetch(`${apiUrl}/api/signals/clear`, { method: 'POST' });
    fetchSignals();
  };

  const launchTurbo = async () => {
    if (!turboTicker.trim()) return;
    setTurboLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/signals/turbo/${turboTicker.trim().toUpperCase()}`, { method: 'POST' });
      if (!res.ok) { const e = await res.json(); alert(e.detail || 'Error'); }
      else { setTurboTicker(''); fetchSignals(true); }
    } catch (e) { alert(e.message); }
    setTurboLoading(false);
  };

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    setCountdown(30);
    const priceInterval = setInterval(() => fetchSignals(true), 30000);
    const tickInterval = setInterval(() => setCountdown(c => c <= 1 ? 30 : c - 1), 1000);
    return () => { clearInterval(priceInterval); clearInterval(tickInterval); };
  }, [autoRefresh]);

  useEffect(() => { fetchSignals(); }, []);

  const stats = data?.stats || {};
  const active = data?.active || [];
  const closed = data?.closed || [];
  const display = tab === 'active' ? active : closed;

  return (
    <div style={{ background:"#050810", padding:"20px 16px", fontFamily:"'Courier New',monospace", color:"#c9d8e8" }}>
      {/* Header */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", borderBottom:"1px solid #1a2535", paddingBottom:14, marginBottom:20 }}>
        <div>
          <span style={{ fontWeight:"bold", fontSize:22 }}>Signal<span style={{ color:"#c084fc" }}>Tracker</span></span>
          <span style={{ color:"#c084fc", fontSize:11, fontWeight:"bold", background:"rgba(192,132,252,0.15)", border:"1px solid rgba(192,132,252,0.3)", padding:"1px 7px", borderRadius:3, marginLeft:10 }}>LIVE</span>
          <div style={{ color:"#2a4a5a", fontSize:10, marginTop:2, fontFamily:"sans-serif" }}>PAPER VALIDATION · AUTO-TRACK · WIN RATE</div>
        </div>
        <div style={{ display:"flex", gap:8 }}>
          <button onClick={() => fetchSignals(true)} disabled={refreshing}
            style={{ background:"#0d1520", border:"1px solid #1a2535", borderRadius:4, padding:"6px 12px", color:"#c084fc", fontSize:10, fontFamily:"sans-serif", cursor:"pointer", display:"flex", alignItems:"center", gap:4 }}>
            <RefreshCw size={12} className={refreshing?"spin":""} /> {refreshing ? "CHECKING..." : "CHECK PRICES"}
          </button>
          <button onClick={clearAll}
            style={{ background:"#0d1520", border:"1px solid #ff446633", borderRadius:4, padding:"6px 12px", color:"#ff4466", fontSize:10, fontFamily:"sans-serif", cursor:"pointer" }}>
            RESET ALL
          </button>
        </div>
      </div>

      {/* Turbo Launch + Auto Refresh */}
      <div style={{ display:"flex", gap:12, marginBottom:16, alignItems:"center", flexWrap:"wrap" }}>
        <div style={{ display:"flex", gap:6, alignItems:"center", background:"#0a0f18", border:"1px solid #1a2535", borderRadius:8, padding:"8px 12px", flex:1, minWidth:250 }}>
          <span style={{ fontSize:10, color:"#c084fc", fontWeight:"bold", fontFamily:"sans-serif", whiteSpace:"nowrap" }}>⚡ TURBO</span>
          <input value={turboTicker} onChange={e => setTurboTicker(e.target.value.toUpperCase())} placeholder="AAPL" onKeyDown={e => e.key === 'Enter' && launchTurbo()}
            style={{ flex:1, background:"#0d1a2a", border:"1px solid #1a2535", borderRadius:4, padding:"6px 10px", color:"#e0e0e0", fontSize:13, fontFamily:"monospace", minWidth:60 }} />
          <button onClick={launchTurbo} disabled={turboLoading || !turboTicker.trim()}
            style={{ background:turboLoading?"#1a2535":"linear-gradient(135deg,#c084fc,#7c3aed)", border:"none", borderRadius:4, padding:"6px 14px", color:"#fff", fontSize:11, fontWeight:"bold", fontFamily:"sans-serif", cursor:turboLoading?"wait":"pointer", whiteSpace:"nowrap" }}>
            {turboLoading ? "..." : "🚀 LAUNCH"}
          </button>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8, background:"#0a0f18", border:"1px solid #1a2535", borderRadius:8, padding:"8px 12px" }}>
          <span style={{ fontSize:10, color:"#4a6070", fontFamily:"sans-serif" }}>AUTO-REFRESH</span>
          <button onClick={() => setAutoRefresh(!autoRefresh)}
            style={{ width:40, height:22, borderRadius:11, border:"none", background:autoRefresh?"#00ff88":"#1a2535", cursor:"pointer", position:"relative", transition:"background 0.2s" }}>
            <div style={{ width:18, height:18, borderRadius:9, background:"#fff", position:"absolute", top:2, left:autoRefresh?20:2, transition:"left 0.2s" }} />
          </button>
          {autoRefresh && <span style={{ fontSize:11, color:"#00ff88", fontFamily:"monospace", fontWeight:"bold", minWidth:30 }}>{countdown}s</span>}
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(6,1fr)", gap:10, marginBottom:20 }}>
        {[
          { label:"ACTIVE", val:active.length, color:"#00d4ff" },
          { label:"WIN RATE", val:`${stats.win_rate||0}%`, color:stats.win_rate>=50?"#00ff88":"#ff4466" },
          { label:"AVG P&L", val:`${stats.avg_pnl||0}%`, color:pnlColor(stats.avg_pnl||0) },
          { label:"WINS", val:stats.wins||0, color:"#00ff88" },
          { label:"LOSSES", val:stats.losses||0, color:"#ff4466" },
          { label:"TP1 HIT%", val:`${stats.tp1_hit_rate||0}%`, color:"#fbbf24" },
        ].map(c => (
          <div key={c.label} style={{ background:"#0a0f18", border:"1px solid #1a2535", borderRadius:8, padding:"12px", textAlign:"center" }}>
            <div style={{ fontSize:9, color:"#2a4a5a", letterSpacing:1.5, fontFamily:"sans-serif", marginBottom:6 }}>{c.label}</div>
            <div style={{ fontSize:20, fontWeight:"bold", color:c.color }}>{c.val}</div>
          </div>
        ))}
      </div>

      {/* Tab toggle */}
      <div style={{ display:"flex", gap:0, marginBottom:14, borderBottom:"1px solid #1a2535" }}>
        <button onClick={() => setTab('active')} style={{ background:tab==='active'?"#0d1a2a":"transparent", color:tab==='active'?"#c084fc":"#4a6070", border:"none", borderBottom:tab==='active'?"2px solid #c084fc":"2px solid transparent", padding:"8px 20px", fontSize:11, fontWeight:"bold", fontFamily:"sans-serif", cursor:"pointer" }}>
          ACTIVE ({active.length})
        </button>
        <button onClick={() => setTab('closed')} style={{ background:tab==='closed'?"#0d1a2a":"transparent", color:tab==='closed'?"#c084fc":"#4a6070", border:"none", borderBottom:tab==='closed'?"2px solid #c084fc":"2px solid transparent", padding:"8px 20px", fontSize:11, fontWeight:"bold", fontFamily:"sans-serif", cursor:"pointer" }}>
          CLOSED ({closed.length})
        </button>
      </div>

      {/* No signals message */}
      {display.length === 0 && (
        <div style={{ textAlign:"center", padding:"40px", color:"#2a4a5a", fontFamily:"sans-serif" }}>
          <Target size={32} style={{ marginBottom:10, opacity:0.3 }} />
          <div style={{ fontSize:14 }}>{tab === 'active' ? 'No active signals' : 'No closed signals yet'}</div>
          <div style={{ fontSize:11, marginTop:6, color:"#1a2535" }}>Run a scan with 60%+ conviction to auto-record signals</div>
        </div>
      )}

      {/* Signals Table */}
      {display.length > 0 && (
        <div style={{ overflowX:"auto", borderRadius:8, border:"1px solid #1a2535" }}>
          <table style={{ width:"100%", borderCollapse:"collapse", background:"#080c14", whiteSpace:"nowrap", minWidth:1000 }}>
            <thead>
              <tr>
                {["Ticker","Type","Entry","Current","P&L","SL","TP1","TP2","TP3","Conv","TAS","Days","Status",tab==='active'?"":"Reason"].filter(Boolean).map(h => (
                  <th key={h} style={{ background:"#0a0f18", color:"#2a4a5a", fontSize:9, letterSpacing:1.2, textTransform:"uppercase", padding:"10px 8px", textAlign:"left", borderBottom:"1px solid #1a2535", fontFamily:"sans-serif" }}>{h}</th>
                ))}
                {tab === 'active' && <th style={{ background:"#0a0f18", borderBottom:"1px solid #1a2535" }}></th>}
              </tr>
            </thead>
            <tbody>
              {display.map(s => {
                const td = { padding:"10px 8px", borderBottom:"1px solid #0d1420", verticalAlign:"middle" };
                return (
                  <tr key={s.id}>
                    <td style={td}>
                      <div style={{ color:s.asset_type==="crypto"?"#f7931a":"#00d4ff", fontWeight:"bold", fontSize:13 }}>{s.ticker}</div>
                      <div style={{ color:"#2a4a5a", fontSize:9, fontFamily:"sans-serif" }}>{s.entry_time?.slice(0,10)}</div>
                    </td>
                    <td style={td}>
                      <span style={{ fontSize:9, fontFamily:"sans-serif", padding:"2px 6px", borderRadius:3,
                        background:s.asset_type==="crypto"?"rgba(247,147,26,0.1)":"rgba(0,212,255,0.1)",
                        color:s.asset_type==="crypto"?"#f7931a":"#00d4ff",
                        border:`1px solid ${s.asset_type==="crypto"?"#f7931a33":"#00d4ff33"}` }}>
                        {s.asset_type==="crypto"?"₿ CRYPTO":"📈 STOCK"}
                      </span>
                    </td>
                    <td style={{...td, fontWeight:"bold", fontSize:12}}>${s.entry_price}</td>
                    <td style={{...td, fontWeight:"bold", fontSize:12, color:pnlColor(s.pnl_pct)}}>${s.current_price}</td>
                    <td style={td}>
                      <div style={{ display:"flex", alignItems:"center", gap:4 }}>
                        {s.pnl_pct > 0 ? <TrendingUp size={12} color="#00ff88" /> : s.pnl_pct < 0 ? <TrendingDown size={12} color="#ff4466" /> : null}
                        <span style={{ color:pnlColor(s.pnl_pct), fontWeight:"bold", fontSize:13 }}>{s.pnl_pct > 0 ? "+" : ""}{s.pnl_pct}%</span>
                      </div>
                    </td>
                    <td style={{...td, color:"#ff4466", fontSize:11}}>${s.sl}</td>
                    <td style={{...td, color:s.tp1_hit?"#00ff88":"#4a6070", fontSize:11, fontWeight:s.tp1_hit?"bold":"normal"}}>{s.tp1_hit?"✓ ":""}${s.tp1}</td>
                    <td style={{...td, color:s.tp2_hit?"#00ff88":"#4a6070", fontSize:11, fontWeight:s.tp2_hit?"bold":"normal"}}>{s.tp2_hit?"✓ ":""}${s.tp2}</td>
                    <td style={{...td, color:s.tp3_hit?"#00ff88":"#4a6070", fontSize:11, fontWeight:s.tp3_hit?"bold":"normal"}}>{s.tp3_hit?"✓ ":""}${s.tp3}</td>
                    <td style={{...td, fontSize:12, fontWeight:"bold", color:s.conviction>=70?"#00ff88":s.conviction>=60?"#fbbf24":"#94a3b8"}}>{s.conviction}%</td>
                    <td style={{...td, fontSize:12, fontWeight:"bold", color:parseInt(s.tas)>=3?"#00ff88":"#fbbf24"}}>{s.tas}</td>
                    <td style={{...td, fontSize:12, color:"#94a3b8", fontFamily:"sans-serif"}}>{s.bars_held}d</td>
                    <td style={td}>
                      <span style={{ fontSize:10, fontWeight:"bold", padding:"3px 8px", borderRadius:3, fontFamily:"sans-serif",
                        background:`${statusColor(s.status)}15`, color:statusColor(s.status), border:`1px solid ${statusColor(s.status)}33` }}>
                        {statusLabel(s.status)}
                      </span>
                    </td>
                    {tab === 'closed' && <td style={{...td, fontSize:10, color:"#4a6070", fontFamily:"sans-serif", maxWidth:150, whiteSpace:"normal"}}>{s.close_reason}</td>}
                    {tab === 'active' && (
                      <td style={td}>
                        <button onClick={() => closeSignal(s.id)} style={{ background:"transparent", border:"1px solid #ff446633", borderRadius:3, padding:"3px 6px", color:"#ff4466", fontSize:9, cursor:"pointer", fontFamily:"sans-serif" }}>
                          <X size={10} /> CLOSE
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default SignalTracker;
