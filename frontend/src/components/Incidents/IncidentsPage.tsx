import { useState } from 'react';
import { getIncidents, approveAction, updateIncidentStatus } from '../../api/client';
import { useApi } from '../../hooks/useApi';
import type { Incident, IncidentStatus } from '../../types';
import RiskBadge from '../Common/RiskBadge';
import StatusBadge from '../Common/StatusBadge';
import LoadingSpinner from '../Common/LoadingSpinner';

type Filter = 'ALL' | IncidentStatus;

const PIPELINE: IncidentStatus[] = ['NEW', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED'];

function Pipeline({ current }: { current: IncidentStatus }) {
  const steps = PIPELINE;
  const currentIdx = steps.indexOf(current);

  return (
    <div className="pipeline">
      {steps.map((step, i) => {
        const isDone = i < currentIdx;
        const isCurrent = i === currentIdx;
        const isEscalated = current === 'ESCALATED';
        return (
          <span key={step}>
            <span
              className={`pipeline-step${isCurrent || (isEscalated && step === 'NEW') ? ' active' : ''}${isDone ? ' done' : ''}`}
            >
              {step.replace('_', ' ')}
            </span>
            {i < steps.length - 1 && <span className="pipeline-arrow">→</span>}
          </span>
        );
      })}
      {current === 'ESCALATED' && (
        <>
          <span className="pipeline-arrow">→</span>
          <span className="pipeline-step active" style={{ borderColor: 'var(--accent-red)', color: 'var(--accent-red)' }}>
            ⚡ ESCALATED
          </span>
        </>
      )}
    </div>
  );
}

export default function IncidentsPage() {
  const [filter, setFilter] = useState<Filter>('ALL');
  const [acting, setActing] = useState<string | null>(null);
  const { data: incidents, loading, refetch } = useApi(getIncidents, []);

  const filtered = !incidents ? [] :
    filter === 'ALL' ? incidents : incidents.filter((i) => i.status === filter);

  const counts = incidents
    ? (['NEW', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'ESCALATED'] as IncidentStatus[]).reduce(
        (acc, s) => ({ ...acc, [s]: incidents.filter((i) => i.status === s).length }),
        {} as Record<IncidentStatus, number>
      )
    : ({} as Record<IncidentStatus, number>);

  async function handleAction(incident: Incident, action: 'APPROVE' | 'OVERRIDE' | 'RESOLVE') {
    setActing(incident.id);
    try {
      if (action === 'RESOLVE') {
        await updateIncidentStatus(incident.id, 'RESOLVED');
      } else {
        await approveAction({
          request_id: incident.id,
          action,
          officer_id: 'OFFICER_DEMO',
        });
      }
      refetch();
    } catch {
      refetch();
    } finally {
      setActing(null);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="page-title">📋 Incident Management</div>
            <div className="page-subtitle">
              All wildlife conflict incidents with status pipeline · Officer action required for dispatch
            </div>
          </div>
          <span className="demo-data-label">DEMO DATA</span>
        </div>
      </div>

      {/* Status Filter */}
      <div className="filter-tabs mb-16">
        <button
          className={`filter-tab${filter === 'ALL' ? ' active' : ''}`}
          onClick={() => setFilter('ALL')}
        >
          ALL ({incidents?.length ?? 0})
        </button>
        {(['NEW', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'ESCALATED'] as IncidentStatus[]).map(
          (s) => (
            <button
              key={s}
              className={`filter-tab${filter === s ? ' active' : ''}`}
              onClick={() => setFilter(s)}
            >
              {s.replace('_', ' ')} ({counts[s] ?? 0})
            </button>
          )
        )}
      </div>

      {/* Pipeline Legend */}
      <div
        className="card mb-16"
        style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 12 }}
      >
        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>
          STATUS PIPELINE:
        </span>
        <Pipeline current={'IN_PROGRESS'} />
      </div>

      {loading && !incidents ? (
        <LoadingSpinner label="Loading incidents..." />
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">✅</div>
          <div>No incidents in this status</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {filtered.map((inc) => (
            <IncidentCard
              key={inc.id}
              incident={inc}
              acting={acting}
              onAction={handleAction}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function IncidentCard({
  incident,
  acting,
  onAction,
}: {
  incident: Incident;
  acting: string | null;
  onAction: (i: Incident, action: 'APPROVE' | 'OVERRIDE' | 'RESOLVE') => void;
}) {
  const riskColor =
    incident.risk_score >= 0.7
      ? 'var(--accent-red)'
      : incident.risk_score >= 0.4
      ? 'var(--accent-orange)'
      : 'var(--accent-green)';

  return (
    <div
      className="card"
      style={{
        borderLeft: `4px solid ${
          incident.severity === 'HIGH'
            ? 'var(--accent-red)'
            : incident.severity === 'MEDIUM'
            ? 'var(--accent-orange)'
            : 'var(--accent-green)'
        }`,
        padding: '14px 16px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8 }}>
        {/* Left: ID + badges + species + village */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
            <span
              style={{
                fontFamily: 'monospace',
                fontSize: 13,
                fontWeight: 700,
                color: 'var(--accent-blue)',
              }}
            >
              {incident.display_id}
            </span>
            <RiskBadge level={incident.severity} />
            <StatusBadge status={incident.status} />
            {incident.pending_approval && (
              <span className="badge badge-ai">⚡ OFFICER APPROVAL REQUIRED</span>
            )}
          </div>

          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', marginBottom: 6 }}>
            <IncidentMeta icon="🦁" value={incident.species} />
            <IncidentMeta icon="📍" value={incident.village} />
            {incident.recommended_team && (
              <IncidentMeta icon="🛡️" value={incident.recommended_team} />
            )}
            {incident.assigned_officer && (
              <IncidentMeta icon="👮" value={incident.assigned_officer} />
            )}
          </div>

          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
            {incident.description}
          </div>

          <Pipeline current={incident.status} />
        </div>

        {/* Right: risk score + timestamp */}
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div
            style={{ fontSize: 24, fontWeight: 800, color: riskColor, fontFamily: 'monospace' }}
          >
            {incident.risk_score.toFixed(2)}
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Risk Score</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
            {new Date(incident.timestamp).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div
        style={{
          marginTop: 12,
          paddingTop: 10,
          borderTop: '1px solid var(--border)',
          display: 'flex',
          gap: 8,
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        {incident.pending_approval && incident.status !== 'RESOLVED' && (
          <>
            <button
              className="btn btn-success btn-sm"
              disabled={acting === incident.id}
              onClick={() => onAction(incident, 'APPROVE')}
            >
              {acting === incident.id ? '...' : '✓ Approve Dispatch'}
            </button>
            <button
              className="btn btn-danger btn-sm"
              disabled={acting === incident.id}
              onClick={() => onAction(incident, 'OVERRIDE')}
            >
              ⚡ Override
            </button>
          </>
        )}
        {incident.status !== 'RESOLVED' && (
          <button
            className="btn btn-secondary btn-sm"
            disabled={acting === incident.id}
            onClick={() => onAction(incident, 'RESOLVE')}
          >
            Mark Resolved
          </button>
        )}
        {incident.status === 'RESOLVED' && (
          <span style={{ fontSize: 12, color: 'var(--accent-green)' }}>
            ✅ Incident Resolved
          </span>
        )}
      </div>
    </div>
  );
}

function IncidentMeta({ icon, value }: { icon: string; value: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12 }}>
      <span>{icon}</span>
      <span style={{ color: 'var(--text-secondary)' }}>{value}</span>
    </div>
  );
}
