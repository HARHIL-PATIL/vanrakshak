import { useState, useRef } from 'react';
import { runDemo } from '../../api/client';
import type { DemoStep, DemoStepStatus } from '../../types';

// ─── Fallback demo steps ──────────────────────────────────────────────────────

const DEMO_STEPS_TEMPLATE: Omit<DemoStep, 'status' | 'timestamp'>[] = [
  {
    step: 1,
    icon: '🦁',
    title: 'Wildlife sighting reported',
    description: 'Forest guard Ramesh Patel reports an Asiatic Lion sighting near Maldhari settlement, Sasan Gir area at 08:15 AM.',
    agent: undefined,
    data: { sighting_id: 'S-001', species: 'Asiatic Lion', location: 'Sasan Gir Sector 7', reported_by: 'Forest Guard Ramesh Patel', time: '08:15 AM' },
  },
  {
    step: 2,
    icon: '✅',
    title: 'System validates report',
    description: 'Sighting Validation Agent cross-checks report against known patrol schedules, camera trap data, and historical records.',
    agent: 'Agent 1: SightingValidator',
    data: { validated: true, cross_references: 3, confidence: 0.91 },
  },
  {
    step: 3,
    icon: '📊',
    title: 'Historical sightings checked',
    description: '47 prior sightings in this sector retrieved. Lion is a known adult male (tagged M-07) with established territory overlapping this settlement.',
    agent: 'Agent 1: SightingValidator',
    data: { prior_sightings: 47, known_animal: 'Male Lion M-07', territory_overlap: true },
  },
  {
    step: 4,
    icon: '📍',
    title: 'Distance from settlement calculated',
    description: 'Geospatial analysis estimates 1.8 km from nearest Maldhari colony. Livestock grazing area at 0.6 km.',
    agent: 'Agent 2: RiskAssessor',
    data: { distance_settlement_km: 1.8, distance_livestock_km: 0.6, sector: '7-B' },
  },
  {
    step: 5,
    icon: '⚖️',
    title: 'Conflict risk score calculated',
    description: 'Risk Assessor applies proximity multiplier (1.4x), seasonal factor (monsoon: 1.2x), and historical conflict rate. Final risk: HIGH.',
    agent: 'Agent 2: RiskAssessor',
    data: { base_score: 0.55, proximity_multiplier: 1.4, seasonal_factor: 1.2, final_risk_score: 0.87, classification: 'HIGH' },
  },
  {
    step: 6,
    icon: '🤖',
    title: 'Movement Prediction Agent activates',
    description: 'Agent predicts 73% probability of lion approaching settlement within 4 hours based on weather and livestock movement patterns.',
    agent: 'Agent 2: RiskAssessor',
    data: { prediction_confidence: 0.73, time_window_hours: 4, recommended_action: 'IMMEDIATE_RESPONSE' },
  },
  {
    step: 7,
    icon: '📢',
    title: 'Alert Agent generates bilingual warning',
    description: 'Alert Broadcaster generates English + Gujarati village warning with safety action checklist. SMS broadcast to 247 households.',
    agent: 'Agent 3: AlertBroadcaster',
    data: {
      alert_id: 'alert-001',
      languages: ['English', 'Gujarati'],
      households_notified: 247,
      message_preview: '⚠️ HIGH RISK: Asiatic Lion sighted 1.8km from Sasan Gir...',
      gujarati_preview: '⚠️ ઉચ્ચ જોખમ: સાસણ ગીર નજીક સિંહ જોવા મળ્યો...',
    },
  },
  {
    step: 8,
    icon: '🎫',
    title: 'Response Agent creates incident ticket',
    description: 'Incident Orchestrator creates ticket INC-001, assigns Rapid Response Team Alpha, requests officer approval before field dispatch.',
    agent: 'Agent 4: IncidentOrchestrator',
    data: {
      incident_id: 'INC-001',
      status: 'NEW',
      assigned_team: 'Rapid Response Team Alpha',
      personnel: 4,
      vehicles: 1,
      pending_approval: true,
    },
  },
  {
    step: 9,
    icon: '🗺️',
    title: 'Dashboard highlights risk zone',
    description: 'Command center dashboard updates in real-time. Sasan Gir sector turns HIGH (red) on the village risk map. All operators notified.',
    agent: undefined,
    data: { map_updated: true, sector_risk: 'HIGH', dashboard_alert: true, color: '#ff3b3b' },
  },
  {
    step: 10,
    icon: '👮',
    title: 'Officer reviews AI recommendation',
    description: 'Forest Officer Mehra receives push notification on dashboard. Reviews incident INC-001, risk score 0.87, and recommended team dispatch.',
    agent: undefined,
    data: {
      officer: 'Officer Mehra',
      review_time_seconds: 45,
      risk_score_shown: 0.87,
      recommendation: 'Dispatch Rapid Response Team Alpha — 4 personnel',
    },
  },
  {
    step: 11,
    icon: '✔️',
    title: 'Officer approves action',
    description: 'Officer Mehra approves dispatch. System records officer approval with timestamp. Team dispatch authorized — AI recommendation confirmed.',
    agent: 'Agent 4: IncidentOrchestrator',
    data: {
      approved_by: 'Officer Mehra (Badge: FR-2847)',
      approval_time: '08:22 AM',
      incident_status: 'ASSIGNED',
      team_dispatched: 'Rapid Response Team Alpha',
      note: 'AI CANNOT approve — human officer required',
    },
  },
  {
    step: 12,
    icon: '📡',
    title: 'Response status tracked',
    description: 'Incident status pipeline: NEW → ASSIGNED → IN PROGRESS. Team en route. Real-time updates broadcast to dashboard and village watch posts.',
    agent: 'Agent 4: IncidentOrchestrator',
    data: { pipeline_stage: 'IN_PROGRESS', eta_minutes: 18, status_updates: ['Team dispatched 08:22', 'En route 08:23', 'Arrival ETA 08:40'] },
  },
  {
    step: 13,
    icon: '📚',
    title: 'Incident becomes training data',
    description: 'After resolution, incident logs feed back into the AI model. Risk patterns updated. Future predictions for Sector 7 improved.',
    agent: 'Agent 5: CompensationGuide',
    data: {
      feedback_loop: true,
      data_points_added: 12,
      model_update_scheduled: 'nightly',
      sector_7_risk_updated: true,
      compensation_checklist_generated: true,
    },
  },
];

