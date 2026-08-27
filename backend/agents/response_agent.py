"""
VanRakshak AI — Agent 3: Forest Response Coordination Agent
============================================================
Responsibilities:
  - Create incident tickets from sighting + risk assessment data
  - Find and rank nearest available response teams by distance
  - Manage incident lifecycle (NEW → ASSIGNED → IN_PROGRESS → RESOLVED / ESCALATED)

CRITICAL: Every ticket is a RECOMMENDATION only.
A human Forest Officer MUST confirm before any team is dispatched.
AI never autonomously dispatches field personnel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from data.sample_data import SAMPLE_RESPONSE_TEAMS, get_village_by_id
from ml.risk_engine import haversine_km

# Valid status transitions
STATUS_TRANSITIONS: dict[str, list[str]] = {
    "NEW":         ["ASSIGNED", "ESCALATED", "CLOSED"],
    "ASSIGNED":    ["IN_PROGRESS", "ESCALATED", "CLOSED"],
    "IN_PROGRESS": ["RESOLVED", "ESCALATED"],
    "RESOLVED":    ["CLOSED"],
    "ESCALATED":   ["IN_PROGRESS", "CLOSED"],
    "CLOSED":      [],
}


class ResponseCoordinationAgent:
    """
    Agent 3 — Forest Response Coordination.

    Creates and manages incident tickets, ranks response teams by proximity
    and availability, and handles status lifecycle transitions.

    IMPORTANT: All dispatch recommendations require human officer approval.
    """

    AGENT_NAME = "response_agent"

    def __init__(self):
        # In-memory incident ticket store (keyed by ticket_id)
        self._tickets: dict[str, dict] = {}

    def create_incident_ticket(
        self,
        sighting: dict,
        risk_assessment: dict,
        village_id: Optional[str] = None,
    ) -> dict:
        """
        Create an incident ticket from a sighting + risk assessment pair.

        Steps:
            1. Derive priority from consensus_risk_level
            2. Determine incident location (sighting coords)
            3. Calculate distance from each response team to the incident
            4. Rank teams: available first, then by ascending distance
            5. Return ticket with top recommended team

        IMPORTANT: Ticket status starts as NEW; dispatch requires officer approval.

        Args:
            sighting        : Sighting dict (lat, lon, species, sighting_id, …)
            risk_assessment : Output from MovementPredictionAgent.analyze()
            village_id      : Optional override village ID

        Returns:
            IncidentTicket-equivalent dict
        """
        ticket_id   = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"

        # ── Resolve priority ───────────────────────────────────────────────
        risk_level = risk_assessment.get(
            "consensus_risk_level",
            risk_assessment.get("risk_assessment", {}).get("risk_level", "MEDIUM"),
        )

        # ── Incident location = sighting coordinates ───────────────────────
        inc_lat = sighting.get("lat", 21.1242)
        inc_lon = sighting.get("lon", 70.5521)

        # ── Step 3 & 4: Rank response teams ────────────────────────────────
        teams_with_distance = []
        for team in SAMPLE_RESPONSE_TEAMS:
            dist_km = haversine_km(
                inc_lat, inc_lon,
                team["base_lat"], team["base_lon"],
            )
            teams_with_distance.append({
                **team,
                "distance_km": round(dist_km, 3),
            })

        # Sort: available teams first, then by distance
        teams_with_distance.sort(
            key=lambda t: (not t["availability"], t["distance_km"])
        )

        recommended_team = teams_with_distance[0] if teams_with_distance else None
        all_teams_ranked = [
            {
                "team_id":      t["team_id"],
                "name":         t["name"],
                "available":    t["availability"],
                "distance_km":  t["distance_km"],
                "specialization": t["specialization"],
                "status":       t["current_status"],
            }
            for t in teams_with_distance
        ]

        village = get_village_by_id(village_id or sighting.get("nearest_village_id", ""))
        village_name = village["name"] if village else "Unknown Village"

        ticket = {
            "ticket_id":             ticket_id,
            "incident_id":           incident_id,
            "sighting_id":           sighting.get("sighting_id", "UNKNOWN"),
            "species":               sighting.get("species", "Unknown"),
            "village_id":            village_id or sighting.get("nearest_village_id", ""),
            "village_name":          village_name,
            "incident_lat":          inc_lat,
            "incident_lon":          inc_lon,
            "priority":              risk_level,
            "risk_score":            risk_assessment.get("risk_assessment", {}).get("risk_score", 0.5),
            "recommended_team_id":   recommended_team["team_id"]   if recommended_team else None,
            "recommended_team_name": recommended_team["name"]       if recommended_team else None,
            "recommended_team_specialization": recommended_team["specialization"] if recommended_team else None,
            "distance_km":           recommended_team["distance_km"] if recommended_team else None,
            "all_teams_ranked":      all_teams_ranked,
            "status":                "NEW",
            "assigned_officer_id":   None,
            "created_at":            datetime.now(timezone.utc).isoformat(),
            "updated_at":            datetime.now(timezone.utc).isoformat(),
            "human_approval_required": True,
            "approval_note": (
                "RECOMMENDATION ONLY — Human Forest Officer must review and "
                "approve before any team is dispatched to the field."
            ),
            "is_demo": True,
        }

        self._tickets[ticket_id] = ticket
        return ticket

    def update_incident_status(
        self,
        ticket_id: str,
        new_status: str,
        officer_id: str,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Update the lifecycle status of an incident ticket.

        Valid transitions:
            NEW → ASSIGNED → IN_PROGRESS → RESOLVED / ESCALATED → CLOSED

        Args:
            ticket_id   : The ticket to update
            new_status  : Target status string
            officer_id  : ID of the approving officer
            notes       : Optional resolution / escalation notes

        Returns:
            Updated ticket dict or error dict
        """
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            return {
                "success": False,
                "error":   f"Ticket {ticket_id} not found",
                "is_demo": True,
            }

        current_status = ticket["status"]
        allowed_next   = STATUS_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next:
            return {
                "success":         False,
                "error":           (
                    f"Invalid transition: {current_status} → {new_status}. "
                    f"Allowed: {allowed_next}"
                ),
                "current_status":  current_status,
                "ticket_id":       ticket_id,
                "is_demo":         True,
            }

        ticket["status"]              = new_status
        ticket["assigned_officer_id"] = officer_id
        ticket["updated_at"]          = datetime.now(timezone.utc).isoformat()
        if notes:
            ticket["resolution_notes"] = notes

        return {
            "success":          True,
            "ticket_id":        ticket_id,
            "previous_status":  current_status,
            "new_status":       new_status,
            "updated_by":       officer_id,
            "updated_at":       ticket["updated_at"],
            "is_demo":          True,
        }

    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        """Retrieve a ticket by ID from in-memory store."""
        return self._tickets.get(ticket_id)

    def list_tickets(self, status_filter: Optional[str] = None) -> list[dict]:
        """List all tickets, optionally filtered by status."""
        tickets = list(self._tickets.values())
        if status_filter:
            tickets = [t for t in tickets if t["status"] == status_filter]
        return tickets
