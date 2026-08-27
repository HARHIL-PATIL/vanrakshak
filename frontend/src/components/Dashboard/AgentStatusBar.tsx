import type { AgentInfo } from '../../types';

interface AgentStatusBarProps {
  agents: AgentInfo[];
  pendingApprovals?: number;
}

const STATUS_COLOR: Record<string, string> = {
  ACTIVE: 'var(--accent-green)',
  IDLE: 'var(--accent-blue)',
  ERROR: 'var(--accent-red)',
  WAITING: 'var(--accent-yellow)',
};

export default function AgentStatusBar({ agents, pendingApprovals = 0 }: AgentStatusBarProps) {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">🤖 AI Agent Status</span>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {pendingApprovals > 0 && (
            <span className="badge badge-ai">⏳ {pendingApprovals} PENDING APPROVALS</span>
          )}
          <span className="demo-data-label">DEMO DATA</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {agents.map((agent) => {
          const color = STATUS_COLOR[agent.status] ?? 'var(--text-muted)';
          return (
            <div
              key={agent.agent_id}
              style={{
                flex: '1 1 160px',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderTop: `2px solid ${color}`,
                borderRadius: 5,
                padding: '10px 12px',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: 6,
                }}
              >
                <div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, letterSpacing: 0.5 }}>
                    AGENT {agent.agent_number}
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {agent.name}
                  </div>
                </div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 5,
                    padding: '2px 7px',
                    background: `${color}20`,
                    border: `1px solid ${color}`,
                    borderRadius: 3,
                    fontSize: 9,
                    fontWeight: 700,
                    color,
                  }}
                >
                  <div
                    style={{
                      width: 5,
                      height: 5,
                      borderRadius: '50%',
                      background: color,
                    }}
                  />
                  {agent.status}
                </div>
              </div>

              <div
                style={{
                  fontSize: 11,
                  color: 'var(--text-muted)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                title={agent.latest_action}
              >
                {agent.latest_action}
              </div>

              <div style={{ marginTop: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div className="confidence-bar-wrap" style={{ flex: 1, marginRight: 8 }}>
                  <div className="confidence-bar">
                    <div
                      className="confidence-bar-fill"
                      style={{
                        width: `${agent.confidence * 100}%`,
                        background: color,
                      }}
                    />
                  </div>
                </div>
                <span style={{ fontSize: 10, fontFamily: 'monospace', color }}>
                  {agent.confidence.toFixed(2)}
                </span>
              </div>

              {agent.escalation_required && (
                <div style={{ marginTop: 6 }}>
                  <span className="badge badge-waiting" style={{ fontSize: 9 }}>
                    ⚡ ESCALATION REQUIRED
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
