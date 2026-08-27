"""VanRakshak AI — Compensation Routes"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/compensation/start")
async def start_claim(body: dict):
    """
    POST /api/compensation/start
    Initiate a livestock/crop compensation claim draft.

    Required body fields:
        incident_id (str), claimant_name (str), claimant_village_id (str),
        loss_type (str), loss_description (str)

    Optional: estimated_loss_value (float)

    IMPORTANT: AI produces a DRAFT only. Officer approval required.
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    required = ("incident_id", "claimant_name", "claimant_village_id",
                 "loss_type", "loss_description")
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {missing}")

    claim = orch.agents["compensation"].start_claim(
        incident_id=body["incident_id"],
        villager_info={
            "claimant_name":  body["claimant_name"],
            "village_id":     body["claimant_village_id"],
            "contact_number": body.get("contact_number", "N/A"),
        },
        loss_details={
            "loss_type":             body["loss_type"],
            "loss_description":      body["loss_description"],
            "species_responsible":   body.get("species_responsible", "Unknown"),
            "estimated_loss_value":  body.get("estimated_loss_value"),
        },
    )
    orch.shared_state["claims"].append(claim)
    return claim


@router.get("/compensation/{claim_id}")
async def get_claim(claim_id: str):
    """
    GET /api/compensation/{claim_id}
    Retrieve a specific compensation claim draft.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    claim = orch.agents["compensation"].get_claim(claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    return claim


@router.get("/compensation/checklist/{loss_type}")
async def get_checklist(loss_type: str):
    """
    GET /api/compensation/checklist/{loss_type}
    Return the required document checklist for a given loss type.

    loss_type values: livestock_predation, crop_damage, human_injury, property_damage
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    checklist = orch.agents["compensation"].get_document_checklist(loss_type)
    return {
        "loss_type": loss_type,
        "checklist": checklist,
        "count":     len(checklist),
        "is_demo":   True,
    }
