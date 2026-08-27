import type { Sighting } from '../../types';
import RiskBadge from '../Common/RiskBadge';

interface RecentSightingsProps {
  sightings: Sighting[];
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function RecentSightings({ sightings }: RecentSightingsProps) {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Recent Sightings</span>
        <span className="demo-data-label">DEMO DATA</span>
      </div>

      {sightings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <div>No recent sightings</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {sightings.slice(0, 5).map((s) => (
            <div
              key={s.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
                padding: '8px 10px',
                background: 'var(--bg-elevated)',
                borderRadius: 4,
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
                  <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                    🦁 {s.species}
                  </span>
                  <RiskBadge level={s.risk_level} size="sm" />
                  {s.verified && (
                    <span
                      style={{
                        fontSize: 9,
                        color: 'var(--accent-green)',
                        fontWeight: 700,
                      }}
                    >
                      ✓ VERIFIED
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  📍 {s.village} · {s.distance_km} km from settlement
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
                  {s.reported_by}
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 600 }}>
                  {timeAgo(s.timestamp)}
                </div>
                <div
                  style={{ fontSize: 11, color: 'var(--accent-blue)', fontFamily: 'monospace' }}
                >
                  {(s.confidence * 100).toFixed(0)}% conf
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
