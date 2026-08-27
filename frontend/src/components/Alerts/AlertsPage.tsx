import { useState } from 'react';
import { getAlerts, approveAction } from '../../api/client';
import { useApi } from '../../hooks/useApi';
import type { Alert, RiskLevel } from '../../types';
import RiskBadge from '../Common/RiskBadge';
import LoadingSpinner from '../Common/LoadingSpinner';

type Filter = 'ALL' | RiskLevel;

export default function AlertsPage() {
  const [filter, setFilter] = useState<Filter>('ALL');
  const [approving, setApproving] = useState<string | null>(null);
  const { data: alerts, loading, refetch } = useApi(getAlerts, []);

  const filtered =
    !alerts ? [] :
    filter === 'ALL' ? alerts : alerts.filter((a) => a.risk_level === filter);

  async function handleApprove(alert: Alert, action: 'APPROVE' | 'OVERRIDE') {
    setApproving(alert.id);
    try {
      await approveAction({
        request_id: alert.id,
        action,
        officer_id: 'OFFICER_DEMO',
        notes: action === 'OVERRIDE' ? 'Manual override by demo officer' : undefined,
      });
      refetch();
    } catch {
      // fallback: just refetch
      refetch();
    } finally {
      setApproving(null);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="page-title">⚠️ Wildlife Alerts</div>
            <div className="page-subtitle">
              AI-generated bilingual alerts for village communities · Pending officer review
            </div>
          </div>
          <span className="demo-data-label">DEMO DATA</span>
        </div>
      </div>

      {/* Filters */}
      <div className="filter-tabs mb-16">
        {(['ALL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((f) => (
          <button
            key={f}
            className={`filter-tab${filter === f ? ' active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'ALL' ? 'ALL ALERTS' : f}
            {f !== 'ALL' && alerts && (
              <span style={{ marginLeft: 5, opacity: 0.7 }}>
                ({alerts.filter((a) => a.risk_level === f).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {loading && !alerts ? (
        <LoadingSpinner label="Fetching alerts..." />
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">✅</div>
          <div style={{ color: 'var(--accent-green)', fontWeight: 600 }}>
            No active alerts — All systems nominal
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {filtered.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              approving={approving}
              onApprove={handleApprove}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function AlertCard({
  alert,
  approving,
  onApprove,
}: {
  alert: Alert;
  approving: string | null;
  onApprove: (a: Alert, action: 'APPROVE' | 'OVERRIDE') => void;
}) {
  const borderColor =
    alert.risk_level === 'HIGH'
      ? 'var(--accent-red)'
      : alert.risk_level === 'MEDIUM'
      ? 'var(--accent-orange)'
      : 'var(--accent-green)';

  return (
    <div
      className="card"
      style={{ borderLeft: `4px solid ${borderColor}`, padding: '16px 18px' }}
    >
      {/* Alert header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: 12,
          flexWrap: 'wrap',
          gap: 8,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <RiskBadge level={alert.risk_level} />
          <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>
            📍 {alert.village}
          </span>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            🦁 {alert.species}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          {alert.pending_review && (
            <span className="badge badge-ai">🤖 AI RECOMMENDATION — Pending Officer Review</span>
          )}
          {alert.officer_approved && (
            <span className="badge badge-resolved">✅ OFFICER APPROVED</span>
          )}
          {alert.officer_override && (
            <span className="badge badge-escalated">⚡ OFFICER OVERRIDE</span>
          )}
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {new Date(alert.timestamp).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Meta row */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 12, flexWrap: 'wrap' }}>
        <MetaTag label="Proximity" value={`~${alert.distance_km} km from settlement`} />
        <MetaTag
          label="AI Confidence"
          value={`${(alert.confidence * 100).toFixed(0)}%`}
          color={
            alert.confidence >= 0.8
              ? 'var(--accent-green)'
              : alert.confidence >= 0.6
              ? 'var(--accent-orange)'
              : 'var(--accent-red)'
          }
        />
        {alert.incident_id && (
          <MetaTag label="Incident" value={alert.incident_id.toUpperCase()} color="var(--accent-blue)" />
        )}
      </div>

      {/* English message */}
      <div
        style={{
          padding: '10px 12px',
          background: 'var(--bg-elevated)',
          borderRadius: 4,
          fontSize: 13,
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
          marginBottom: 10,
        }}
      >
        {alert.message_en}
      </div>

      {/* Gujarati message */}
      <div className="gujarati-text">{alert.message_gu}</div>

      {/* Safety actions */}
      <div style={{ marginTop: 12 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 8 }}>
          Safety Actions
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {alert.safety_actions.map((action, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: 8,
                fontSize: 12,
                color: 'var(--text-secondary)',
                alignItems: 'flex-start',
              }}
            >
              <span style={{ color: 'var(--accent-orange)', flexShrink: 0, fontWeight: 700 }}>
                {i + 1}.
              </span>
              {action}
            </div>
          ))}
        </div>
      </div>

      {/* Officer actions */}
      {alert.pending_review && !alert.officer_approved && (
        <div
          style={{
            marginTop: 14,
            paddingTop: 12,
            borderTop: '1px solid var(--border)',
            display: 'flex',
            gap: 10,
            alignItems: 'center',
          }}
        >
          <span style={{ fontSize: 11, color: 'var(--text-muted)', flex: 1 }}>
            👮 Officer Action Required:
          </span>
          <button
            className="btn btn-success btn-sm"
            disabled={approving === alert.id}
            onClick={() => onApprove(alert, 'APPROVE')}
          >
            {approving === alert.id ? '...' : '✓ Approve Dispatch'}
          </button>
          <button
            className="btn btn-danger btn-sm"
            disabled={approving === alert.id}
            onClick={() => onApprove(alert, 'OVERRIDE')}
          >
            ⚡ Override
          </button>
        </div>
      )}
    </div>
  );
}

function MetaTag({
  label,
  value,
  color = 'var(--text-primary)',
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div>
      <span style={{ fontSize: 10, color: 'var(--text-muted)', display: 'block', marginBottom: 1 }}>
        {label}
      </span>
      <span style={{ fontSize: 12, fontWeight: 600, color }}>{value}</span>
    </div>
  );
}
