"""VanRakshak AI — Incidents Routes"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/incidents")
async def list_incidents(
    status: Optional[str]  = Query(default=None, description="Filter by status (NEW, ASSIGNED, etc.)"),
    severity: Optional[str] = Query(default=None, description="Filter by severity (HIGH, MEDIUM, LOW)"),
    village_id: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100, ge=1),
):
    """
    GET /api/incidents
    List conflict incidents with optional filters.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    incidents = list(orch.shared_state["incidents"])

    if status:
        incidents = [i for i in incidents if i.get("status", "").upper() == status.upper()]
    if severity:
        incidents = [i for i in incidents if i.get("severity", "").upper() == severity.upper()]
    if village_id:
        incidents = [i for i in incidents if i.get("village_id") == village_id]

    incidents = sorted(incidents, key=lambda i: i.get("date", ""), reverse=True)
    return {
        "incidents": incidents[:limit],
        "total":     len(incidents),
        "filters":   {"status": status, "severity": severity, "village_id": village_id},
        "is_demo":   True,
    }


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """
    GET /api/incidents/{incident_id}
    Retrieve a single incident by ID.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    incidents = orch.shared_state["incidents"]
    incident = next((i for i in incidents if i.get("incident_id") == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.put("/incidents/{incident_id}/status")
async def update_incident_status(incident_id: str, body: dict):
    """
    PUT /api/incidents/{incident_id}/status
    Update the status of an incident ticket.

    Required body: new_status (str), officer_id (str)
    Optional: notes (str)
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    new_status = body.get("new_status")
    officer_id = body.get("officer_id")
    if not new_status or not officer_id:
        raise HTTPException(
            status_code=422,
            detail="Required fields: new_status, officer_id",
        )

    # Look for ticket matching this incident_id
    matching_tickets = [
        t for t in orch.shared_state["tickets"]
        if t.get("incident_id") == incident_id
    ]
    if not matching_tickets:
        raise HTTPException(
            status_code=404,
            detail=f"No ticket found for incident {incident_id}",
        )

    ticket = matching_tickets[-1]
    result = orch.agents["response"].update_incident_status(
        ticket_id=ticket["ticket_id"],
        new_status=new_status.upper(),
        officer_id=officer_id,
        notes=body.get("notes"),
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
