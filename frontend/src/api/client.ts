import type {
  DashboardData,
  Alert,
  Incident,
  Sighting,
  AgentStatusResponse,
  CompensationClaim,
  CompensationChecklist,
  DemoScenario,
  StartCompensationRequest,
  ApproveRequest,
  SightingCreateRequest,
  LossType,
} from '../types';

const BASE_URL = '/api';

// ─── Fallback / Sample Data ───────────────────────────────────────────────────

export const FALLBACK_SIGHTINGS: Sighting[] = [
  {
    id: 'S-001',
    species: 'Asiatic Lion',
    location: 'Sector 7 — Near Maldhari settlement',
    village: 'Sasan Gir',
    distance_km: 1.8,
    confidence: 0.91,
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
    reported_by: 'Forest Guard Ramesh Patel',
    verified: true,
    risk_level: 'HIGH',
  },
  {
    id: 'S-002',
    species: 'Leopard',
    location: 'Agricultural fringe — Khambha road',
    village: 'Dhari',
    distance_km: 3.2,
    confidence: 0.78,
    timestamp: new Date(Date.now() - 90 * 60000).toISOString(),
    reported_by: 'Camera Trap CT-14',
    verified: true,
    risk_level: 'MEDIUM',
  },
  {
    id: 'S-003',
    species: 'Asiatic Lion',
    location: 'Deep forest interior — Block D',
    village: 'Mendarda',
    distance_km: 7.4,
    confidence: 0.85,
    timestamp: new Date(Date.now() - 180 * 60000).toISOString(),
    reported_by: 'Aerial Survey AS-2024',
    verified: true,
    risk_level: 'LOW',
  },
  {
    id: 'S-004',
    species: 'Striped Hyena',
    location: 'Cattle grazing boundary',
    village: 'Talala',
    distance_km: 0.9,
    confidence: 0.72,
    timestamp: new Date(Date.now() - 240 * 60000).toISOString(),
    reported_by: 'Village Watchman Bharat Singh',
    verified: false,
    risk_level: 'HIGH',
  },
  {
    id: 'S-005',
    species: 'Leopard',
    location: 'Riverbed — Hiran river crossing',
    village: 'Visavadar',
    distance_km: 4.1,
    confidence: 0.68,
    timestamp: new Date(Date.now() - 360 * 60000).toISOString(),
    reported_by: 'Camera Trap CT-07',
    verified: true,
    risk_level: 'MEDIUM',
  },
];

