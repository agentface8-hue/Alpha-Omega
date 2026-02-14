import React, { useEffect, useRef } from 'react';

// Agent avatar mapping
const AGENT_AVATARS = {
    'The Historian': { emoji: '📊', color: '#3b82f6' },
    'The Newsroom': { emoji: '📰', color: '#8b5cf6' },
    'The Macro-Strategist': { emoji: '🌍', color: '#06b6d4' },
    'Synthesis Engine': { emoji: '🧠', color: '#f59e0b' },
    'The Contrarian': { emoji: '⚔️', color: '#ef4444' },
    'The Executioner': { emoji: '⚡', color: '#22c55e' },
};

function getAgentFromMessage(message) {
    for (const [name, data] of Object.entries(AGENT_AVATARS)) {
        if (message.includes(name)) return data;
    }
    return null;
}

const Terminal = ({ logs }) => {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="terminal">
            {logs.length === 0 && (
                <div className="terminal-idle">
                    <span className="terminal-prompt">▶</span> Awaiting orders...<span className="cursor-blink"></span>
                </div>
            )}
            {logs.map((log, index) => {
                const agent = getAgentFromMessage(log.message);
                return (
                    <div key={index} className="terminal-line">
                        <span className="terminal-timestamp">[{log.timestamp}]</span>
                        {agent && (
                            <span className="agent-avatar" style={{ background: agent.color + '22', borderColor: agent.color + '55' }}>
                                {agent.emoji}
                            </span>
                        )}
                        <span className={`terminal-message ${log.type === 'error' ? 'is-error' : ''} ${log.type === 'success' ? 'is-success' : ''}`}>
                            {log.message}
                        </span>
                    </div>
                );
            })}
            {logs.length > 0 && logs[logs.length - 1]?.type !== 'success' && logs[logs.length - 1]?.type !== 'error' && (
                <div className="terminal-line">
                    <span className="terminal-prompt">▶</span>
                    <span className="cursor-blink"></span>
                </div>
            )}
            <div ref={bottomRef} />
        </div>
    );
};

export default Terminal;
