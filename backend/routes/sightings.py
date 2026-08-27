"""VanRakshak AI — Sightings Routes"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/sightings")
async def list_sightings(
    limit: int = Query(default=20, le=100, ge=1),
    species: Optional[str] = Query(default=None),
):
    """
    GET /api/sightings
    Return recent wildlife sightings from shared state.
    Optionally filter by species.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    sightings = list(orch.shared_state["sightings"])

    if species:
        sightings = [s for s in sightings if s.get("species", "").lower() == species.lower()]

    # Most recent first
    sightings = sorted(sightings, key=lambda s: s.get("timestamp", ""), reverse=True)
    return {
        "sightings": sightings[:limit],
        "total":     len(sightings),
        "is_demo":   True,
    }


@router.post("/sightings")
async def report_sighting(body: dict):
    """
    POST /api/sightings
    Report a new wildlife sighting. Triggers the full orchestrated
    PREDICT → ALERT → COORDINATE workflow.

    Required body fields:
        species (str), lat (float), lon (float)

    Optional:
        count, source, nearest_village_id, notes
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    # Basic validation
    required = ("species", "lat", "lon")
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {missing}",
        )

    # Add timestamp if absent
    if "timestamp" not in body:
        body["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Run the full orchestrated workflow
    result = orch.process_sighting(body)
    return result
