import type { Incident } from '../../types';
import RiskBadge from '../Common/RiskBadge';
import StatusBadge from '../Common/StatusBadge';

interface ActiveIncidentsProps {
  incidents: Incident[];
}

export default function ActiveIncidents({ incidents }: ActiveIncidentsProps) {
  const active = incidents.filter((i) => i.status !== 'RESOLVED').slice(0, 6);

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Active Incidents</span>
        <div style={{ display: 'flex', gap: 6 }}>
          <span className="demo-data-label">DEMO DATA</span>
          <span
            style={{
              fontSize: 11,
              color: 'var(--text-muted)',
              background: 'var(--bg-elevated)',
              padding: '2px 7px',
              borderRadius: 3,
            }}
          >
            {active.length} active
          </span>
        </div>
      </div>

      {active.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">✅</div>
          <div>No active incidents — All clear</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {active.map((inc) => (
            <div
              key={inc.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
                padding: '8px 10px',
                background: 'var(--bg-elevated)',
                borderRadius: 4,
                borderLeft: `3px solid ${
                  inc.severity === 'HIGH'
                    ? 'var(--accent-red)'
                    : inc.severity === 'MEDIUM'
                    ? 'var(--accent-orange)'
                    : 'var(--accent-green)'
                }`,
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    marginBottom: 3,
                    flexWrap: 'wrap',
                  }}
                >
                  <span
                    style={{
                      fontFamily: 'monospace',
                      fontSize: 11,
                      color: 'var(--accent-blue)',
                      fontWeight: 700,
                    }}
                  >
                    {inc.display_id}
                  </span>
                  <RiskBadge level={inc.severity} size="sm" />
                  <StatusBadge status={inc.status} />
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 2 }}>
                  🦁 {inc.species} · 📍 {inc.village}
                </div>
                {inc.pending_approval && (
                  <span className="badge badge-ai" style={{ fontSize: 9 }}>
                    ⏳ OFFICER APPROVAL REQUIRED
                  </span>
                )}
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <span
                  className={`risk-score ${
                    inc.risk_score >= 0.7
                      ? 'high'
                      : inc.risk_score >= 0.4
                      ? 'medium'
                      : 'low'
                  }`}
                >
                  {inc.risk_score.toFixed(2)}
                </span>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
                  {new Date(inc.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
