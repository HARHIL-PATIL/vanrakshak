# ============================================================
# VanRakshak AI — Flask Application Entry Point
# Human-Wildlife Conflict Mitigation Platform — Gir Forest
# PROTOTYPE / DEMO VERSION
# Run: python app.py
# ============================================================

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, render_template
from agents.orchestrator import Orchestrator
from agents.compensation_agent import CompensationAgent

app = Flask(__name__, template_folder="templates")
app.config["JSON_SORT_KEYS"] = False

# Single orchestrator instance (in-memory state)
orch = Orchestrator()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _ok(data):
    return jsonify({"success": True, "data": data})


def _err(msg, code=400):
    return jsonify({"success": False, "error": msg}), code


# ===========================================================================
# HTML Front-end
# ===========================================================================

@app.route("/")
def index():
    return render_template("index.html")


# ===========================================================================
# Dashboard
# ===========================================================================

@app.route("/api/dashboard")
def api_dashboard():
    return _ok(orch.get_dashboard())


# ===========================================================================
# Villages
# ===========================================================================

@app.route("/api/villages")
def api_villages():
    risk_map = {r["village_id"]: r for r in orch.risk_assessments}
    result = []
    for v in orch.villages:
        r = risk_map.get(v["id"], {})
        result.append({
            **v,
            "risk_score": r.get("risk_score", 0.0),
            "risk_level": r.get("risk_level", "LOW"),
            "confidence": r.get("confidence", 0.70),
        })
    return _ok(result)


# ===========================================================================
# Sightings
# ===========================================================================

@app.route("/api/sightings", methods=["GET"])
def api_sightings_get():
    sightings = sorted(orch.sightings, key=lambda s: s.get("timestamp", ""), reverse=True)
    return _ok(sightings)


@app.route("/api/sightings", methods=["POST"])
def api_sightings_post():
    data = request.get_json(silent=True) or {}
    required = ["species", "lat", "lon", "nearest_village", "distance_km", "time_of_day"]
    for field in required:
        if field not in data:
            return _err(f"Missing required field: {field}")

    pipeline_result = orch.process_sighting(data)
    return _ok(pipeline_result), 201


# ===========================================================================
# Incidents
# ===========================================================================

@app.route("/api/incidents", methods=["GET"])
def api_incidents():
    incidents = sorted(orch.incidents, key=lambda i: i.get("timestamp", ""), reverse=True)
    return _ok(incidents)


@app.route("/api/incidents/<incident_id>/update", methods=["POST"])
def api_incident_update(incident_id):
    data       = request.get_json(silent=True) or {}
    new_status = data.get("status")
    notes      = data.get("notes", "")
    if not new_status:
        return _err("Missing 'status' field")
    updated = orch.update_incident(incident_id, new_status, notes)
    if not updated:
        return _err(f"Incident {incident_id} not found", 404)
    return _ok(updated)


# ===========================================================================
# Alerts
# ===========================================================================

@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    alerts = sorted(orch.alerts, key=lambda a: a.get("timestamp", ""), reverse=True)
    # Seed alerts from sample data if none yet generated
    if not alerts:
        from data.sample_data import SIGHTINGS, VILLAGES
        from agents.movement_agent import MovementAgent
        from agents.alert_agent    import AlertAgent
        ma = MovementAgent()
        aa = AlertAgent()
        village_map = {v["id"]: v for v in VILLAGES}
        for s in SIGHTINGS[:5]:
            v = village_map.get(s["nearest_village"])
            if not v:
                continue
            mv = ma.process(s, v, SIGHTINGS, orch.incidents)
            al = aa.process(mv, s, v)
            alerts.append(al)
    return _ok(alerts)


@app.route("/api/alerts/generate", methods=["POST"])
def api_alert_generate():
    """Generate a new alert for a given village/sighting combo."""
    data = request.get_json(silent=True) or {}
    village_id  = data.get("village_id", "V001")
    sighting_id = data.get("sighting_id")

    village = next((v for v in orch.villages if v["id"] == village_id), orch.villages[0])
    sighting = (
        next((s for s in orch.sightings if s["id"] == sighting_id), None)
        if sighting_id
        else orch.sightings[0]
    )
    if not sighting:
        return _err("No sighting found")

    from agents.movement_agent import MovementAgent
    mv_result = MovementAgent().process(sighting, village, orch.sightings, orch.incidents)
    alert     = orch.alert_agent.process(mv_result, sighting, village)
    orch.alerts.append(alert)
    return _ok(alert), 201


# ===========================================================================
# Hotspots
# ===========================================================================

@app.route("/api/hotspots")
def api_hotspots():
    return _ok(orch.get_hotspot_data())


# ===========================================================================
# Agent status
# ===========================================================================

@app.route("/api/agents/status")
def api_agents_status():
    statuses = [
        orch.movement_agent.get_status(),
        orch.alert_agent.get_status(),
        orch.response_agent.get_status(),
        orch.compensation_agent.get_status(),
        orch.hotspot_agent.get_status(),
    ]
    return _ok(statuses)


@app.route("/api/agents/logs")
def api_agents_logs():
    logs = sorted(orch.agent_logs, key=lambda l: l.get("timestamp", ""), reverse=True)[:50]
    return _ok(logs)


# ===========================================================================
# Approval queue (Human-in-the-Loop)
# ===========================================================================

@app.route("/api/approval-queue")
def api_approval_queue():
    return _ok(orch.pending_approvals)


@app.route("/api/approve/<action_id>", methods=["POST"])
def api_approve(action_id):
    data         = request.get_json(silent=True) or {}
    decision     = data.get("decision", "APPROVE").upper()
    officer_note = data.get("officer_note", "")
    if decision not in ("APPROVE", "REJECT"):
        return _err("decision must be APPROVE or REJECT")
    result = orch.approve_action(action_id, decision, officer_note)
    if not result["success"]:
        return _err(result["error"], 404)
    return _ok(result)


# ===========================================================================
# Compensation
# ===========================================================================

@app.route("/api/compensation/claims")
def api_claims_list():
    claims = sorted(orch.compensation_claims, key=lambda c: c.get("timestamp", ""), reverse=True)
    return _ok(claims)


@app.route("/api/compensation/submit", methods=["POST"])
def api_claim_submit():
    data = request.get_json(silent=True) or {}
    required = ["claimant_name", "village_id", "livestock_type", "livestock_count"]
    for field in required:
        if field not in data:
            return _err(f"Missing required field: {field}")
    claim = orch.submit_compensation_claim(data)
    return _ok(claim), 201


@app.route("/api/compensation/rates")
def api_comp_rates():
    return _ok(CompensationAgent.get_compensation_rates())


@app.route("/api/compensation/required-docs")
def api_required_docs():
    return _ok(CompensationAgent.get_required_docs())


# ===========================================================================
# Demo scenario
# ===========================================================================

@app.route("/api/demo/run")
def api_demo_run():
    result = orch.run_demo_scenario()
    return _ok(result)


# ===========================================================================
# Audit log
# ===========================================================================

@app.route("/api/audit-log")
def api_audit_log():
    logs = list(reversed(orch.audit_log[-100:]))
    return _ok(logs)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  VanRakshak AI — Human-Wildlife Conflict Mitigation")
    print("  Gir Forest Prototype | DEMO MODE")
    print("  Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