export const FALLBACK_INCIDENTS: Incident[] = [
  {
    id: 'inc-001',
    display_id: 'INC-001',
    village: 'Sasan Gir',
    species: 'Asiatic Lion',
    severity: 'HIGH',
    risk_score: 0.87,
    status: 'ASSIGNED',
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
    recommended_team: 'Rapid Response Team Alpha',
    assigned_officer: 'Officer Mehra',
    description: 'Lion sighted near livestock pen, Maldhari colony. Immediate response required.',
    pending_approval: false,
    sighting_id: 'S-001',
  },
  {
    id: 'inc-002',
    display_id: 'INC-002',
    village: 'Dhari',
    species: 'Leopard',
    severity: 'MEDIUM',
    risk_score: 0.63,
    status: 'NEW',
    timestamp: new Date(Date.now() - 95 * 60000).toISOString(),
    recommended_team: 'Patrol Unit B',
    description: 'Leopard photographed at agricultural boundary. Monitoring recommended.',
    pending_approval: true,
  },
  {
    id: 'inc-003',
    display_id: 'INC-003',
    village: 'Talala',
    species: 'Striped Hyena',
    severity: 'HIGH',
    risk_score: 0.79,
    status: 'IN_PROGRESS',
    timestamp: new Date(Date.now() - 250 * 60000).toISOString(),
    recommended_team: 'Rapid Response Team Beta',
    assigned_officer: 'Officer Singh',
    description: 'Hyena pack near cattle pen. Two calves reportedly missing.',
    pending_approval: false,
    sighting_id: 'S-004',
  },
  {
    id: 'inc-004',
    display_id: 'INC-004',
    village: 'Mendarda',
    species: 'Asiatic Lion',
    severity: 'LOW',
    risk_score: 0.32,
    status: 'RESOLVED',
    timestamp: new Date(Date.now() - 24 * 3600000).toISOString(),
    recommended_team: 'Monitoring Unit',
    assigned_officer: 'Officer Patel',
    description: 'Lion sighted deep in forest interior. No immediate threat. Logged for tracking.',
    pending_approval: false,
    sighting_id: 'S-003',
  },
  {
    id: 'inc-005',
    display_id: 'INC-005',
    village: 'Visavadar',
    species: 'Leopard',
    severity: 'MEDIUM',
    risk_score: 0.55,
    status: 'ESCALATED',
    timestamp: new Date(Date.now() - 6 * 3600000).toISOString(),
    recommended_team: 'Rapid Response Team Alpha',
    description: 'Leopard entered village outskirts. Villager reported close encounter.',
    pending_approval: false,
    sighting_id: 'S-005',
  },
  {
    id: 'inc-006',
    display_id: 'INC-006',
    village: 'Una',
    species: 'Crocodile',
    severity: 'MEDIUM',
    risk_score: 0.61,
    status: 'NEW',
    timestamp: new Date(Date.now() - 2 * 3600000).toISOString(),
    recommended_team: 'Reptile Response Unit',
    description: 'Large crocodile sighted near Shetrunji river bank used for bathing.',
    pending_approval: true,
  },
];

