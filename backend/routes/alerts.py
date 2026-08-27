"""VanRakshak AI — Alerts Routes"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/alerts")
async def list_active_alerts():
    """
    GET /api/alerts
    Return all currently active alerts from shared state.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    alerts = [a for a in orch.shared_state["alerts"] if a.get("is_active", True)]
    return {
        "alerts":  alerts,
        "total":   len(alerts),
        "is_demo": True,
    }


@router.post("/alerts/generate")
async def generate_alert(body: dict):
    """
    POST /api/alerts/generate
    Manually trigger alert generation for a sighting + village pair.

    Required body fields: sighting_id (str), village_id (str)
    """
    from main import get_orchestrator
    from data.sample_data import get_village_by_id, SAMPLE_SIGHTINGS

    sighting_id = body.get("sighting_id")
    village_id  = body.get("village_id")
    if not sighting_id or not village_id:
        raise HTTPException(
            status_code=422,
            detail="Required: sighting_id, village_id",
        )

    orch = get_orchestrator()

    # Resolve sighting from shared state or sample data
    sighting = next(
        (s for s in orch.shared_state["sightings"] if s.get("sighting_id") == sighting_id),
        next((s for s in SAMPLE_SIGHTINGS if s.get("sighting_id") == sighting_id), None),
    )
    if sighting is None:
        raise HTTPException(status_code=404, detail=f"Sighting {sighting_id} not found")

    village = get_village_by_id(village_id)
    if village is None:
        raise HTTPException(status_code=404, detail=f"Village {village_id} not found")

    # Run movement assessment first to get risk data
    assessment = orch.agents["movement"].analyze(
        sighting_data=sighting,
        village_id=village_id,
    )

    alert = orch.agents["alert"].generate_alert(
        risk_assessment=assessment,
        village=village,
        species=sighting.get("species", "Unknown"),
    )
    orch.shared_state["alerts"].append(alert)
    return alert
