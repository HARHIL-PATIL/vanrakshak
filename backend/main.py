"""
VanRakshak AI — FastAPI Application Entry Point
=================================================
Run with:
    uvicorn backend.main:app --reload
  or (from inside backend/):
    uvicorn main:app --reload

ALL DATA AND MODELS ARE DEMO / PROTOTYPE ONLY.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from orchestrator.orchestrator import VanRakshakOrchestrator

# ---------------------------------------------------------------------------
# Create the module-level orchestrator singleton
# ---------------------------------------------------------------------------
_orchestrator: VanRakshakOrchestrator | None = None


def get_orchestrator() -> VanRakshakOrchestrator:
    """Return the app-wide orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VanRakshakOrchestrator()
    return _orchestrator


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VanRakshak AI",
    description=(
        "Agentic AI Platform for Human-Wildlife Conflict Mitigation "
        "around Gir Forest, Gujarat, India.\n\n"
        "⚠️ **PROTOTYPE / DEMO** — All data is synthetic. "
        "Not for operational use without validated models and Forest Department approval."
    ),
    version="1.0.0-demo",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------

from routes.dashboard    import router as dashboard_router
from routes.sightings    import router as sightings_router
from routes.incidents    import router as incidents_router
from routes.alerts       import router as alerts_router
from routes.compensation import router as compensation_router
from routes.agents       import router as agents_router
from routes.demo         import router as demo_router

app.include_router(dashboard_router,    prefix="/api", tags=["Dashboard"])
app.include_router(sightings_router,    prefix="/api", tags=["Sightings"])
app.include_router(incidents_router,    prefix="/api", tags=["Incidents"])
app.include_router(alerts_router,       prefix="/api", tags=["Alerts"])
app.include_router(compensation_router, prefix="/api", tags=["Compensation"])
app.include_router(agents_router,       prefix="/api", tags=["Agents"])
app.include_router(demo_router,         prefix="/api", tags=["Demo"])

# ---------------------------------------------------------------------------
# Root health-check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def root():
    return {
        "service":     "VanRakshak AI",
        "status":      "running",
        "version":     "1.0.0-demo",
        "description": "Agentic AI for Human-Wildlife Conflict Mitigation — Gir Forest",
        "disclaimer":  "PROTOTYPE / DEMO — All data is synthetic",
        "docs":        "/docs",
        "is_demo":     True,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "is_demo": True}


# ---------------------------------------------------------------------------
# Startup event — initialise orchestrator eagerly
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Pre-warm the orchestrator and ML model on startup."""
    orch = get_orchestrator()
    # Trigger ML model training (happens in __init__ of MovementPredictor)
    _ = orch.agents["movement"]
    print("✅ VanRakshak AI started — orchestrator and ML model ready [DEMO MODE]")