export const FALLBACK_ALERTS: Alert[] = [
  {
    id: 'alert-001',
    incident_id: 'inc-001',
    village: 'Sasan Gir',
    species: 'Asiatic Lion',
    risk_level: 'HIGH',
    distance_km: 1.8,
    confidence: 0.91,
    message_en:
      '⚠️ HIGH RISK ALERT: Asiatic Lion sighted approximately 1.8 km from Sasan Gir settlement. Livestock must be secured immediately. Do not venture outside after dark.',
    message_gu:
      '⚠️ ઉચ્ચ જોખમ ચેતવણી: સાસણ ગીર વસ્તીથી આશરે ૧.૮ કિ.મી. દૂર એશિયાઈ સિંહ જોવા મળ્યો છે. પશુઓને તાત્કાલિક સુરક્ષિત કરો. અંધારા પછી બહાર ન નીકળો.',
    safety_actions: [
      'Secure all livestock in reinforced enclosures immediately',
      'Alert neighboring households via community messaging',
      'Do not approach or attempt to chase the animal',
      'Contact Forest Department: 1926 or +91-2877-285541',
      'Remain indoors after sunset until further notice',
    ],
    timestamp: new Date(Date.now() - 20 * 60000).toISOString(),
    officer_approved: true,
    officer_override: false,
    pending_review: false,
  },
  {
    id: 'alert-002',
    incident_id: 'inc-002',
    village: 'Dhari',
    species: 'Leopard',
    risk_level: 'MEDIUM',
    distance_km: 3.2,
    confidence: 0.78,
    message_en:
      '⚡ MEDIUM RISK: Leopard detected at agricultural boundary near Dhari. Avoid the Khambha road fringe area after dusk. Forest patrol has been alerted.',
    message_gu:
      '⚡ મધ્યમ જોખમ: ધારી નજીક કૃષિ સીમા પર દીપડો જોવા મળ્યો. સૂર્યાસ્ત પછી ખંભા રોડ ફ્રિન્જ વિસ્તાર ટાળો. વન ગાર્ડ્સને ચેતવી દેવામાં આવ્યા છે.',
    safety_actions: [
      'Avoid the agricultural fringe area, especially Khambha road sector',
      'Keep children and elderly indoors after dusk',
      'Secure domestic animals overnight',
      'Report additional sightings to nearest forest post',
    ],
    timestamp: new Date(Date.now() - 85 * 60000).toISOString(),
    officer_approved: false,
    officer_override: false,
    pending_review: true,
  },
  {
    id: 'alert-003',
    incident_id: 'inc-003',
    village: 'Talala',
    species: 'Striped Hyena',
    risk_level: 'HIGH',
    distance_km: 0.9,
    confidence: 0.72,
    message_en:
      '🚨 CRITICAL: Hyena pack reported within 0.9 km of Talala. Missing livestock reported. Forest rapid response team dispatched. Please stay alert.',
    message_gu:
      '🚨 ગંભીર: ટાળા ગામ નજીક ૦.૯ કિ.મી.ની અંદર ઝરખ (hyena) ટોળું જોવા મળ્યું. ગૂમ થયેલ પશુઓ નોંધાયા. ઝડપી પ્રતિભાવ ટીમ મોકલવામાં આવી છે.',
    safety_actions: [
      'Do NOT venture near the boundary area',
      'Keep all livestock secured — hyenas are nocturnal predators',
      'Travel in groups with torchlight if movement required',
      'Report any missing or injured livestock to Forest Department immediately',
      'Emergency: 1926',
    ],
    timestamp: new Date(Date.now() - 245 * 60000).toISOString(),
    officer_approved: true,
    officer_override: false,
    pending_review: false,
  },
  {
    id: 'alert-004',
    incident_id: 'inc-005',
    village: 'Visavadar',
    species: 'Leopard',
    risk_level: 'MEDIUM',
    distance_km: 4.1,
    confidence: 0.68,
    message_en:
      '⚡ MEDIUM RISK: Leopard movement near Visavadar. Animal has been sighted near river crossing. Monitor situation.',
    message_gu:
      '⚡ મધ્યમ જોખમ: વિસાવદર નજીક દીપડાની હિલચાલ. નદી ક્રોસિંગ પર પ્રાણી જોવા મળ્યું. પરિસ્થિતિ પર ધ્યાન રાખો.',
    safety_actions: [
      'Avoid Hiran river crossing area until Forest Department clearance',
      'Do not allow children near the riverbank',
      'Alert community members of sighting',
    ],
    timestamp: new Date(Date.now() - 350 * 60000).toISOString(),
    officer_approved: false,
    officer_override: false,
    pending_review: true,
  },
  {
    id: 'alert-005',
    incident_id: 'inc-006',
    village: 'Una',
    species: 'Crocodile',
    risk_level: 'MEDIUM',
    distance_km: 0.3,
    confidence: 0.85,
    message_en:
      '⚡ MEDIUM RISK: Large Mugger Crocodile (est. 4m) on Shetrunji river bank. Area frequently used for bathing. Avoid river access immediately.',
    message_gu:
      '⚡ મધ્યમ જોખમ: શેત્રુંજી નદી કિનારે મોટો મગર (અંદાજે ૪ મી.) જોવા મળ્યો. સ્નાન માટે ઉપયોગમાં આવતો વિસ્તાર. તાત્કાલિક નદી ઍક્સેસ ટાળો.',
    safety_actions: [
      'Prohibit all river bathing and washing activities immediately',
      'Reptile Response Unit has been notified',
      'Keep children away from all river banks',
      'Do not attempt to remove the animal yourself',
    ],
    timestamp: new Date(Date.now() - 115 * 60000).toISOString(),
    officer_approved: false,
    officer_override: false,
    pending_review: true,
  },
];

