// ─── Risk & Status Enums ─────────────────────────────────────────────────────

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentStatus = 'NEW' | 'ASSIGNED' | 'IN_PROGRESS' | 'RESOLVED' | 'ESCALATED';
export type AgentStatus = 'ACTIVE' | 'IDLE' | 'ERROR' | 'WAITING';
export type LossType = 'LIVESTOCK_PREDATION' | 'CROP_DAMAGE' | 'PROPERTY_DAMAGE' | 'INJURY';
export type DemoStepStatus = 'PENDING' | 'RUNNING' | 'COMPLETE' | 'WAITING_FOR_OFFICER';

// ─── Core Domain Types ────────────────────────────────────────────────────────

export interface Sighting {
  id: string;
  species: string;
  location: string;
  village: string;
  distance_km: number;
  confidence: number;
  timestamp: string;
  reported_by: string;
  verified: boolean;
  risk_level: RiskLevel;
}

export interface Alert {
  id: string;
  incident_id?: string;
  village: string;
  species: string;
  risk_level: RiskLevel;
  distance_km: number;
  confidence: number;
  message_en: string;
  message_gu: string;
  safety_actions: string[];
  timestamp: string;
  officer_approved: boolean;
  officer_override: boolean;
  pending_review: boolean;
}

export interface Incident {
  id: string;
  display_id: string;
  village: string;
  species: string;
  severity: RiskLevel;
  risk_score: number;
  status: IncidentStatus;
  timestamp: string;
  recommended_team: string;
  assigned_officer?: string;
  description: string;
  pending_approval: boolean;
  sighting_id?: string;
}

export interface AgentInfo {
  agent_id: string;
  agent_number: number;
  name: string;
  full_name: string;
  status: AgentStatus;
  latest_action: string;
  confidence: number;
  last_active: string;
  escalation_required: boolean;
  action_log: string[];
}

export interface AgentStatusResponse {
  agents: AgentInfo[];
  orchestrator: {
    status: AgentStatus;
    active_workflows: number;
    pending_approvals: number;
    last_updated: string;
  };
}

export interface CompensationClaim {
  claim_id: string;
  incident_id: string;
  villager_name: string;
  village: string;
  contact: string;
  loss_type: LossType;
  loss_details: string;
  animals_lost?: number;
  estimated_value?: number;
  status: string;
  officer_review_status: string;
  created_at: string;
  documents_checklist: string[];
}

export interface CompensationChecklist {
  loss_type: LossType;
  required_documents: string[];
  optional_documents: string[];
  notes: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface DashboardStats {
  active_incidents: number;
  incidents_high: number;
  incidents_medium: number;
  incidents_low: number;
  avg_ai_confidence: number;
  sightings_today: number;
  sightings_by_species: Record<string, number>;
  response_teams_available: number;
  response_teams_total: number;
  pending_approvals: number;
}

export interface DashboardData {
  stats: DashboardStats;
  incidents: Incident[];
  sightings: Sighting[];
  agents: AgentInfo[];
  alerts: Alert[];
  last_updated: string;
}

// ─── Demo Workflow ────────────────────────────────────────────────────────────

export interface DemoStep {
  step: number;
  icon: string;
  title: string;
  description: string;
  agent?: string;
  data?: Record<string, unknown>;
  status: DemoStepStatus;
  timestamp?: string;
}

export interface DemoScenario {
  scenario_id: string;
  status: 'IDLE' | 'RUNNING' | 'COMPLETE';
  steps: DemoStep[];
  risk_score?: number;
  alert_text?: string;
  incident_ticket?: Record<string, unknown>;
  started_at?: string;
  completed_at?: string;
}

// ─── API Requests ─────────────────────────────────────────────────────────────

export interface StartCompensationRequest {
  incident_id: string;
  villager_name: string;
  village: string;
  contact: string;
  loss_type: LossType;
  loss_details: string;
  animals_lost?: number;
  estimated_value?: number;
}

export interface ApproveRequest {
  request_id: string;
  action: 'APPROVE' | 'OVERRIDE';
  officer_id: string;
  notes?: string;
}

export interface SightingCreateRequest {
  species: string;
  location: string;
  village: string;
  distance_km: number;
  confidence?: number;
  reported_by?: string;
}

// ─── Village Map ──────────────────────────────────────────────────────────────

export interface VillageMapNode {
  id: string;
  name: string;
  name_gu: string;
  x: number;
  y: number;
  risk: RiskLevel;
  incidents: number;
}
