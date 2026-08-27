"""VanRakshak AI — Dashboard Route"""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

# Agent display names for frontend
AGENT_DISPLAY = [
    {"agent_id": "agent-1", "agent_number": 1,
     "name": "Movement Predictor", "full_name": "Wildlife Movement Prediction Agent",
     "key": "movement_agent"},
    {"agent_id": "agent-2", "agent_number": 2,
     "name": "Alert Generator", "full_name": "Village Alert & Early Warning Agent",
     "key": "alert_agent"},
    {"agent_id": "agent-3", "agent_number": 3,
     "name": "Response Coordinator", "full_name": "Forest Response Coordination Agent",
     "key": "response_agent"},
    {"agent_id": "agent-4", "agent_number": 4,
     "name": "Compensation Guide", "full_name": "Livestock Compensation Assistant Agent",
     "key": "compensation_agent"},
    {"agent_id": "agent-5", "agent_number": 5,
     "name": "Hotspot Analyst", "full_name": "Conflict Hotspot Dashboard Agent",
     "key": "hotspot_agent"},
]


@router.get("/dashboard")
async def get_dashboard():
    """
    GET /api/dashboard
    Returns full dashboard data: stats, active incidents, recent sightings,
    risk map data, and agent statuses.

    Response shape matches frontend DashboardData type:
      { stats, incidents, sightings, agents, alerts, last_updated }
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    raw = orch.get_dashboard_data()

    # --- Build frontend-compatible incidents list ---
    incidents = []
    for idx, inc in enumerate(raw.get("active_incidents", [])[:6]):
        incidents.append({
            "id":               inc.get("incident_id", f"INC-{idx:03d}"),
            "display_id":       inc.get("incident_id", f"INC-{idx:03d}").upper(),
            "village":          inc.get("village_name", inc.get("village_id", "Unknown")),
            "species":          inc.get("species", "Unknown"),
            "severity":         inc.get("severity", "MEDIUM"),
            "risk_score":       round(inc.get("risk_score", 0.5), 2),
            "status":           inc.get("status", "NEW"),
            "timestamp":        inc.get("date", inc.get("timestamp", datetime.now(timezone.utc).isoformat())),
            "recommended_team": inc.get("recommended_team", "Forest Patrol Unit"),
            "assigned_officer": inc.get("assigned_officer"),
            "description":      inc.get("incident_type", inc.get("description", "Wildlife conflict incident")),
            "pending_approval": inc.get("status") in ("NEW", "ASSIGNED"),
            "sighting_id":      inc.get("sighting_id"),
        })

    # --- Build frontend-compatible sightings list ---
    sightings = []
    for idx, s in enumerate(raw.get("recent_sightings", [])[-6:]):
        sightings.append({
            "id":          s.get("sighting_id", f"SIG-{idx:03d}"),
            "species":     s.get("species", "Unknown"),
            "location":    s.get("notes", s.get("source", "Gir Forest Area")),
            "village":     s.get("nearest_village_id", "Sasan Gir"),
            "distance_km": round(s.get("distance_to_nearest_village_km", 2.5), 1),
            "confidence":  round(s.get("confidence", 0.75), 2),
            "timestamp":   s.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "reported_by": s.get("source", "ranger_report"),
            "verified":    s.get("confidence", 0.75) >= 0.7,
            "risk_level":  "HIGH" if s.get("confidence", 0.75) >= 0.8 else
                           "MEDIUM" if s.get("confidence", 0.75) >= 0.5 else "LOW",
        })

    # --- Build frontend-compatible agent list ---
    agents = []
    for ag in AGENT_DISPLAY:
        last_log = next(
            (log for log in reversed(orch.agent_logs) if log.get("agent") == ag["key"]),
            None,
        )
        agents.append({
            "agent_id":           ag["agent_id"],
            "agent_number":       ag["agent_number"],
            "name":               ag["name"],
            "full_name":          ag["full_name"],
            "status":             "ACTIVE",
            "latest_action":      last_log["output_summary"][:80] if last_log else "Monitoring...",
            "confidence":         round(last_log.get("confidence") or 0.82, 2),
            "last_active":        last_log["timestamp"] if last_log else datetime.now(timezone.utc).isoformat(),
            "escalation_required":last_log["escalation_required"] if last_log else False,
            "action_log":         [last_log["output_summary"]] if last_log else [],
        })

    # --- Build frontend-compatible stats ---
    raw_stats = raw.get("stats", {})
    active_inc = raw.get("active_incidents", [])
    stats = {
        "active_incidents":          raw_stats.get("active_incidents", 0),
        "incidents_high":            sum(1 for i in active_inc if i.get("severity") == "HIGH"),
        "incidents_medium":          sum(1 for i in active_inc if i.get("severity") == "MEDIUM"),
        "incidents_low":             sum(1 for i in active_inc if i.get("severity") == "LOW"),
        "avg_ai_confidence":         0.82,
        "sightings_today":           raw_stats.get("total_sightings_30d", 0),
        "sightings_by_species":      {},
        "response_teams_available":  3,
        "response_teams_total":      4,
        "pending_approvals":         raw_stats.get("pending_approvals", 0),
    }

    # --- Build frontend-compatible alerts list ---
    alerts = []
    for al in raw.get("recent_alerts", []):
        alerts.append({
            "id":              al.get("alert_id", ""),
            "incident_id":     al.get("incident_id"),
            "village":         al.get("village_name", "Unknown"),
            "species":         al.get("species", "Unknown"),
            "risk_level":      al.get("risk_level", "MEDIUM"),
            "distance_km":     round(al.get("distance_km", 2.5), 1),
            "confidence":      round(al.get("confidence", 0.75), 2),
            "message_en":      al.get("message_en", ""),
            "message_gu":      al.get("message_gu", ""),
            "safety_actions":  al.get("safety_actions", []),
            "timestamp":       al.get("issued_at", datetime.now(timezone.utc).isoformat()),
            "officer_approved":al.get("officer_approved", False),
            "officer_override":al.get("officer_override", False),
            "pending_review":  not al.get("officer_approved", False),
        })

    return {
        "stats":        stats,
        "incidents":    incidents,
        "sightings":    sightings,
        "agents":       agents,
        "alerts":       alerts,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "is_demo":      True,
    }