export const FALLBACK_AGENTS: AgentStatusResponse = {
  agents: [
    {
      agent_id: 'agent-1',
      agent_number: 1,
      name: 'SightingValidator',
      full_name: 'Sighting Validation & Verification Agent',
      status: 'ACTIVE',
      latest_action: 'Validating sighting S-001 from Sasan Gir sector',
      confidence: 0.91,
      last_active: new Date(Date.now() - 2 * 60000).toISOString(),
      escalation_required: false,
      action_log: [
        'Received raw sighting report from forest guard',
        'Cross-referenced with historical data — 47 prior incidents in sector',
        'Validated report confidence: 0.91 — marked VERIFIED',
      ],
    },
    {
      agent_id: 'agent-2',
      agent_number: 2,
      name: 'RiskAssessor',
      full_name: 'Conflict Risk Assessment Agent',
      status: 'ACTIVE',
      latest_action: 'Calculating composite risk score for INC-002',
      confidence: 0.84,
      last_active: new Date(Date.now() - 5 * 60000).toISOString(),
      escalation_required: false,
      action_log: [
        'Loaded seasonal migration patterns for Asiatic Lion',
        'Distance 1.8km — applying proximity risk multiplier: 1.4x',
        'Composite risk score: 0.87 — classified HIGH',
      ],
    },
    {
      agent_id: 'agent-3',
      agent_number: 3,
      name: 'AlertBroadcaster',
      full_name: 'Bilingual Alert Generation & Broadcast Agent',
      status: 'IDLE',
      latest_action: 'Last alert broadcast: alert-001 to Sasan Gir',
      confidence: 0.88,
      last_active: new Date(Date.now() - 22 * 60000).toISOString(),
      escalation_required: false,
      action_log: [
        'Generated bilingual alert (EN+GU) for Sasan Gir',
        'Alert distributed to 247 village households via SMS gateway',
        'Awaiting officer approval for alert-002 (Dhari)',
      ],
    },
    {
      agent_id: 'agent-4',
      agent_number: 4,
      name: 'IncidentOrchestrator',
      full_name: 'Incident Response Coordination Agent',
      status: 'WAITING',
      latest_action: 'Awaiting officer approval for INC-002 dispatch',
      confidence: 0.76,
      last_active: new Date(Date.now() - 15 * 60000).toISOString(),
      escalation_required: true,
      action_log: [
        'Created incident ticket INC-002 for Dhari leopard sighting',
        'Recommended: Patrol Unit B — 2 personnel, 1 vehicle',
        'WAITING: Officer approval required before dispatch',
      ],
    },
    {
      agent_id: 'agent-5',
      agent_number: 5,
      name: 'CompensationGuide',
      full_name: 'Compensation Assistance & Documentation Agent',
      status: 'IDLE',
      latest_action: 'Generated document checklist for claim CLM-014',
      confidence: 0.95,
      last_active: new Date(Date.now() - 60 * 60000).toISOString(),
      escalation_required: false,
      action_log: [
        'Loaded Gujarat Livestock Loss Compensation scheme FY2024',
        'Generated 7-item document checklist for CLM-014',
        'Claim routing to Officer Mehta for final approval',
      ],
    },
  ],
  orchestrator: {
    status: 'ACTIVE',
    active_workflows: 3,
    pending_approvals: 2,
    last_updated: new Date().toISOString(),
  },
};

export const FALLBACK_DASHBOARD: DashboardData = {
  stats: {
    active_incidents: 4,
    incidents_high: 2,
    incidents_medium: 2,
    incidents_low: 0,
    avg_ai_confidence: 0.82,
    sightings_today: 5,
    sightings_by_species: {
      'Asiatic Lion': 2,
      Leopard: 2,
      'Striped Hyena': 1,
    },
    response_teams_available: 3,
    response_teams_total: 5,
    pending_approvals: 2,
  },
  incidents: FALLBACK_INCIDENTS,
  sightings: FALLBACK_SIGHTINGS,
  agents: FALLBACK_AGENTS.agents,
  alerts: FALLBACK_ALERTS,
  last_updated: new Date().toISOString(),
};

// ─── HTTP Helper ──────────────────────────────────────────────────────────────

