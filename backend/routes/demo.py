"""VanRakshak AI — Demo Scenario Routes"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/demo/run")
async def run_demo():
    """
    POST /api/demo/run
    Execute the full VanRakshak demo scenario:

    Scenario: Asiatic Lion sighted near Sasan Gir at dawn.
    Demonstrates the complete PREDICT → ALERT → COORDINATE workflow
    with simulated human-in-the-loop officer approval.

    Steps demonstrated:
        1. Sighting received (camera trap)
        2. Agent 1: Movement & Risk Prediction
        3. Agent 2: Bilingual Alert Generation (EN + Gujarati)
        4. Agent 3: Incident Ticket with Team Recommendation
        5. Human-in-the-Loop: Simulated Officer Approval
        6. Agent 4: Compensation Claim Draft
        7. Agent 5: Hotspot Dashboard Update
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    result = orch.run_demo_scenario()
    return result


@router.get("/demo/status")
async def demo_status():
    """
    GET /api/demo/status
    Return the current state of the demo scenario.
    If the demo hasn't run yet, returns a prompt to POST /api/demo/run.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    return orch.get_demo_status()
