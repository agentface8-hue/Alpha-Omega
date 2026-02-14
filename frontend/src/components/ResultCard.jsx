import React from 'react';
import { TrendingUp, ShieldAlert, ShieldCheck } from 'lucide-react';

const ResultCard = ({ result }) => {
    if (!result) return null;

    const { consensus_view, confidence_score, executioner_decision, full_report } = result;
    const decision = executioner_decision || 'PENDING';

    const upperDecision = decision.toUpperCase();
    const isBuy = upperDecision.includes('BUY');
    const isHalt = upperDecision.includes('HALT');

    let cardClass = 'result-hold';
    let decisionColor = 'var(--accent-yellow)';
    let Icon = ShieldCheck;

    if (isBuy) {
        cardClass = 'result-buy';
        decisionColor = 'var(--accent-green)';
        Icon = TrendingUp;
    } else if (isHalt) {
        cardClass = 'result-halt';
        decisionColor = 'var(--accent-red)';
        Icon = ShieldAlert;
    }

    return (
        <div className={`result-card ${cardClass}`}>
            <div className="result-header">
                <div className="result-decision" style={{ color: decisionColor }}>
                    <Icon size={18} />
                    FINAL DECISION
                </div>
                <div className="result-confidence">
                    CONFIDENCE: {(confidence_score * 100).toFixed(1)}%
                </div>
            </div>

            <div className="result-body">
                <div style={{
                    fontSize: '20px',
                    fontWeight: 800,
                    color: decisionColor,
                    letterSpacing: '2px',
                    marginBottom: '12px'
                }}>
                    {decision}
                </div>
                <p style={{
                    borderLeft: '2px solid var(--border-color)',
                    paddingLeft: '12px',
                    fontStyle: 'italic',
                    color: 'var(--text-muted)'
                }}>
                    "{consensus_view}"
                </p>
            </div>

            <div className="result-agents">
                <div className="agent-badge">
                    <div className="agent-badge-label">HISTORIAN</div>
                    <div className="agent-badge-status">
                        {full_report?.historian ? 'Analysis Complete' : 'Pending...'}
                    </div>
                </div>
                <div className="agent-badge">
                    <div className="agent-badge-label">NEWSROOM</div>
                    <div className="agent-badge-status">
                        {full_report?.newsroom ? 'Analysis Complete' : 'Pending...'}
                    </div>
                </div>
                <div className="agent-badge">
                    <div className="agent-badge-label">MACRO</div>
                    <div className="agent-badge-status">
                        {full_report?.macro ? 'Analysis Complete' : 'Pending...'}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultCard;
