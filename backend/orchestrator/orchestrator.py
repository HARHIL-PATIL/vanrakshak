"""
VanRakshak AI — Central Orchestration Layer
=============================================
The Orchestrator is the single entry point for all multi-agent workflows.
It maintains shared state and coordinates the five specialist agents.

Workflow: PREDICT → ALERT → COORDINATE
  1. MovementPredictionAgent  → risk assessment
  2. AlertAgent               → bilingual alert (if risk ≥ threshold)
  3. ResponseCoordinationAgent→ incident ticket (awaiting officer approval)
  4. All results queued in pending_approvals for human-in-the-loop review
  5. CompensationAssistantAgent & HotspotDashboardAgent run independently

IMPORTANT: Every consequential action sets human_approval_required=True.
No field dispatch, alert broadcast, or claim action is taken without
explicit officer approval recorded in the system.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from agents.movement_agent     import MovementPredictionAgent
from agents.alert_agent        import AlertAgent
from agents.response_agent     import ResponseCoordinationAgent
from agents.compensation_agent import CompensationAssistantAgent
from agents.hotspot_agent      import HotspotDashboardAgent
from data.sample_data          import (
    SAMPLE_SIGHTINGS,
    SAMPLE_VILLAGES,
    SAMPLE_INCIDENTS,
    SAMPLE_RESPONSE_TEAMS,
    SAMPLE_AGENT_LOGS,
    get_village_by_id,
)


class VanRakshakOrchestrator:
    """
    Central Orchestration Layer — coordinates all VanRakshak agents.

    Architecture:
        - shared_state : dict holding all live incidents, assessments,
                         alerts, approvals, and workflow results
        - agents       : singleton instances of all five specialist agents
        - agent_logs   : chronological action log across all agents
        - pending_approvals : queue of items awaiting officer review

    Thread-safety: single-process prototype — not thread-safe in production.
    """

    def __init__(self):
        # ── Agent singletons ──────────────────────────────────────────────
        self.agents: dict[str, Any] = {
            "movement":     MovementPredictionAgent(),
            "alert":        AlertAgent(),
            "response":     ResponseCoordinationAgent(),
            "compensation": CompensationAssistantAgent(),
            "hotspot":      HotspotDashboardAgent(),
        }

        # ── Shared state ─────────────────────────────────────────────────
        self.shared_state: dict[str, Any] = {
            "sightings":     list(SAMPLE_SIGHTINGS),   # accumulated sightings
            "incidents":     list(SAMPLE_INCIDENTS),    # all incidents
            "assessments":   [],                        # RiskAssessment results
            "alerts":        [],                        # AlertMessage results
            "tickets":       [],                        # IncidentTicket results
            "claims":        [],                        # CompensationClaim results
            "approvals":     [],                        # OfficerApproval records
            "demo_results":  [],                        # demo scenario step results
        }

        # ── Logs and approval queue ───────────────────────────────────────
        self.agent_logs:        list[dict] = list(SAMPLE_AGENT_LOGS)
        self.pending_approvals: list[dict] = []

        # ── Demo scenario state ───────────────────────────────────────────
        self._demo_ran: bool = False
        self._demo_result: Optional[dict] = None

    # ═══════════════════════════════════════════════════════════════════════
    # Primary workflow: process a new sighting
    # ═══════════════════════════════════════════════════════════════════════

    def process_sighting(self, sighting_data: dict) -> dict:
        """
        Full PREDICT → ALERT → COORDINATE workflow for a new sighting.

        Steps:
            1.  Persist sighting to shared state
            2.  Determine target village (nearest or specified)
            3.  Call movement_agent.analyze()
            4.  Persist risk assessment to shared state
            5.  Call alert_agent.generate_alert() if risk ≥ threshold
            6.  Persist alert to shared state
            7.  Call response_agent.create_incident_ticket()
            8.  Persist ticket + add to pending_approvals queue
            9.  Log all agent actions
            10. Return complete workflow result dict

        Args:
            sighting_data : dict — must include lat, lon, species.
                            sighting_id is auto-generated if absent.

        Returns:
            Workflow result dict with all step outputs.
        """
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"
        started_at  = datetime.now(timezone.utc)

        # ── Step 1: Persist sighting ───────────────────────────────────────
        if "sighting_id" not in sighting_data or not sighting_data["sighting_id"]:
            sighting_data["sighting_id"] = f"SGT-{uuid.uuid4().hex[:6].upper()}"
        if "timestamp" not in sighting_data:
            sighting_data["timestamp"] = started_at.isoformat()
        if "is_demo" not in sighting_data:
            sighting_data["is_demo"] = True

        self.shared_state["sightings"].append(sighting_data)

        # ── Step 2: Resolve target village ────────────────────────────────
        village_id = sighting_data.get("nearest_village_id")
        if not village_id:
            village_id = self._nearest_village(
                sighting_data["lat"], sighting_data["lon"]
            )
        village = get_village_by_id(village_id) or SAMPLE_VILLAGES[0]

        # ── Step 3: Movement Agent ─────────────────────────────────────────
        assessment = self.agents["movement"].analyze(
            sighting_data=sighting_data,
            village_id=village_id,
        )
        self._log_agent_action(
            agent="movement_agent",
            action="analyze_sighting",
            input_ref=sighting_data["sighting_id"],
            output_summary=(
                f"{assessment['consensus_risk_level']} risk for "
                f"{village['name']}, score="
                f"{assessment['risk_assessment']['risk_score']}, "
                f"confidence={assessment['risk_assessment']['confidence']}"
            ),
            escalation_required=assessment["consensus_risk_level"] == "HIGH",
        )

        # ── Step 4: Persist assessment ─────────────────────────────────────
        self.shared_state["assessments"].append(assessment)

        # ── Step 5 & 6: Alert Agent ────────────────────────────────────────
        alert_result = None
        if self.agents["alert"].should_alert(
            assessment["risk_assessment"]["risk_score"]
        ):
            alert_result = self.agents["alert"].generate_alert(
                risk_assessment=assessment,
                village=village,
                species=sighting_data.get("species", "Unknown"),
            )
            self.shared_state["alerts"].append(alert_result)
            self._log_agent_action(
                agent="alert_agent",
                action="generate_alert",
                input_ref=sighting_data["sighting_id"],
                output_summary=(
                    f"{alert_result['severity']} alert issued for "
                    f"{village['name']} — broadcast_required="
                    f"{alert_result['broadcast_required']}"
                ),
                escalation_required=alert_result["severity"] == "HIGH",
            )

        # ── Step 7 & 8: Response Agent ─────────────────────────────────────
        ticket = self.agents["response"].create_incident_ticket(
            sighting=sighting_data,
            risk_assessment=assessment,
            village_id=village_id,
        )
        self.shared_state["tickets"].append(ticket)
        self._log_agent_action(
            agent="response_agent",
            action="create_incident_ticket",
            input_ref=sighting_data["sighting_id"],
            output_summary=(
                f"Ticket {ticket['ticket_id']} created — "
                f"recommended team: {ticket['recommended_team_name']} "
                f"({ticket['distance_km']} km) — AWAITING OFFICER APPROVAL"
            ),
            escalation_required=True,
        )

        # Add to pending approvals queue
        approval = self._create_pending_approval(
            ticket_id=ticket["ticket_id"],
            incident_id=ticket["incident_id"],
            sighting_id=sighting_data["sighting_id"],
            risk_level=assessment["consensus_risk_level"],
        )
        self.shared_state["approvals"].append(approval)

        # ── Step 9 & 10: Return workflow result ────────────────────────────
        return {
            "workflow_id":       workflow_id,
            "sighting_id":       sighting_data["sighting_id"],
            "village_id":        village_id,
            "village_name":      village["name"],
            "risk_level":        assessment["consensus_risk_level"],
            "steps_completed":   ["movement_agent", "alert_agent", "response_agent"],
            "risk_assessment":   assessment,
            "alert":             alert_result,
            "incident_ticket":   ticket,
            "pending_approval":  approval,
            "human_approval_required": True,
            "note": (
                "Workflow complete. All outputs are RECOMMENDATIONS. "
                "Officer approval required at: POST /api/agents/approve"
            ),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "is_demo": True,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Officer approval / override
    # ═══════════════════════════════════════════════════════════════════════

    def officer_approve(
        self,
        approval_id: str,
        officer_id: str,
        decision: str,                    # "APPROVED" | "REJECTED" | "OVERRIDE"
        override_data: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Process an officer approval, rejection, or override for a pending action.

        Steps:
            1. Find the approval record by ID
            2. Validate decision value
            3. Update approval record
            4. If APPROVED / OVERRIDE → update incident ticket status
            5. Log the officer action

        Args:
            approval_id   : ID of the pending approval record
            officer_id    : Forest Officer ID
            decision      : "APPROVED" | "REJECTED" | "OVERRIDE"
            override_data : Optional dict with fields to override (team, priority, etc.)
            notes         : Optional officer notes

        Returns:
            Result dict with updated approval and next-step info
        """
        # Find approval record
        approval = next(
            (a for a in self.pending_approvals if a["approval_id"] == approval_id),
            None,
        )
        if approval is None:
            # Also check shared_state approvals
            approval = next(
                (a for a in self.shared_state["approvals"] if a["approval_id"] == approval_id),
                None,
            )
        if approval is None:
            return {
                "success": False,
                "error":   f"Approval record {approval_id} not found",
                "is_demo": True,
            }

        valid_decisions = ("APPROVED", "REJECTED", "OVERRIDE")
        if decision not in valid_decisions:
            return {
                "success": False,
                "error":   f"Invalid decision '{decision}'. Must be one of {valid_decisions}",
                "is_demo": True,
            }

        # Update approval record
        approval["decision"]     = decision
        approval["officer_id"]   = officer_id
        approval["decided_at"]   = datetime.now(timezone.utc).isoformat()
        approval["notes"]        = notes
        approval["override_data"]= override_data

        # Update ticket status if approved
        ticket_id = approval.get("ticket_id")
        status_result = None
        if ticket_id and decision in ("APPROVED", "OVERRIDE"):
            status_result = self.agents["response"].update_incident_status(
                ticket_id=ticket_id,
                new_status="ASSIGNED",
                officer_id=officer_id,
                notes=notes,
            )

        self._log_agent_action(
            agent="orchestrator",
            action=f"officer_{decision.lower()}",
            input_ref=approval_id,
            output_summary=(
                f"Officer {officer_id} {decision} approval {approval_id}. "
                f"Ticket {ticket_id} → ASSIGNED" if decision == "APPROVED" else
                f"Officer {officer_id} {decision} approval {approval_id}."
            ),
            escalation_required=False,
        )

        return {
            "success":        True,
            "approval_id":    approval_id,
            "decision":       decision,
            "officer_id":     officer_id,
            "ticket_id":      ticket_id,
            "ticket_update":  status_result,
            "decided_at":     approval["decided_at"],
            "notes":          notes,
            "is_demo":        True,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Demo scenario
    # ═══════════════════════════════════════════════════════════════════════

    def run_demo_scenario(self) -> dict:
        """
        Execute the full VanRakshak demo scenario step by step.

        Scenario: Asiatic Lion sighted near Sasan Gir village at dawn.
        Demonstrates the complete PREDICT → ALERT → COORDINATE workflow
        with human-in-the-loop approval.

        Returns:
            Dict with each step's result, timestamps, and final state summary.
        """
        demo_id    = f"DEMO-{uuid.uuid4().hex[:6].upper()}"
        started_at = datetime.now(timezone.utc)
        steps      = []

        def record_step(name: str, result: Any) -> None:
            steps.append({
                "step":      name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result":    result,
            })

        # ── Demo Step 1: Incoming sighting ─────────────────────────────────
        demo_sighting = {
            "sighting_id":        f"DEMO-SGT-{uuid.uuid4().hex[:6].upper()}",
            "species":            "Asiatic Lion",
            "lat":                21.1300,
            "lon":                70.5600,
            "timestamp":          started_at.isoformat(),
            "confidence":         0.95,
            "source":             "camera_trap",
            "count":              2,
            "nearest_village_id": "VLG001",
            "notes":              "Demo scenario: Adult lion pair at forest edge",
            "is_demo":            True,
        }
        record_step("1_sighting_received", {
            "description": "New camera trap alert: Asiatic Lion near Sasan Gir",
            "sighting":    demo_sighting,
        })

        # ── Demo Step 2: Full orchestrated workflow ────────────────────────
        workflow_result = self.process_sighting(demo_sighting)
        record_step("2_movement_prediction", {
            "description": "Agent 1 — Movement & Risk Assessment",
            "risk_level":  workflow_result["risk_level"],
            "risk_score":  workflow_result["risk_assessment"]["risk_assessment"]["risk_score"],
            "distance_km": workflow_result["risk_assessment"]["distance_km"],
        })

        if workflow_result.get("alert"):
            alert = workflow_result["alert"]
            record_step("3_alert_generated", {
                "description":    "Agent 2 — Bilingual Alert Generated",
                "severity":       alert["severity"],
                "message_en":     alert["message_english"],
                "message_gu":     alert["message_gujarati"],
                "safety_actions": alert["safety_actions"][:3],
                "status":         "PENDING OFFICER BROADCAST APPROVAL",
            })
        else:
            record_step("3_alert_generated", {
                "description": "Agent 2 — Risk below broadcast threshold; alert logged only",
                "status":      "NO BROADCAST",
            })

        ticket = workflow_result["incident_ticket"]
        record_step("4_incident_ticket_created", {
            "description":     "Agent 3 — Incident Ticket Created",
            "ticket_id":       ticket["ticket_id"],
            "recommended_team":ticket["recommended_team_name"],
            "distance_km":     ticket["distance_km"],
            "status":          "AWAITING OFFICER APPROVAL",
        })

        # ── Demo Step 3: Simulated officer approval ────────────────────────
        approval = workflow_result["pending_approval"]
        approval_result = self.officer_approve(
            approval_id=approval["approval_id"],
            officer_id="DEMO-OFFICER-001",
            decision="APPROVED",
            notes="Demo approval — dispatching nearest available team",
        )
        record_step("5_officer_approval", {
            "description": "Human-in-the-Loop: Officer reviews and APPROVES dispatch",
            "officer_id":  "DEMO-OFFICER-001",
            "decision":    "APPROVED",
            "ticket_id":   approval_result.get("ticket_id"),
            "note":        "In production: officer reviews alert + ticket before approving",
        })

        # ── Demo Step 4: Compensation claim initiation ─────────────────────
        claim = self.agents["compensation"].start_claim(
            incident_id=ticket["incident_id"],
            villager_info={
                "claimant_name":  "Demo Villager (Sasan Gir)",
                "village_id":     "VLG001",
                "contact_number": "+91-98765-00001",
            },
            loss_details={
                "loss_type":         "livestock_predation",
                "loss_description":  "Demo: 1 cattle allegedly lost near forest edge",
                "species_responsible": "Asiatic Lion",
                "estimated_loss_value": 25000,
            },
        )
        self.shared_state["claims"].append(claim)
        record_step("6_compensation_draft", {
            "description":       "Agent 4 — Compensation Claim Draft Prepared",
            "claim_id":          claim["claim_id"],
            "documents_required":len(claim["document_checklist"]),
            "status":            "DRAFT — PENDING OFFICER REVIEW",
            "disclaimer":        claim["disclaimer"],
        })

        # ── Demo Step 5: Hotspot analysis ──────────────────────────────────
        hotspot_result = self.agents["hotspot"].analyze_hotspots(top_n=3)
        record_step("7_hotspot_analysis", {
            "description":    "Agent 5 — Hotspot Dashboard Updated",
            "top_hotspots":   [
                f"{h['villages'][0] if h['villages'] else 'Zone'} ({h['risk_level']})"
                for h in hotspot_result["hotspots"][:3]
            ],
            "overall_trend":  hotspot_result["overall_trend"],
            "summary":        hotspot_result["summary"],
        })

        # ── Final state ────────────────────────────────────────────────────
        self._demo_ran    = True
        self._demo_result = {
            "demo_id":          demo_id,
            "scenario":         "Asiatic Lion sighting near Sasan Gir — Full Workflow Demo",
            "steps":            steps,
            "total_steps":      len(steps),
            "agents_involved":  ["movement_agent", "alert_agent", "response_agent",
                                 "compensation_agent", "hotspot_agent"],
            "workflow_id":      workflow_result["workflow_id"],
            "final_risk_level": workflow_result["risk_level"],
            "started_at":       started_at.isoformat(),
            "completed_at":     datetime.now(timezone.utc).isoformat(),
            "is_demo":          True,
        }
        return self._demo_result

    def get_demo_status(self) -> dict:
        """Return the current demo scenario state."""
        if not self._demo_ran:
            return {
                "demo_ran": False,
                "message":  "Demo has not been executed yet. POST /api/demo/run to start.",
                "is_demo":  True,
            }
        return {
            "demo_ran": True,
            "result":   self._demo_result,
            "is_demo":  True,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Dashboard data
    # ═══════════════════════════════════════════════════════════════════════

    def get_dashboard_data(self) -> dict:
        """Aggregate data for the main dashboard endpoint."""
        from datetime import timedelta
        now = datetime.now(timezone.utc)

        # Recent sightings (last 30 days)
        recent_sightings = self.shared_state["sightings"][-10:]

        # Active incidents (from sample + any created in session)
        active_incidents = [
            i for i in self.shared_state["incidents"]
            if i.get("status") in ("NEW", "ASSIGNED", "IN_PROGRESS")
        ]

        # High-risk villages
        high_risk = [v for v in SAMPLE_VILLAGES if v["risk_zone"] == "HIGH"]

        # Alerts today
        alerts_today = [
            a for a in self.shared_state["alerts"]
            if a.get("issued_at", "")[:10] == now.date().isoformat()
        ]

        # Pending approvals count
        pending = [
            a for a in self.shared_state["approvals"]
            if a.get("decision", "PENDING") == "PENDING"
        ]

        # Agent status
        agent_statuses = {
            name: {
                "status":   "ACTIVE",
                "last_run": next(
                    (log["timestamp"] for log in reversed(self.agent_logs)
                     if log["agent"] == name + "_agent"),
                    None,
                ),
                "is_demo": True,
            }
            for name in ["movement", "alert", "response", "compensation", "hotspot"]
        }

        return {
            "stats": {
                "total_sightings_30d":       len(self.shared_state["sightings"]),
                "active_incidents":          len(active_incidents),
                "high_risk_villages":        len(high_risk),
                "alerts_issued_today":       len(alerts_today),
                "pending_approvals":         len(pending),
                "compensation_claims_pending": sum(
                    1 for c in self.shared_state["claims"]
                    if c.get("status") in ("DRAFT", "SUBMITTED", "UNDER_REVIEW")
                ),
            },
            "active_incidents":  active_incidents[:5],
            "recent_sightings":  recent_sightings[-5:],
            "risk_zones":        [
                {"village_id": v["village_id"], "name": v["name"],
                 "lat": v["lat"], "lon": v["lon"], "risk_zone": v["risk_zone"]}
                for v in SAMPLE_VILLAGES
            ],
            "agent_statuses":    agent_statuses,
            "recent_alerts":     self.shared_state["alerts"][-5:],
            "pending_approvals": pending[:10],
            "is_demo":           True,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Private helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _nearest_village(self, lat: float, lon: float) -> str:
        """Find the nearest village ID to the given coordinates."""
        from ml.risk_engine import haversine_km as hv
        nearest = min(
            SAMPLE_VILLAGES,
            key=lambda v: hv(lat, lon, v["lat"], v["lon"]),
        )
        return nearest["village_id"]

    def _create_pending_approval(
        self,
        ticket_id: str,
        incident_id: str,
        sighting_id: str,
        risk_level: str,
    ) -> dict:
        """Create a new pending approval record and enqueue it."""
        approval = {
            "approval_id":  f"APR-{uuid.uuid4().hex[:8].upper()}",
            "ticket_id":    ticket_id,
            "incident_id":  incident_id,
            "sighting_id":  sighting_id,
            "risk_level":   risk_level,
            "officer_id":   None,
            "decision":     "PENDING",
            "override_data":None,
            "decided_at":   None,
            "notes":        None,
            "created_at":   datetime.now(timezone.utc).isoformat(),
            "is_demo":      True,
        }
        self.pending_approvals.append(approval)
        return approval

    def _log_agent_action(
        self,
        agent: str,
        action: str,
        input_ref: str,
        output_summary: str,
        escalation_required: bool = False,
        confidence: Optional[float] = None,
    ) -> None:
        """Append a structured log entry to agent_logs."""
        log_entry = {
            "log_id":             f"LOG-{uuid.uuid4().hex[:8].upper()}",
            "agent":              agent,
            "action":             action,
            "input_ref":          input_ref,
            "output_summary":     output_summary,
            "timestamp":          datetime.now(timezone.utc).isoformat(),
            "confidence":         confidence,
            "escalation_required":escalation_required,
            "escalation_status":  "PENDING" if escalation_required else "NONE",
            "is_demo":            True,
        }
        self.agent_logs.append(log_entry)
