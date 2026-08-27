import type { DashboardStats } from '../../types';

interface StatsCardsProps {
  stats: DashboardStats;
}

export default function StatsCards({ stats }: StatsCardsProps) {
  const confPct = Math.round(stats.avg_ai_confidence * 100);
  const confColor =
    confPct >= 80
      ? 'var(--accent-green)'
      : confPct >= 60
      ? 'var(--accent-orange)'
      : 'var(--accent-red)';

  return (
    <div className="grid-4 mb-16">
      {/* Active Incidents */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">Active Incidents</span>
          <span style={{ fontSize: 18 }}>📋</span>
        </div>
        <div
          style={{
            fontSize: 32,
            fontWeight: 700,
            color: 'var(--text-primary)',
            lineHeight: 1,
            marginBottom: 10,
          }}
        >
          {stats.active_incidents}
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <span className="badge badge-high" style={{ fontSize: 10 }}>
            {stats.incidents_high} HIGH
          </span>
          <span className="badge badge-medium" style={{ fontSize: 10 }}>
            {stats.incidents_medium} MED
          </span>
          <span className="badge badge-low" style={{ fontSize: 10 }}>
            {stats.incidents_low} LOW
          </span>
        </div>
      </div>

      {/* AI Confidence */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">AI Confidence</span>
          <span style={{ fontSize: 18 }}>🤖</span>
        </div>
        <div
          style={{
            fontSize: 32,
            fontWeight: 700,
            color: confColor,
            lineHeight: 1,
            marginBottom: 10,
          }}
        >
          {confPct}%
        </div>
        <div className="confidence-bar-wrap">
          <div className="confidence-bar">
            <div
              className="confidence-bar-fill"
              style={{ width: `${confPct}%`, background: confColor }}
            />
          </div>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', minWidth: 28 }}>
            {stats.avg_ai_confidence.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Sightings Today */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">Sightings Today</span>
          <span style={{ fontSize: 18 }}>👁️</span>
        </div>
        <div
          style={{
            fontSize: 32,
            fontWeight: 700,
            color: 'var(--text-primary)',
            lineHeight: 1,
            marginBottom: 10,
          }}
        >
          {stats.sightings_today}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {Object.entries(stats.sightings_by_species).map(([sp, cnt]) => (
            <div
              key={sp}
              style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}
            >
              <span style={{ color: 'var(--text-secondary)' }}>{sp}</span>
              <span style={{ color: 'var(--accent-blue)', fontWeight: 700 }}>{cnt}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Response Teams */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">Response Teams</span>
          <span style={{ fontSize: 18 }}>🛡️</span>
        </div>
        <div
          style={{
            fontSize: 32,
            fontWeight: 700,
            color: 'var(--accent-green)',
            lineHeight: 1,
            marginBottom: 10,
          }}
        >
          {stats.response_teams_available}
          <span
            style={{ fontSize: 16, color: 'var(--text-muted)', fontWeight: 400 }}
          >
            /{stats.response_teams_total}
          </span>
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          Available · {stats.pending_approvals} approval
          {stats.pending_approvals !== 1 ? 's' : ''} pending
        </div>
        {stats.pending_approvals > 0 && (
          <div style={{ marginTop: 6 }}>
            <span className="badge badge-ai">⏳ NEEDS REVIEW</span>
          </div>
        )}
      </div>
    </div>
  );
}