let backendOnline = true;

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<{ data: T | null; error: string | null; offline: boolean }> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    const data = (await res.json()) as T;
    backendOnline = true;
    return { data, error: null, offline: false };
  } catch (err) {
    backendOnline = false;
    const message = err instanceof Error ? err.message : 'Unknown error';
    return { data: null, error: message, offline: true };
  }
}

export function isBackendOnline() {
  return backendOnline;
}

// ─── API Functions ────────────────────────────────────────────────────────────

export async function getDashboard(): Promise<DashboardData> {
  const { data, offline } = await fetchApi<DashboardData>('/dashboard');
  if (offline || !data) return FALLBACK_DASHBOARD;
  return data;
}

export async function getSightings(): Promise<Sighting[]> {
  // Backend returns { sightings: [...], total, is_demo }
  const { data, offline } = await fetchApi<{ sightings: Sighting[] }>('/sightings');
  if (offline || !data) return FALLBACK_SIGHTINGS;
  return data.sightings ?? FALLBACK_SIGHTINGS;
}

export async function createSighting(body: SightingCreateRequest): Promise<Sighting | null> {
  const { data } = await fetchApi<Sighting>('/sightings', {
    method: 'POST',
    body: JSON.stringify({
      species: body.species,
      lat: 21.1,
      lon: 70.5,
      source: body.reported_by ?? 'villager_report',
      notes: body.location,
      nearest_village_id: body.village,
      confidence: body.confidence ?? 0.75,
    }),
  });
  return data;
}

export async function getIncidents(): Promise<Incident[]> {
  // Backend returns { incidents: [...], total, filters, is_demo }
  const { data, offline } = await fetchApi<{ incidents: Incident[] }>('/incidents');
  if (offline || !data) return FALLBACK_INCIDENTS;
  return data.incidents ?? FALLBACK_INCIDENTS;
}

export async function getIncident(id: string): Promise<Incident | null> {
  const { data } = await fetchApi<Incident>(`/incidents/${id}`);
  return data;
}

export async function updateIncidentStatus(
  id: string,
  status: string
): Promise<Incident | null> {
  const { data } = await fetchApi<Incident>(`/incidents/${id}/status`, {
    method: 'PUT',
    body: JSON.stringify({ new_status: status, officer_id: 'OFFICER_DEMO' }),
  });
  return data;
}

export async function getAlerts(): Promise<Alert[]> {
  // Backend returns { alerts: [...], total, is_demo }
  const { data, offline } = await fetchApi<{ alerts: Alert[] }>('/alerts');
  if (offline || !data) return FALLBACK_ALERTS;
  // Normalize alert objects to match frontend Alert type
  const raw = data.alerts ?? [];
  return raw.map((al: Record<string, unknown>) => ({
    id:              (al.alert_id as string) || (al.id as string) || '',
    incident_id:     al.incident_id as string | undefined,
    village:         (al.village_name as string) || (al.village as string) || 'Unknown',
    species:         (al.species as string) || 'Unknown',
    risk_level:      (al.risk_level as string) || 'MEDIUM',
    distance_km:     Number(al.distance_km) || 2.5,
    confidence:      Number(al.confidence) || 0.75,
    message_en:      (al.message_en as string) || '',
    message_gu:      (al.message_gu as string) || '',
    safety_actions:  (al.safety_actions as string[]) || [],
    timestamp:       (al.issued_at as string) || (al.timestamp as string) || new Date().toISOString(),
    officer_approved:(al.officer_approved as boolean) || false,
    officer_override:(al.officer_override as boolean) || false,
    pending_review:  !(al.officer_approved as boolean),
  })) as Alert[];
}

export async function generateAlert(incidentId: string): Promise<Alert | null> {
  const { data } = await fetchApi<Alert>('/alerts/generate', {
    method: 'POST',
    body: JSON.stringify({ incident_id: incidentId }),
  });
  return data;
}