const STEP_DELAY_MS = 1200;

type StepWithStatus = DemoStep;

function initSteps(): StepWithStatus[] {
  return DEMO_STEPS_TEMPLATE.map((s) => ({ ...s, status: 'PENDING' as DemoStepStatus }));
}

export default function DemoPage() {
  const [steps, setSteps] = useState<StepWithStatus[]>(initSteps);
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const abortRef = useRef(false);

  async function runDemoAnimation() {
    abortRef.current = false;
    setRunning(true);
    setCompleted(false);
    setCurrentStep(-1);
    setSteps(initSteps());

    // Try to trigger backend
    runDemo().catch(() => {});

    for (let i = 0; i < DEMO_STEPS_TEMPLATE.length; i++) {
      if (abortRef.current) break;

      setCurrentStep(i);
      setSteps((prev) =>
        prev.map((s, idx) => ({
          ...s,
          status:
            idx < i
              ? 'COMPLETE'
              : idx === i
              ? 'RUNNING'
              : 'PENDING',
          timestamp: idx === i ? new Date().toISOString() : s.timestamp,
        }))
      );

      // Step 10 (officer review) gets a longer pause to simulate "waiting"
      const delay =
        i === 9
          ? STEP_DELAY_MS * 2.5
          : i === 10
          ? STEP_DELAY_MS * 1.8
          : STEP_DELAY_MS;

      await new Promise((res) => setTimeout(res, delay));
    }

    if (!abortRef.current) {
      setSteps((prev) =>
        prev.map((s) => ({
          ...s,
          status: 'COMPLETE',
        }))
      );
      setCurrentStep(DEMO_STEPS_TEMPLATE.length);
      setCompleted(true);
    }
    setRunning(false);
  }

  function resetDemo() {
    abortRef.current = true;
    setRunning(false);
    setCompleted(false);
    setCurrentStep(-1);
    setSteps(initSteps());
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🎬 End-to-End Demo Scenario</div>
          <div className="page-subtitle">
            PREDICT → ALERT → COORDINATE → LEARN · Simulated agent workflow visualization
          </div>
        </div>
      </div>

      {/* Demo control bar */}
      <div
        className="card mb-16"
        style={{ padding: '14px 18px' }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12,
          }}
        >
          <div>
            <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)', marginBottom: 4 }}>
              Simulated Scenario: Asiatic Lion sighting near Sasan Gir
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              08:15 AM — Maldhari settlement area · All 5 agents activated · Officer approval required
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            {!running && !completed && (
              <button className="btn btn-primary" onClick={runDemoAnimation}>
                ▶ Run Demo
              </button>
            )}
            {running && (
              <button className="btn btn-danger" onClick={resetDemo}>
                ⏹ Stop
              </button>
            )}
            {completed && (
              <>
                <span style={{ color: 'var(--accent-green)', fontWeight: 700, fontSize: 13 }}>
                  ✅ Demo Complete!
                </span>
                <button className="btn btn-secondary" onClick={resetDemo}>
                  🔄 Reset
                </button>
              </>
            )}
          </div>
        </div>

        {/* Progress bar */}
        {(running || completed) && (
          <div style={{ marginTop: 12 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 11,
                color: 'var(--text-muted)',
                marginBottom: 4,
              }}
            >
              <span>Progress</span>
              <span>
                {Math.min(currentStep + 1, DEMO_STEPS_TEMPLATE.length)} / {DEMO_STEPS_TEMPLATE.length} steps
              </span>
            </div>
            <div
              style={{
                height: 4,
                background: 'var(--border)',
                borderRadius: 2,
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  background: completed ? 'var(--accent-green)' : 'var(--accent-blue)',
                  borderRadius: 2,
                  transition: 'width 0.4s',
                  width: `${(Math.min(currentStep + 1, DEMO_STEPS_TEMPLATE.length) / DEMO_STEPS_TEMPLATE.length) * 100}%`,
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Workflow phases */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {[
          { label: '🔍 PREDICT', steps: [1, 2, 3, 4, 5, 6], color: 'var(--accent-blue)' },
          { label: '📢 ALERT', steps: [7, 8], color: 'var(--accent-orange)' },
          { label: '🛡️ COORDINATE', steps: [9, 10, 11, 12], color: 'var(--accent-red)' },
          { label: '📚 LEARN', steps: [13], color: 'var(--accent-green)' },
        ].map((phase) => {
          const doneCount = steps.filter(
            (s) => phase.steps.includes(s.step) && s.status === 'COMPLETE'
          ).length;
          return (
            <div
              key={phase.label}
              style={{
                padding: '6px 14px',
                background: 'var(--bg-card)',
                border: `1px solid ${phase.color}`,
                borderRadius: 4,
                fontSize: 11,
                fontWeight: 700,
                color: phase.color,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              {phase.label}
              <span
                style={{
                  background: `${phase.color}20`,
                  padding: '1px 6px',
                  borderRadius: 2,
                  fontSize: 10,
                }}
              >
                {doneCount}/{phase.steps.length}
              </span>
            </div>
          );
        })}
      </div>

      {/* Step timeline */}
      <div className="demo-timeline">
        {steps.map((step) => (
          <DemoStepCard key={step.step} step={step} />
        ))}
      </div>

      {/* Completion summary */}
      {completed && (
        <div
          className="card mt-16"
          style={{ borderLeft: '4px solid var(--accent-green)', padding: '16px 18px' }}
        >
          <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--accent-green)', marginBottom: 8 }}>
            ✅ Demo Scenario Complete — Full Workflow Executed
          </div>
          <div className="grid-4" style={{ gap: 12 }}>
            {[
              { label: 'Risk Score', value: '0.87 (HIGH)', color: 'var(--accent-red)' },
              { label: 'Agents Activated', value: '4 of 5', color: 'var(--accent-purple)' },
              { label: 'Households Alerted', value: '247', color: 'var(--accent-orange)' },
              { label: 'Officer Decision', value: 'APPROVED', color: 'var(--accent-green)' },
            ].map((stat) => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: stat.color, fontFamily: 'monospace' }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
          <div className="notice-box warning mt-12">
            <span>⚠️</span>
            <span>
              This is a <strong>simulated demonstration</strong>. All data, alerts, and AI outputs shown
              are fictional and for demo purposes only.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function DemoStepCard({ step }: { step: StepWithStatus }) {
  const isPending = step.status === 'PENDING';
  const isRunning = step.status === 'RUNNING';
  const isComplete = step.status === 'COMPLETE';
  const isWaiting = step.status === 'WAITING_FOR_OFFICER';

  // Steps 10-11 get "waiting for officer" visual treatment
  const effectiveStatus =
    step.status === 'RUNNING' && (step.step === 10 || step.step === 11)
      ? 'WAITING_FOR_OFFICER'
      : step.status;

  const iconCls =
    effectiveStatus === 'WAITING_FOR_OFFICER'
      ? 'waiting'
      : isRunning
      ? 'running'
      : isComplete
      ? 'complete'
      : '';

  return (
    <div className="demo-step">
      <div className={`demo-step-icon ${iconCls}`}>{step.icon}</div>
      <div
        className={`demo-step-body ${
          effectiveStatus === 'WAITING_FOR_OFFICER'
            ? 'waiting'
            : isRunning
            ? 'running'
            : isComplete
            ? 'complete'
            : ''
        }`}
        style={{ opacity: isPending ? 0.45 : 1 }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 6, marginBottom: 4 }}>
          <div>
            <span style={{ fontFamily: 'monospace', fontSize: 10, color: 'var(--text-muted)', marginRight: 8 }}>
              STEP {step.step}
            </span>
            <span className="demo-step-title">{step.title}</span>
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            {step.agent && (
              <span
                style={{
                  fontSize: 9,
                  padding: '2px 6px',
                  background: 'var(--accent-purple-dim)',
                  border: '1px solid var(--accent-purple)',
                  color: 'var(--accent-purple)',
                  borderRadius: 3,
                  fontWeight: 700,
                }}
              >
                {step.agent}
              </span>
            )}
            <StepStatusBadge status={effectiveStatus as DemoStepStatus} />
            {step.timestamp && isComplete && (
              <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>
                {new Date(step.timestamp).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        <div className="demo-step-desc">{step.description}</div>

        {/* Data snippet */}
        {(isComplete || isRunning || isWaiting) && step.data && (
          <div className="demo-step-data">
            {JSON.stringify(step.data, null, 2)}
          </div>
        )}
      </div>
    </div>
  );
}

function StepStatusBadge({ status }: { status: DemoStepStatus }) {
  const config: Record<DemoStepStatus, { cls: string; label: string }> = {
    PENDING: { cls: '', label: 'PENDING' },
    RUNNING: { cls: 'badge-new', label: '⟳ RUNNING' },
    COMPLETE: { cls: 'badge-resolved', label: '✓ COMPLETE' },
    WAITING_FOR_OFFICER: { cls: 'badge-waiting', label: '👮 OFFICER REVIEW' },
  };
  const c = config[status] ?? config.PENDING;
  return (
    <span
      className={`badge ${c.cls}`}
      style={{ fontSize: 9, opacity: status === 'PENDING' ? 0.4 : 1 }}
    >
      {c.label}
    </span>
  );
}
