"""VanRakshak AI — Agents Routes (status, logs, approvals)"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()


@router.get("/agents/status")
async def get_agent_statuses():
    """
    GET /api/agents/status
    Return the current status of all five VanRakshak agents.
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    agent_names = ["movement_agent", "alert_agent", "response_agent",
                   "compensation_agent", "hotspot_agent"]

    statuses = []
    for name in agent_names:
        last_log = next(
            (log for log in reversed(orch.agent_logs) if log["agent"] == name),
            None,
        )
        statuses.append({
            "agent":        name,
            "status":       "ACTIVE",
            "last_action":  last_log["action"]    if last_log else None,
            "last_run":     last_log["timestamp"] if last_log else None,
            "escalation_required": last_log["escalation_required"] if last_log else False,
            "is_demo":      True,
        })

    return {
        "agents":      statuses,
        "total":       len(statuses),
        "is_demo":     True,
    }


@router.get("/agents/logs")
async def get_agent_logs(
    agent: Optional[str] = Query(default=None, description="Filter by agent name"),
    limit: int = Query(default=50, le=200, ge=1),
):
    """
    GET /api/agents/logs
    Return agent action logs, most recent first.
    Optionally filter by agent name.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    logs = list(orch.agent_logs)

    if agent:
        logs = [l for l in logs if l.get("agent") == agent]

    logs = sorted(logs, key=lambda l: l.get("timestamp", ""), reverse=True)
    return {
        "logs":    logs[:limit],
        "total":   len(logs),
        "is_demo": True,
    }


@router.post("/agents/approve")
async def officer_approve(body: dict):
    """
    POST /api/agents/approve
    Submit an officer approval, rejection, or override for a pending action.

    Required body fields:
        approval_id (str), officer_id (str), decision (str)
        decision values: APPROVED | REJECTED | OVERRIDE

    Optional:
        notes (str), override_data (dict)
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    required = ("approval_id", "officer_id", "decision")
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {missing}")

    result = orch.officer_approve(
        approval_id=body["approval_id"],
        officer_id=body["officer_id"],
        decision=body["decision"].upper(),
        override_data=body.get("override_data"),
        notes=body.get("notes"),
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/agents/pending-approvals")
async def get_pending_approvals():
    """
    GET /api/agents/pending-approvals
    List all pending human-in-the-loop approval items.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    pending = [
        a for a in orch.shared_state["approvals"]
        if a.get("decision", "PENDING") == "PENDING"
    ]
    return {
        "pending_approvals": pending,
        "count":             len(pending),
        "is_demo":           True,
    }