export async function startCompensation(
  body: StartCompensationRequest
): Promise<CompensationClaim | null> {
  const { data } = await fetchApi<CompensationClaim>('/compensation/start', {
    method: 'POST',
    body: JSON.stringify({
      incident_id:       body.incident_id,
      claimant_name:     body.villager_name,
      claimant_village_id: body.village,
      loss_type:         body.loss_type,
      loss_description:  body.loss_details,
      contact_number:    body.contact,
      estimated_loss_value: body.estimated_value,
    }),
  });
  return data;
}

export async function getCompensation(id: string): Promise<CompensationClaim | null> {
  const { data } = await fetchApi<CompensationClaim>(`/compensation/${id}`);
  return data;
}

export async function getCompensationChecklist(
  lossType: LossType
): Promise<CompensationChecklist | null> {
  const { data } = await fetchApi<CompensationChecklist>(
    `/compensation/checklist/${lossType}`
  );
  if (!data) {
    return {
      loss_type: lossType,
      required_documents: [
        'FIR / First Information Report from nearest police station',
        'Forest Department sighting verification certificate',
        'Panchnama (witness statement) — minimum 3 witnesses',
        'Veterinary certificate (for livestock claims)',
        'Photographs of loss/damage (timestamped)',
        'Land / livestock ownership documents',
        'Bank account details for direct transfer',
      ],
      optional_documents: [
        'Camera trap footage (if available)',
        'Village head (Sarpanch) letter of attestation',
      ],
      notes:
        'All claims must be filed within 30 days of the incident. Final approval rests with authorized Forest Department officer.',
    };
  }
  return data;
}

export async function getAgentStatus(): Promise<AgentStatusResponse> {
  // Try the dashboard endpoint which returns properly-shaped agents[]
  const { data: dashData, offline } = await fetchApi<{ agents: AgentInfo[] }>('/dashboard');
  if (!offline && dashData?.agents) {
    return {
      agents: dashData.agents,
      orchestrator: {
        status: 'ACTIVE',
        active_workflows: 1,
        pending_approvals: 0,
        last_updated: new Date().toISOString(),
      },
    };
  }
  return FALLBACK_AGENTS;
}

export async function getAgentLogs(): Promise<Record<string, string[]>> {
  // Backend returns { logs: [...], total, is_demo }
  const { data } = await fetchApi<{ logs: Array<Record<string, unknown>> }>('/agents/logs');
  if (!data?.logs) return {};
  // Group by agent name
  const grouped: Record<string, string[]> = {};
  for (const log of data.logs) {
    const agent = String(log.agent || 'unknown');
    if (!grouped[agent]) grouped[agent] = [];
    grouped[agent].push(String(log.output_summary || log.action || ''));
  }
  return grouped;
}

export async function getPendingApprovals(): Promise<unknown[]> {
  // Backend endpoint is /agents/pending-approvals (not /agents/pending)
  const { data } = await fetchApi<{ pending_approvals: unknown[] }>('/agents/pending-approvals');
  return data?.pending_approvals || [];
}

export async function approveAction(body: ApproveRequest): Promise<unknown> {
  // Backend expects { approval_id, officer_id, decision, notes?, override_data? }
  // Frontend sends { request_id, action, officer_id, notes? }
  const backendBody = {
    approval_id: body.request_id,
    officer_id:  body.officer_id,
    decision:    body.action === 'APPROVE' ? 'APPROVED' : 'OVERRIDE',
    notes:       body.notes,
  };
  const { data, error } = await fetchApi<unknown>('/agents/approve', {
    method: 'POST',
    body: JSON.stringify(backendBody),
  });
  if (error) throw new Error(error);
  return data;
}

export async function runDemo(): Promise<DemoScenario | null> {
  const { data } = await fetchApi<DemoScenario>('/demo/run', { method: 'POST' });
  return data;
}

export async function getDemoStatus(): Promise<DemoScenario | null> {
  const { data } = await fetchApi<DemoScenario>('/demo/status');
  return data;
}
