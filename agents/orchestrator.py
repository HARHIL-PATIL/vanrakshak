# ============================================================
# VanRakshak AI — Central Orchestrator
# Routes wildlife events through all 5 agents in sequence.
# Maintains shared state. Human-approval queue enforced.
# ============================================================

import copy
import uuid
from datetime import datetime

from agents.movement_agent     import MovementAgent
from agents.alert_agent        import AlertAgent
from agents.response_agent     import ResponseAgent
from agents.compensation_agent import CompensationAgent
from agents.hotspot_agent      import HotspotAgent
from data.sample_data          import get_all_data


class Orchestrator:
    """
    Central Orchestration Layer for VanRakshak AI.

    State held in-memory (no database).  The pipeline for a new sighting:
        S001  →  MovementAgent  →  AlertAgent  →  ResponseAgent
              →  HotspotAgent  →  (human approval queue)
    """

    def __init__(self):
        # --- Load demo seed data ---
        seed = get_all_data()
        self.villages        = seed["villages"]
        self.sightings       = seed["sightings"]
        self.incidents       = seed["incidents"]
        self.response_teams  = seed["response_teams"]
        self.risk_assessments = seed["risk_assessments"]
        self.agent_logs      = seed["agent_logs"]

        # Runtime state
        self.alerts           = []
        self.compensation_claims = []
        self.pending_approvals  = []
        self.approved_actions   = []
        self.audit_log          = []

        # Instantiate all agents
        self.movement_agent     = MovementAgent()
        self.alert_agent        = AlertAgent()
        self.response_agent     = ResponseAgent()
        self.compensation_agent = CompensationAgent()
        self.hotspot_agent      = HotspotAgent()

        # Run initial hotspot assessment on seed data
        self._refresh_hotspots()
        self._log("Orchestrator", "System initialised with demo seed data", 1.0)

    # ==================================================================
    # Main pipeline — called on every new sighting
    # ==================================================================

    def process_sighting(self, sighting: dict) -> dict:
        """
        Full 5-agent pipeline for a new wildlife sighting.

        1. Identify nearest village
        2. Agent 1 — movement / risk prediction
        3. Agent 2 — alert generation
        4. Agent 3 — incident + approval queue
        5. Agent 5 — hotspot refresh
        Returns a pipeline result dict.
        """
        pipeline_id = f"PIP-{uuid.uuid4().hex[:6].upper()}"
        self._log("Orchestrator", f"Pipeline {pipeline_id} started for {sighting.get('id','new')}", 1.0)

        # Assign an id if new
        if not sighting.get("id"):
            sighting["id"] = f"S{len(self.sightings)+1:03d}"
        self.sightings.append(sighting)

        # Step 1 — resolve village
        village = self._find_village(sighting.get("nearest_village")) or self.villages[0]

        # Step 2 — Movement Agent
        movement_result = self.movement_agent.process(
            sighting, village, self.sightings, self.incidents
        )
        self._log("MovementAgent",
                  f"Risk={movement_result['risk_score']} ({movement_result['risk_level']}) for {village['name']}",
                  movement_result["confidence"])

        # Step 3 — Alert Agent
        alert = self.alert_agent.process(movement_result, sighting, village)
        self.alerts.append(alert)
        self._log("AlertAgent",
                  f"{'Broadcast' if alert['broadcast'] else 'Logged'} {alert['severity']} alert — {village['name']}",
                  alert["confidence"])

        # Step 4 — Response Agent (only for MEDIUM/HIGH)
        incident = None
        if movement_result["risk_level"] in ("MEDIUM", "HIGH"):
            incident = self.response_agent.process(
                alert, sighting, village, self.response_teams, self.pending_approvals
            )
            self.incidents.append(incident)
            self._log("ResponseAgent",
                      f"Incident {incident['id']} created — team {incident['recommended_team_name']} recommended",
                      alert["confidence"])
        else:
            self._log("ResponseAgent", "Risk LOW — no incident created", alert["confidence"])

        # Step 5 — Hotspot refresh
        hotspot_result = self._refresh_hotspots()
        self._log("HotspotAgent",
                  f"{len(hotspot_result['hotspots'])} clusters recalculated",
                  hotspot_result["confidence"])

        self._log("Orchestrator", f"Pipeline {pipeline_id} complete", movement_result["confidence"])

        return {
            "pipeline_id":    pipeline_id,
            "sighting":       sighting,
            "village":        village,
            "movement":       movement_result,
            "alert":          alert,
            "incident":       incident,
            "hotspots":       hotspot_result["hotspots"][:3],
            "pending_approvals": len(self.pending_approvals),
            "timestamp":      datetime.utcnow().isoformat(),
        }

    # ==================================================================
    # Compensation claim
    # ==================================================================

    def submit_compensation_claim(self, claim_data: dict) -> dict:
        claim = self.compensation_agent.process(claim_data, self.pending_approvals)
        self.compensation_claims.append(claim)
        self._log("CompensationAgent",
                  f"Claim {claim['claim_id']} drafted — ₹{claim['preliminary_amount_inr']:,}",
                  claim["confidence"])
        return claim

    # ==================================================================
    # Human approval
    # ==================================================================

    def approve_action(self, action_id: str, decision: str, officer_note: str = "") -> dict:
        """
        decision: 'APPROVE' or 'REJECT'
        """
        for item in self.pending_approvals:
            if item["action_id"] == action_id:
                item["status"]        = decision
                item["officer_note"]  = officer_note
                item["decided_at"]    = datetime.utcnow().isoformat()

                if decision == "APPROVE" and item["action_type"] == "DISPATCH_TEAM":
                    # Actually assign the team to the incident
                    inc_id = item.get("incident_id")
                    for inc in self.incidents:
                        if inc["id"] == inc_id:
                            self.response_agent.update_status(
                                inc, "ASSIGNED", self.response_teams,
                                f"Officer approved dispatch of {item['recommended_team_name']}"
                            )
                            break

                self.approved_actions.append(item)
                self.pending_approvals.remove(item)
                self._log("Orchestrator",
                          f"Action {action_id} {decision} by officer",
                          item.get("confidence", 1.0))
                return {"success": True, "action": item}

        return {"success": False, "error": f"Action {action_id} not found"}

    # ==================================================================
    # Incident status update
    # ==================================================================

    def update_incident(self, incident_id: str, new_status: str, notes: str = "") -> dict:
        for inc in self.incidents:
            if inc["id"] == incident_id:
                self.response_agent.update_status(inc, new_status, self.response_teams, notes)
                self._log("ResponseAgent", f"Incident {incident_id} → {new_status}", 1.0)
                return inc
        return {}

    # ==================================================================
    # Demo scenario — 8-step end-to-end walkthrough
    # ==================================================================

    def run_demo_scenario(self) -> dict:
        """
        Simulate a complete pipeline: lion sighting near Sasan Gir at night.
        Returns step-by-step log for the UI.
        """
        steps = []

        steps.append({
            "step": 1, "agent": "Field Sensor / Guard",
            "action": "New sighting reported",
            "detail": "Forest Guard Ramesh K. reports: Male Asiatic Lion, 0.7 km from Sasan Gir village pen area. Time: 22:30 IST.",
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
        })

        demo_sighting = {
            "id": f"DEMO-{uuid.uuid4().hex[:4].upper()}",
            "species": "Asiatic Lion",
            "lat": 21.1195, "lon": 70.6110,
            "nearest_village": "V001",
            "distance_km": 0.7,
            "timestamp": datetime.utcnow().isoformat(),
            "time_of_day": "night",
            "observer": "Forest Guard Ramesh K.",
            "notes": "DEMO: Male lion near livestock pen — demo scenario",
            "verified": True,
        }

        steps.append({
            "step": 2, "agent": "Orchestrator",
            "action": "Event routed to pipeline",
            "detail": f"Sighting {demo_sighting['id']} ingested. Routing to MovementAgent.",
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
        })

        village = self._find_village("V001")
        movement = self.movement_agent.process(
            demo_sighting, village, self.sightings, self.incidents
        )
        steps.append({
            "step": 3, "agent": "MovementAgent",
            "action": "Movement & risk prediction",
            "detail": (
                f"Risk Score: {movement['risk_score']} — {movement['risk_level']}. "
                f"Movement Probability: {movement['movement_probability']:.0%}. "
                f"Predicted Zone: {movement['predicted_risk_zone']}."
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "risk_score": movement["risk_score"],
                "risk_level": movement["risk_level"],
                "confidence": movement["confidence"],
            },
        })

        alert = self.alert_agent.process(movement, demo_sighting, village)
        self.alerts.append(alert)
        steps.append({
            "step": 4, "agent": "AlertAgent",
            "action": f"{'Broadcast' if alert['broadcast'] else 'Logged'} {alert['severity']} alert",
            "detail": alert["en_text"],
            "gu_text": alert["gu_text"],
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "alert_id": alert["alert_id"],
                "severity": alert["severity"],
                "broadcast": alert["broadcast"],
            },
        })

        incident = self.response_agent.process(
            alert, demo_sighting, village, self.response_teams, self.pending_approvals
        )
        self.incidents.append(demo_sighting)
        steps.append({
            "step": 5, "agent": "ResponseAgent",
            "action": f"Incident ticket {incident['id']} created",
            "detail": (
                f"Severity: {incident['severity']}. "
                f"Nearest team: {incident['recommended_team_name']} "
                f"({incident['distance_to_team_km']} km away). "
                f"Dispatch approval requested from officer."
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "incident_id": incident["id"],
                "recommended_team": incident["recommended_team_name"],
                "approval_id": incident.get("approval_id"),
            },
        })

        steps.append({
            "step": 6, "agent": "Officer (Human-in-the-Loop)",
            "action": "Approval queue — officer reviews dispatch recommendation",
            "detail": (
                f"AI Recommendation: Dispatch {incident['recommended_team_name']}. "
                f"Confidence: {alert['confidence']:.0%}. "
                "Officer reviews and APPROVES or OVERRIDES. "
                "⚠️ No autonomous dispatch — human decision required."
            ),
            "status": "AWAITING_HUMAN", "timestamp": datetime.utcnow().isoformat(),
        })

        hotspot_result = self._refresh_hotspots()
        steps.append({
            "step": 7, "agent": "HotspotAgent",
            "action": "Hotspot clusters recalculated",
            "detail": (
                f"{len(hotspot_result['hotspots'])} conflict zones identified. "
                f"Daily summary: {hotspot_result['daily_summary']}"
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "cluster_count": len(hotspot_result["hotspots"]),
                "top_hotspot": hotspot_result["hotspots"][0]["center_village"] if hotspot_result["hotspots"] else "N/A",
            },
        })

        steps.append({
            "step": 8, "agent": "Orchestrator",
            "action": "Audit log updated — pipeline complete",
            "detail": (
                "Full pipeline executed: PREDICT → ALERT → COORDINATE → LEARN. "
                "All actions logged. Human approval enforced at dispatch stage. "
                "System ready for next event."
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
        })

        self._log("Orchestrator", "Demo scenario completed", movement["confidence"])

        return {
            "scenario": "Lion Sighting — Sasan Gir Night Alert",
            "steps": steps,
            "sighting": demo_sighting,
            "alert": alert,
            "incident": incident,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ==================================================================
    # Dashboard data
    # ==================================================================

    def get_dashboard(self) -> dict:
        active_incidents  = sum(1 for i in self.incidents if i.get("status") not in ("RESOLVED",))
        high_risk         = sum(1 for r in self.risk_assessments if r["risk_level"] == "HIGH")
        avg_confidence    = (
            sum(r["confidence"] for r in self.risk_assessments) / max(1, len(self.risk_assessments))
        )
        pending_approvals = len(self.pending_approvals)

        # Enrich villages with risk level
        risk_map = {r["village_id"]: r for r in self.risk_assessments}
        villages_enriched = []
        for v in self.villages:
            r = risk_map.get(v["id"], {})
            villages_enriched.append({
                **v,
                "risk_score":  r.get("risk_score", 0.0),
                "risk_level":  r.get("risk_level", "LOW"),
                "confidence":  r.get("confidence", 0.70),
            })

        recent_sightings = sorted(
            self.sightings, key=lambda s: s.get("timestamp", ""), reverse=True
        )[:6]

        recent_alerts = sorted(
            self.alerts, key=lambda a: a.get("timestamp", ""), reverse=True
        )[:5]

        recent_incidents = sorted(
            self.incidents, key=lambda i: i.get("timestamp", ""), reverse=True
        )[:6]

        return {
            "stats": {
                "active_incidents":  active_incidents,
                "high_risk_zones":   high_risk,
                "avg_confidence":    round(avg_confidence, 2),
                "pending_approvals": pending_approvals,
                "total_sightings":   len(self.sightings),
                "total_incidents":   len(self.incidents),
            },
            "villages":          villages_enriched,
            "recent_sightings":  recent_sightings,
            "recent_alerts":     recent_alerts,
            "recent_incidents":  recent_incidents,
            "agent_statuses":    self._get_all_agent_statuses(),
        }

    def get_hotspot_data(self) -> dict:
        return self._refresh_hotspots()

    def _refresh_hotspots(self) -> dict:
        result = self.hotspot_agent.process(self.incidents, self.sightings, self.villages)
        self.last_hotspot_result = result
        return result

    def _get_all_agent_statuses(self) -> list:
        return [
            self.movement_agent.get_status(),
            self.alert_agent.get_status(),
            self.response_agent.get_status(),
            self.compensation_agent.get_status(),
            self.hotspot_agent.get_status(),
        ]

    def _find_village(self, village_id: str):
        for v in self.villages:
            if v["id"] == village_id:
                return v
        return None

    def _log(self, agent: str, action: str, confidence: float):
        self.audit_log.append({
            "agent":      agent,
            "action":     action,
            "confidence": confidence,
            "timestamp":  datetime.utcnow().isoformat(),
        })
        # Mirror to agent_logs list (used by the API)
        self.agent_logs.append({
            "agent":      agent,
            "action":     action,
            "confidence": confidence,
            "timestamp":  datetime.utcnow().isoformat(),
        })
