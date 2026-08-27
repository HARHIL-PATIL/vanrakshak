import { getAgentStatus } from '../../api/client';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../Common/LoadingSpinner';
import type { AgentInfo } from '../../types';

const STATUS_COLOR: Record<string, string> = {
  ACTIVE: 'var(--accent-green)',
  IDLE: 'var(--accent-blue)',
  ERROR: 'var(--accent-red)',
  WAITING: 'var(--accent-yellow)',
};

function AgentCard({ agent }: { agent: AgentInfo }) {
  const color = STATUS_COLOR[agent.status] ?? 'var(--text-muted)';
  const statusCls = agent.status.toLowerCase();

  return (
    <div className={`agent-card ${statusCls}`}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div className="agent-number">Agent {agent.agent_number}</div>
          <div className="agent-name">{agent.name}</div>
          <div className="agent-full-name">{agent.full_name}</div>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            padding: '3px 9px',
            background: `${color}20`,
            border: `1px solid ${color}`,
            borderRadius: 3,
            fontSize: 10,
            fontWeight: 700,
            color,
            whiteSpace: 'nowrap',
          }}
        >
          <div
            style={{ width: 6, height: 6, borderRadius: '50%', background: color }}
          />
          {agent.status}
        </div>
      </div>

      {/* Latest Action */}
      <div className="agent-action">{agent.latest_action}</div>

      {/* Confidence */}
      <div style={{ margin: '8px 0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Confidence</span>
          <span style={{ fontSize: 11, fontFamily: 'monospace', color }}>
            {agent.confidence.toFixed(2)}
          </span>
        </div>
        <div className="confidence-bar">
          <div
            className="confidence-bar-fill"
            style={{ width: `${agent.confidence * 100}%`, background: color }}
          />
        </div>
      </div>

      {/* Escalation */}
      {agent.escalation_required && (
        <div style={{ marginBottom: 8 }}>
          <span className="badge badge-waiting" style={{ fontSize: 9 }}>
            ⚡ ESCALATION REQUIRED — Awaiting Officer
          </span>
        </div>
      )}

      {/* Action log */}
      <div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 6 }}>
          Recent Actions
        </div>
        {agent.action_log.slice(0, 3).map((entry, i) => (
          <div key={i} className="agent-log-entry">
            <span>{entry}</span>
          </div>
        ))}
      </div>

      {/* Timestamp */}
      <div style={{ marginTop: 8, fontSize: 10, color: 'var(--text-muted)', textAlign: 'right' }}>
        Last active: {new Date(agent.last_active).toLocaleTimeString()}
      </div>
    </div>
  );
}

export default function AgentsPage() {
  const { data, loading } = useApi(getAgentStatus, [], { refreshInterval: 15000 });

  if (loading && !data) {
    return <LoadingSpinner label="Loading agent status..." />;
  }

  const { agents, orchestrator } = data!;

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="page-title">🤖 Agent Monitoring Panel</div>
            <div className="page-subtitle">
              Real-time status of all 5 AI agents + Central Orchestrator · Auto-refresh 15s
            </div>
          </div>
          <span className="demo-data-label">DEMO DATA</span>
        </div>
      </div>

      {/* Orchestrator */}
      <div
        className="card mb-16"
        style={{ borderLeft: '4px solid var(--accent-purple)' }}
      >
        <div className="card-header">
          <span className="card-title-main">🎛️ Central Orchestrator</span>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '3px 9px',
                background:
                  orchestrator.status === 'ACTIVE'
                    ? 'var(--accent-green-dim)'
                    : 'var(--accent-yellow-dim)',
                border: `1px solid ${
                  orchestrator.status === 'ACTIVE'
                    ? 'var(--accent-green)'
                    : 'var(--accent-yellow)'
                }`,
                borderRadius: 3,
                fontSize: 10,
                fontWeight: 700,
                color:
                  orchestrator.status === 'ACTIVE'
                    ? 'var(--accent-green)'
                    : 'var(--accent-yellow)',
              }}
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background:
                    orchestrator.status === 'ACTIVE'
                      ? 'var(--accent-green)'
                      : 'var(--accent-yellow)',
                }}
              />
              {orchestrator.status}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
          <OrchestratorStat
            label="Active Workflows"
            value={String(orchestrator.active_workflows)}
            color="var(--accent-blue)"
          />
          <OrchestratorStat
            label="Pending Approvals"
            value={String(orchestrator.pending_approvals)}
            color={
              orchestrator.pending_approvals > 0
                ? 'var(--accent-orange)'
                : 'var(--text-secondary)'
            }
          />
          <OrchestratorStat
            label="Active Agents"
            value={String(agents.filter((a) => a.status === 'ACTIVE').length)}
            color="var(--accent-green)"
          />
          <OrchestratorStat
            label="Last Updated"
            value={new Date(orchestrator.last_updated).toLocaleTimeString()}
            color="var(--text-muted)"
          />
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid-3 mb-16" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
        {agents.map((agent) => (
          <AgentCard key={agent.agent_id} agent={agent} />
        ))}
      </div>

      {/* IBM Technology Notes */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">🔷 IBM Technology Integration Notes</span>
          <span className="badge badge-ai">ARCHITECTURE</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <TechNote
            icon="🤖"
            title="IBM Granite LLM"
            status="PROPOSED INTEGRATION"
            statusColor="var(--accent-orange)"
            desc="Template generation and bilingual alert composition used in prototype. Full integration planned for production deployment via IBM watsonx.ai platform."
          />
          <TechNote
            icon="☁️"
            title="IBM Cloud"
            status="ARCHITECTURE READY"
            statusColor="var(--accent-blue)"
            desc="Infrastructure blueprint designed for IBM Cloud deployment. Kubernetes-based microservices with IBM Cloud Object Storage for media and IBM Event Streams for real-time agent messaging."
          />
          <TechNote
            icon="🔮"
            title="IBM Watson Assistant"
            status="PLANNED"
            statusColor="var(--text-muted)"
            desc="Village-facing conversational interface for sighting reporting in Gujarati via SMS and WhatsApp bridge — planned for Phase 2."
          />
        </div>
      </div>
    </div>
  );
}

function OrchestratorStat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color, fontFamily: 'monospace' }}>{value}</div>
    </div>
  );
}

function TechNote({
  icon,
  title,
  status,
  statusColor,
  desc,
}: {
  icon: string;
  title: string;
  status: string;
  statusColor: string;
  desc: string;
}) {
  return (
    <div
      style={{
        display: 'flex',
        gap: 12,
        padding: '10px 12px',
        background: 'var(--bg-elevated)',
        borderRadius: 4,
        alignItems: 'flex-start',
      }}
    >
      <span style={{ fontSize: 18 }}>{icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <span style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>
            {title}
          </span>
          <span
            style={{
              fontSize: 9,
              fontWeight: 700,
              letterSpacing: '0.8px',
              color: statusColor,
              textTransform: 'uppercase',
            }}
          >
            — {status}
          </span>
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>{desc}</div>
      </div>
    </div>
  );
}
