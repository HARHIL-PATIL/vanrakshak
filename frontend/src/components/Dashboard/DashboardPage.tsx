import { getDashboard } from '../../api/client';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../Common/LoadingSpinner';
import StatsCards from './StatsCards';
import RiskMap from './RiskMap';
import ActiveIncidents from './ActiveIncidents';
import RecentSightings from './RecentSightings';
import AgentStatusBar from './AgentStatusBar';

export default function DashboardPage() {
  const { data, loading } = useApi(getDashboard, [], { refreshInterval: 30000 });

  if (loading && !data) {
    return <LoadingSpinner label="Loading command center data..." />;
  }

  const d = data!;

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <div className="page-title">🏠 Command Center Dashboard</div>
            <div className="page-subtitle">
              Real-time wildlife conflict monitoring · Gir Forest Region
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span className="demo-data-label">DEMO DATA</span>
            <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              Auto-refresh 30s · Last: {new Date(d.last_updated).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <StatsCards stats={d.stats} />

      {/* Main Grid: Risk Map + Incidents + Sightings */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '3fr 2fr',
          gap: 16,
          marginBottom: 16,
        }}
      >
        {/* Left col: Map + Sightings */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <RiskMap />
          <RecentSightings sightings={d.sightings} />
        </div>

        {/* Right col: Incidents */}
        <div>
          <ActiveIncidents incidents={d.incidents} />
        </div>
      </div>

      {/* Agent Status Bar */}
      <AgentStatusBar agents={d.agents} pendingApprovals={d.stats.pending_approvals} />

      {/* Disclaimer */}
      <div className="notice-box warning mt-16">
        <span>⚠️</span>
        <span>
          <strong>DEMONSTRATION SYSTEM</strong> — This dashboard displays sample/simulated data
          for demonstration purposes only. All data, alerts, incidents, and AI recommendations
          shown here are <strong>NOT real</strong> and should not be used for actual wildlife
          management decisions.
        </span>
      </div>
    </div>
  );
}
