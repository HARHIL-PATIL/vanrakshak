"""
VanRakshak AI — Pydantic v2 Data Models
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class IncidentType(str, Enum):
    LIVESTOCK_PREDATION = "livestock_predation"
    CROP_DAMAGE = "crop_damage"
    HUMAN_INJURY = "human_injury"
    PROPERTY_DAMAGE = "property_damage"


class IncidentStatus(str, Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class AlertSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class SightingSource(str, Enum):
    CAMERA_TRAP = "camera_trap"
    RANGER_REPORT = "ranger_report"
    VILLAGER_REPORT = "villager_report"
    SATELLITE = "satellite"
    AI_PREDICTION = "ai_prediction"


class ApprovalDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    OVERRIDE = "OVERRIDE"
    PENDING = "PENDING"


class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISBURSED = "DISBURSED"


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------

class WildlifeSighting(BaseModel):
    """A reported or detected wildlife sighting event."""
    sighting_id: str
    species: str
    lat: float
    lon: float
    timestamp: datetime
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence 0–1")
    source: SightingSource
    count: int = Field(default=1, ge=1)
    nearest_village_id: Optional[str] = None
    notes: Optional[str] = None
    is_demo: bool = True

    model_config = {"json_schema_extra": {"example": {
        "sighting_id": "SGT001",
        "species": "Asiatic Lion",
        "lat": 21.1300,
        "lon": 70.5600,
        "timestamp": "2025-01-01T06:00:00",
        "confidence": 0.95,
        "source": "camera_trap",
        "count": 2,
    }}}


class Village(BaseModel):
    """A village/settlement near Gir Forest."""
    village_id: str
    name: str
    lat: float
    lon: float
    livestock_count: int = Field(ge=0)
    population: int = Field(ge=0)
    contact_number: str
    district: str
    risk_zone: RiskLevel = RiskLevel.UNKNOWN
    is_demo: bool = True


class ConflictIncident(BaseModel):
    """A recorded human-wildlife conflict incident."""
    incident_id: str
    type: IncidentType
    severity: RiskLevel
    village_id: str
    species: str
    date: datetime
    losses: str
    status: IncidentStatus = IncidentStatus.NEW
    assigned_team_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    compensation_claim_id: Optional[str] = None
    is_demo: bool = True


class RiskScoreBreakdown(BaseModel):
    """Component-level breakdown of the weighted risk formula."""
    proximity_score: float
    recent_movement_score: float
    time_of_day_score: float
    livestock_density_score: float
    historical_frequency_score: float
    environment_score: float


class RiskAssessment(BaseModel):
    """
    Output of the VanRakshak risk scoring engine.

    DISCLAIMER: PROTOTYPE RISK-SCORING MODEL — NOT AN OFFICIALLY VALIDATED FORMULA.
    Results are indicative only and must be reviewed by a qualified Forest Officer
    before any field action is taken.
    """
    assessment_id: str
    sighting_id: str
    village_id: str
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    component_breakdown: RiskScoreBreakdown
    confidence: float = Field(ge=0.0, le=1.0)
    assessed_at: datetime
    disclaimer: str = (
        "PROTOTYPE RISK-SCORING MODEL — NOT AN OFFICIALLY VALIDATED FORMULA. "
        "For demonstration purposes only."
    )
    is_demo: bool = True


class ResponseTeam(BaseModel):
    """A forest response / rescue team unit."""
    team_id: str
    name: str
    base_lat: float
    base_lon: float
    availability: bool
    current_status: str
    specialization: str
    member_count: int = Field(ge=1)
    contact: str
    is_demo: bool = True


class IncidentTicket(BaseModel):
    """
    An incident ticket created by the Response Coordination Agent.

    IMPORTANT: This is a RECOMMENDATION only. A human Forest Officer must
    review and confirm before any field team is dispatched.
    """
    ticket_id: str
    incident_id: str
    sighting_id: str
    recommended_team_id: str
    recommended_team_name: str
    distance_km: float
    priority: RiskLevel
    created_at: datetime
    status: IncidentStatus = IncidentStatus.NEW
    human_approval_required: bool = True
    approval_note: str = (
        "RECOMMENDATION ONLY — Human Forest Officer approval required before dispatch."
    )
    is_demo: bool = True


class CompensationClaim(BaseModel):
    """
    A livestock / crop compensation claim draft.

    IMPORTANT: AI prepares the draft only. Final approval / rejection
    is the sole responsibility of the authorised Forest Officer.
    """
    claim_id: str
    incident_id: str
    claimant_name: str
    claimant_village_id: str
    loss_type: IncidentType
    species_responsible: str
    estimated_loss_value: Optional[float] = None
    loss_description: str
    document_checklist: list[str]
    status: ClaimStatus = ClaimStatus.DRAFT
    created_at: datetime
    officer_id: Optional[str] = None
    officer_notes: Optional[str] = None
    human_approval_required: bool = True
    disclaimer: str = (
        "AI-GENERATED DRAFT ONLY — Final approval/rejection by authorised "
        "Forest Department officer only."
    )
    is_demo: bool = True


class AgentLog(BaseModel):
    """An action log entry produced by any VanRakshak agent."""
    log_id: str
    agent: str
    action: str
    input_ref: str
    output_summary: str
    timestamp: datetime
    confidence: Optional[float] = None
    escalation_required: bool = False
    escalation_status: str = "NONE"  # NONE | PENDING | ESCALATED | RESOLVED
    is_demo: bool = True


class OfficerApproval(BaseModel):
    """
    Human-in-the-loop approval record.

    Every consequential AI action requires an OfficerApproval before execution.
    """
    approval_id: str
    ticket_id: Optional[str] = None
    claim_id: Optional[str] = None
    incident_id: Optional[str] = None
    officer_id: str
    decision: ApprovalDecision = ApprovalDecision.PENDING
    override_data: Optional[dict[str, Any]] = None
    decided_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_demo: bool = True


class AlertMessage(BaseModel):
    """A public-facing alert message for villagers/officers."""
    alert_id: str
    sighting_id: str
    village_id: str
    village_name: str
    species: str
    severity: AlertSeverity
    risk_score: float
    message_english: str
    message_gujarati: str
    safety_actions: list[str]
    issued_at: datetime
    is_active: bool = True
    confidence: float = Field(ge=0.0, le=1.0)
    is_demo: bool = True


# ---------------------------------------------------------------------------
# Request / Response schemas for API endpoints
# ---------------------------------------------------------------------------

class SightingCreateRequest(BaseModel):
    species: str
    lat: float
    lon: float
    count: int = 1
    source: SightingSource = SightingSource.VILLAGER_REPORT
    nearest_village_id: Optional[str] = None
    notes: Optional[str] = None


class IncidentStatusUpdateRequest(BaseModel):
    new_status: IncidentStatus
    officer_id: str
    notes: Optional[str] = None


class CompensationStartRequest(BaseModel):
    incident_id: str
    claimant_name: str
    claimant_village_id: str
    loss_type: IncidentType
    loss_description: str
    estimated_loss_value: Optional[float] = None


class OfficerApprovalRequest(BaseModel):
    approval_id: str
    officer_id: str
    decision: ApprovalDecision
    notes: Optional[str] = None
    override_data: Optional[dict[str, Any]] = None


class AlertGenerateRequest(BaseModel):
    sighting_id: str
    village_id: str


# ---------------------------------------------------------------------------
# Dashboard aggregate
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    total_sightings_30d: int
    active_incidents: int
    high_risk_villages: int
    alerts_issued_today: int
    pending_approvals: int
    compensation_claims_pending: int
    is_demo: bool = True
