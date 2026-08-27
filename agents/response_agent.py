# ============================================================
# VanRakshak AI — Agent 3: Forest Response Coordination Agent
# Creates incident tickets, finds nearest team, tracks lifecycle.
# NEVER dispatches autonomously — only recommends.
# ============================================================

import math
import uuid
from datetime import datetime


# Incident lifecycle states
LIFECYCLE = ["NEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "ESCALATED"]


class ResponseAgent:
    """
    Agent 3 — Forest Response Coordination Agent.
    Responsible for:
      - Creating incident tickets
      - Finding the nearest available response team
      - Managing incident lifecycle
      - Queuing dispatch decisions for human approval
    """

    NAME = "ResponseAgent"
    VERSION = "1.0-PROTOTYPE"

    def __init__(self):
        self.status = "IDLE"
        self.last_action = None
        self.last_confidence = None
        self.last_run = None
        self.total_processed = 0

    # ------------------------------------------------------------------

    def process(self, alert: dict, sighting: dict,
                village: dict, response_teams: list,
                pending_approvals: list) -> dict:
        """
        Create an incident ticket and recommend the nearest available team.
        Adds the dispatch recommendation to the human-approval queue.

        Returns the incident ticket dict.
        """
        self.status = "PROCESSING"

        severity    = alert.get("severity", "MEDIUM")
        risk_score  = alert.get("risk_score", 0.0)
        confidence  = alert.get("confidence", 0.70)

        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"

        # Find nearest available team
        nearest_team, distance_to_team = self._find_nearest_team(
            village, response_teams
        )

        incident = {
            "id":              incident_id,
            "village_id":      village["id"],
            "village_name":    village["name"],
            "species":         sighting.get("species", "Unknown"),
            "sighting_id":     sighting.get("id"),
            "severity":        severity,
            "risk_score":      risk_score,
            "status":          "NEW",
            "assigned_team":   None,
            "recommended_team": nearest_team["id"] if nearest_team else None,
            "recommended_team_name": nearest_team["name"] if nearest_team else "None available",
            "distance_to_team_km": round(distance_to_team, 2) if distance_to_team else None,
            "incident_type":   self._classify_incident(sighting, severity),
            "timestamp":       datetime.utcnow().isoformat(),
            "notes":           sighting.get("notes", ""),
            "lifecycle":       ["NEW"],
            "agent_meta": {
                "agent":      self.NAME,
                "version":    self.VERSION,
                "timestamp":  datetime.utcnow().isoformat(),
            },
        }

        # Queue dispatch for human approval
        if nearest_team:
            approval_item = {
                "action_id":    f"APR-{uuid.uuid4().hex[:6].upper()}",
                "action_type":  "DISPATCH_TEAM",
                "incident_id":  incident_id,
                "ai_recommendation": (
                    f"Dispatch {nearest_team['name']} to {village['name']} "
                    f"for {sighting.get('species','Unknown')} incident. "
                    f"Team is {distance_to_team:.1f} km away."
                ),
                "recommended_team": nearest_team["id"],
                "recommended_team_name": nearest_team["name"],
                "confidence":   confidence,
                "risk_score":   risk_score,
                "reasoning": (
                    f"Nearest available team is {nearest_team['name']} "
                    f"({distance_to_team:.1f} km). "
                    f"Risk score: {risk_score:.2f} ({severity}). "
                    f"Team specialization: {nearest_team.get('specialization', 'General')}."
                ),
                "status":      "PENDING",
                "timestamp":   datetime.utcnow().isoformat(),
                "village_id":  village["id"],
            }
            pending_approvals.append(approval_item)
            incident["approval_id"] = approval_item["action_id"]

        self.status = "IDLE"
        self.last_action = f"Created {incident_id} for {village['name']} — team {incident['recommended_team_name']} recommended"
        self.last_confidence = confidence
        self.last_run = datetime.utcnow().isoformat()
        self.total_processed += 1

        return incident

    def update_status(self, incident: dict, new_status: str,
                      response_teams: list, notes: str = "") -> dict:
        """
        Advance an incident through the lifecycle.
        Returns the updated incident.
        """
        if new_status not in LIFECYCLE:
            raise ValueError(f"Invalid status: {new_status}")

        incident["status"] = new_status
        incident["lifecycle"].append(new_status)
        if notes:
            incident["notes"] += f" | {notes}"
        incident["updated_at"] = datetime.utcnow().isoformat()

        if new_status == "ASSIGNED" and incident.get("recommended_team"):
            incident["assigned_team"] = incident["recommended_team"]
            # Mark team as deployed
            for team in response_teams:
                if team["id"] == incident["recommended_team"]:
                    team["status"] = "DEPLOYED"

        return incident

    # ------------------------------------------------------------------

    def _find_nearest_team(self, village: dict, teams: list):
        """Return (nearest_team, distance_km) for the nearest available team."""
        available = [t for t in teams if t.get("status") == "AVAILABLE"]
        if not available:
            return None, None

        best_team, best_dist = None, float("inf")
        for team in available:
            d = _haversine(village["lat"], village["lon"], team["lat"], team["lon"])
            if d < best_dist:
                best_dist = d
                best_team = team

        return best_team, best_dist

    def _classify_incident(self, sighting: dict, severity: str) -> str:
        species = sighting.get("species", "")
        notes   = sighting.get("notes", "").lower()
        if "crop" in notes or "field" in notes:
            return "crop_damage"
        if "kill" in notes or "attack" in notes:
            return "livestock_kill"
        if "child" in notes or "person" in notes or "encounter" in notes:
            return "human_encounter"
        if severity == "HIGH":
            return "high_risk_sighting"
        return "routine_sighting"

    def get_status(self) -> dict:
        return {
            "agent":            self.NAME,
            "status":           self.status,
            "last_action":      self.last_action,
            "last_confidence":  self.last_confidence,
            "last_run":         self.last_run,
            "total_processed":  self.total_processed,
            "escalation_state": "NONE",
        }


def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
