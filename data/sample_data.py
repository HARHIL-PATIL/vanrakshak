# ============================================================
# VanRakshak AI — Sample / Demo Data
# ALL DATA IS SYNTHETIC — DEMO PURPOSES ONLY
# Gir Forest, Gujarat, India
# ============================================================

from datetime import datetime, timedelta
import random

random.seed(42)

# ---------------------------------------------------------------------------
# VILLAGES (8) — approximate coords near Gir National Park
# ---------------------------------------------------------------------------
VILLAGES = [
    {"id": "V001", "name": "Sasan Gir",      "lat": 21.1247, "lon": 70.6143, "population": 2800, "livestock_count": 340, "risk_level": "HIGH"},
    {"id": "V002", "name": "Dhari",           "lat": 21.3295, "lon": 71.0204, "population": 4500, "livestock_count": 210, "risk_level": "MEDIUM"},
    {"id": "V003", "name": "Talala",          "lat": 20.9957, "lon": 70.4579, "population": 3100, "livestock_count": 280, "risk_level": "HIGH"},
    {"id": "V004", "name": "Visavadar",       "lat": 21.3361, "lon": 70.7261, "population": 2200, "livestock_count": 190, "risk_level": "MEDIUM"},
    {"id": "V005", "name": "Una",             "lat": 20.8235, "lon": 71.0367, "population": 5600, "livestock_count": 160, "risk_level": "LOW"},
    {"id": "V006", "name": "Mendarda",        "lat": 21.3019, "lon": 70.4517, "population": 1900, "livestock_count": 320, "risk_level": "HIGH"},
    {"id": "V007", "name": "Junagadh (Buffer)", "lat": 21.5222, "lon": 70.4579, "population": 8200, "livestock_count": 90,  "risk_level": "LOW"},
    {"id": "V008", "name": "Amreli",          "lat": 21.6013, "lon": 71.2218, "population": 6100, "livestock_count": 120, "risk_level": "LOW"},
]

# ---------------------------------------------------------------------------
# WILDLIFE SIGHTINGS (15+)  — [SAMPLE DATA]
# ---------------------------------------------------------------------------
_now = datetime.utcnow()

SIGHTINGS = [
    {
        "id": "S001", "species": "Asiatic Lion",  "lat": 21.1180, "lon": 70.6100,
        "nearest_village": "V001", "distance_km": 0.8,
        "timestamp": (_now - timedelta(hours=2)).isoformat(),
        "time_of_day": "night", "observer": "Forest Guard Ramesh K.",
        "notes": "Male lion, approx 5 yrs, near livestock pen", "verified": True
    },
    {
        "id": "S002", "species": "Leopard",       "lat": 21.3100, "lon": 71.0000,
        "nearest_village": "V002", "distance_km": 1.2,
        "timestamp": (_now - timedelta(hours=5)).isoformat(),
        "time_of_day": "dusk", "observer": "Camera Trap CT-07",
        "notes": "Single leopard moving south-east", "verified": True
    },
    {
        "id": "S003", "species": "Asiatic Lion",  "lat": 20.9900, "lon": 70.4600,
        "nearest_village": "V003", "distance_km": 0.6,
        "timestamp": (_now - timedelta(hours=1)).isoformat(),
        "time_of_day": "night", "observer": "Village Alert Node VAN-03",
        "notes": "Pride of 3, moving toward village perimeter", "verified": True
    },
    {
        "id": "S004", "species": "Hyena",         "lat": 21.3200, "lon": 70.7100,
        "nearest_village": "V004", "distance_km": 2.1,
        "timestamp": (_now - timedelta(hours=8)).isoformat(),
        "time_of_day": "dawn", "observer": "Forest Guard Suresh P.",
        "notes": "Pack of 2 hyenas near water source", "verified": True
    },
    {
        "id": "S005", "species": "Wild Boar",     "lat": 21.2950, "lon": 70.4400,
        "nearest_village": "V006", "distance_km": 0.3,
        "timestamp": (_now - timedelta(hours=3)).isoformat(),
        "time_of_day": "morning", "observer": "Farmer Jayesh B.",
        "notes": "Group of boars raiding crop field", "verified": False
    },
    {
        "id": "S006", "species": "Leopard",       "lat": 21.1300, "lon": 70.6200,
        "nearest_village": "V001", "distance_km": 1.5,
        "timestamp": (_now - timedelta(hours=14)).isoformat(),
        "time_of_day": "night", "observer": "Camera Trap CT-02",
        "notes": "Female with cubs", "verified": True
    },
    {
        "id": "S007", "species": "Asiatic Lion",  "lat": 21.3150, "lon": 70.4600,
        "nearest_village": "V006", "distance_km": 1.0,
        "timestamp": (_now - timedelta(hours=18)).isoformat(),
        "time_of_day": "dusk", "observer": "Patrol Team PT-02",
        "notes": "Sub-adult male, lone", "verified": True
    },
    {
        "id": "S008", "species": "Asiatic Lion",  "lat": 21.0000, "lon": 70.4700,
        "nearest_village": "V003", "distance_km": 0.9,
        "timestamp": (_now - timedelta(hours=26)).isoformat(),
        "time_of_day": "night", "observer": "Camera Trap CT-09",
        "notes": "Two adult females", "verified": True
    },
    {
        "id": "S009", "species": "Hyena",         "lat": 21.1350, "lon": 70.6050,
        "nearest_village": "V001", "distance_km": 0.5,
        "timestamp": (_now - timedelta(hours=30)).isoformat(),
        "time_of_day": "night", "observer": "Forest Guard Ramesh K.",
        "notes": "Single hyena, scavenging near village edge", "verified": True
    },
    {
        "id": "S010", "species": "Wild Boar",     "lat": 20.8300, "lon": 71.0400,
        "nearest_village": "V005", "distance_km": 1.8,
        "timestamp": (_now - timedelta(hours=36)).isoformat(),
        "time_of_day": "morning", "observer": "Farmer Kanji M.",
        "notes": "Field damage reported, 4 boars", "verified": False
    },
    {
        "id": "S011", "species": "Leopard",       "lat": 21.3350, "lon": 70.7300,
        "nearest_village": "V004", "distance_km": 0.7,
        "timestamp": (_now - timedelta(hours=40)).isoformat(),
        "time_of_day": "dusk", "observer": "Camera Trap CT-11",
        "notes": "Adult male, territory marking", "verified": True
    },
    {
        "id": "S012", "species": "Asiatic Lion",  "lat": 21.5100, "lon": 70.4500,
        "nearest_village": "V007", "distance_km": 3.2,
        "timestamp": (_now - timedelta(hours=48)).isoformat(),
        "time_of_day": "dawn", "observer": "Patrol Team PT-01",
        "notes": "Pride of 5 near forest boundary", "verified": True
    },
    {
        "id": "S013", "species": "Hyena",         "lat": 21.2900, "lon": 70.4500,
        "nearest_village": "V006", "distance_km": 1.4,
        "timestamp": (_now - timedelta(hours=52)).isoformat(),
        "time_of_day": "night", "observer": "Camera Trap CT-06",
        "notes": "Pack of 3 moving north", "verified": True
    },
    {
        "id": "S014", "species": "Wild Boar",     "lat": 21.3300, "lon": 71.0100,
        "nearest_village": "V002", "distance_km": 0.4,
        "timestamp": (_now - timedelta(hours=60)).isoformat(),
        "time_of_day": "morning", "observer": "Farmer Bharat S.",
        "notes": "Crop raid — groundnut field", "verified": True
    },
    {
        "id": "S015", "species": "Asiatic Lion",  "lat": 21.1100, "lon": 70.6000,
        "nearest_village": "V001", "distance_km": 0.4,
        "timestamp": (_now - timedelta(hours=72)).isoformat(),
        "time_of_day": "night", "observer": "Forest Guard Dilip T.",
        "notes": "Male lion at village water trough", "verified": True
    },
]

# ---------------------------------------------------------------------------
# HISTORICAL CONFLICT INCIDENTS (10+) — [SAMPLE DATA]
# ---------------------------------------------------------------------------
INCIDENTS = [
    {
        "id": "INC-001", "village_id": "V001", "species": "Asiatic Lion",
        "incident_type": "livestock_kill", "severity": "HIGH",
        "livestock_lost": 2, "livestock_type": "buffalo",
        "timestamp": (_now - timedelta(days=2)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-001",
        "risk_score": 0.82, "notes": "2 buffalo killed near pen at night"
    },
    {
        "id": "INC-002", "village_id": "V003", "species": "Leopard",
        "incident_type": "livestock_kill", "severity": "HIGH",
        "livestock_lost": 1, "livestock_type": "goat",
        "timestamp": (_now - timedelta(days=1)).isoformat(),
        "status": "IN_PROGRESS", "assigned_team": "RT-003",
        "risk_score": 0.76, "notes": "Goat dragged into shrubland"
    },
    {
        "id": "INC-003", "village_id": "V006", "species": "Asiatic Lion",
        "incident_type": "human_encounter", "severity": "HIGH",
        "livestock_lost": 0, "livestock_type": None,
        "timestamp": (_now - timedelta(hours=6)).isoformat(),
        "status": "ASSIGNED", "assigned_team": "RT-002",
        "risk_score": 0.79, "notes": "Farmer Nagji reported close encounter while collecting firewood"
    },
    {
        "id": "INC-004", "village_id": "V002", "species": "Wild Boar",
        "incident_type": "crop_damage", "severity": "MEDIUM",
        "livestock_lost": 0, "livestock_type": None,
        "timestamp": (_now - timedelta(days=3)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-004",
        "risk_score": 0.48, "notes": "2 acres groundnut damaged"
    },
    {
        "id": "INC-005", "village_id": "V004", "species": "Hyena",
        "incident_type": "livestock_kill", "severity": "MEDIUM",
        "livestock_lost": 3, "livestock_type": "sheep",
        "timestamp": (_now - timedelta(days=5)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-001",
        "risk_score": 0.55, "notes": "3 sheep killed in unprotected pen"
    },
    {
        "id": "INC-006", "village_id": "V001", "species": "Asiatic Lion",
        "incident_type": "livestock_kill", "severity": "HIGH",
        "livestock_lost": 1, "livestock_type": "cow",
        "timestamp": (_now - timedelta(days=7)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-001",
        "risk_score": 0.85, "notes": "Cow killed near outskirts"
    },
    {
        "id": "INC-007", "village_id": "V003", "species": "Asiatic Lion",
        "incident_type": "livestock_kill", "severity": "HIGH",
        "livestock_lost": 2, "livestock_type": "cow",
        "timestamp": (_now - timedelta(days=10)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-003",
        "risk_score": 0.80, "notes": "Night raid on open field"
    },
    {
        "id": "INC-008", "village_id": "V006", "species": "Leopard",
        "incident_type": "livestock_kill", "severity": "HIGH",
        "livestock_lost": 1, "livestock_type": "goat",
        "timestamp": (_now - timedelta(days=4)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-002",
        "risk_score": 0.71, "notes": "Goat taken from pen"
    },
    {
        "id": "INC-009", "village_id": "V005", "species": "Wild Boar",
        "incident_type": "crop_damage", "severity": "LOW",
        "livestock_lost": 0, "livestock_type": None,
        "timestamp": (_now - timedelta(days=8)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-005",
        "risk_score": 0.32, "notes": "Minor crop damage at field edge"
    },
    {
        "id": "INC-010", "village_id": "V001", "species": "Hyena",
        "incident_type": "livestock_kill", "severity": "MEDIUM",
        "livestock_lost": 2, "livestock_type": "sheep",
        "timestamp": (_now - timedelta(days=14)).isoformat(),
        "status": "RESOLVED", "assigned_team": "RT-001",
        "risk_score": 0.58, "notes": "Hyena pack attack at dawn"
    },
    {
        "id": "INC-011", "village_id": "V003", "species": "Leopard",
        "incident_type": "human_encounter", "severity": "HIGH",
        "livestock_lost": 0, "livestock_type": None,
        "timestamp": (_now - timedelta(hours=10)).isoformat(),
        "status": "NEW", "assigned_team": None,
        "risk_score": 0.74, "notes": "Child spotted leopard near school path — no injury"
    },
]

# ---------------------------------------------------------------------------
# RESPONSE TEAMS (5) — [SAMPLE DATA]
# ---------------------------------------------------------------------------
RESPONSE_TEAMS = [
    {"id": "RT-001", "name": "Sasan Rapid Response", "lat": 21.1247, "lon": 70.6143,
     "members": 4, "status": "AVAILABLE", "specialization": "Large Cat", "contact": "+91-98250-11001"},
    {"id": "RT-002", "name": "Mendarda Forest Unit",  "lat": 21.3019, "lon": 70.4517,
     "members": 3, "status": "DEPLOYED",  "specialization": "Large Cat", "contact": "+91-98250-11002"},
    {"id": "RT-003", "name": "Talala Rescue Team",    "lat": 20.9957, "lon": 70.4579,
     "members": 5, "status": "AVAILABLE", "specialization": "Multi-species", "contact": "+91-98250-11003"},
    {"id": "RT-004", "name": "Dhari Wildlife Squad",  "lat": 21.3295, "lon": 71.0204,
     "members": 3, "status": "AVAILABLE", "specialization": "Crop Conflict", "contact": "+91-98250-11004"},
    {"id": "RT-005", "name": "Una Buffer Zone Patrol","lat": 20.8235, "lon": 71.0367,
     "members": 4, "status": "AVAILABLE", "specialization": "Patrol", "contact": "+91-98250-11005"},
]

# ---------------------------------------------------------------------------
# RISK ASSESSMENTS — [SAMPLE DATA]
# ---------------------------------------------------------------------------
RISK_ASSESSMENTS = [
    {"village_id": "V001", "risk_score": 0.82, "risk_level": "HIGH",   "confidence": 0.87},
    {"village_id": "V002", "risk_score": 0.51, "risk_level": "MEDIUM", "confidence": 0.79},
    {"village_id": "V003", "risk_score": 0.78, "risk_level": "HIGH",   "confidence": 0.84},
    {"village_id": "V004", "risk_score": 0.45, "risk_level": "MEDIUM", "confidence": 0.72},
    {"village_id": "V005", "risk_score": 0.29, "risk_level": "LOW",    "confidence": 0.81},
    {"village_id": "V006", "risk_score": 0.74, "risk_level": "HIGH",   "confidence": 0.80},
    {"village_id": "V007", "risk_score": 0.31, "risk_level": "LOW",    "confidence": 0.76},
    {"village_id": "V008", "risk_score": 0.22, "risk_level": "LOW",    "confidence": 0.83},
]

# ---------------------------------------------------------------------------
# AGENT LOGS — [SAMPLE DATA]
# ---------------------------------------------------------------------------
AGENT_LOGS = [
    {"agent": "MovementAgent",     "action": "Analyzed S001 — Lion near Sasan Gir",        "timestamp": (_now - timedelta(minutes=10)).isoformat(), "confidence": 0.87},
    {"agent": "AlertAgent",        "action": "Broadcast HIGH alert to V001, V003",          "timestamp": (_now - timedelta(minutes=9)).isoformat(),  "confidence": 0.85},
    {"agent": "ResponseAgent",     "action": "INC-011 ticket created, RT-003 recommended",  "timestamp": (_now - timedelta(minutes=8)).isoformat(),  "confidence": 0.82},
    {"agent": "CompensationAgent", "action": "INC-001 claim drafted for human review",       "timestamp": (_now - timedelta(hours=2)).isoformat(),    "confidence": 0.90},
    {"agent": "HotspotAgent",      "action": "3 hotspot clusters identified",                "timestamp": (_now - timedelta(hours=1)).isoformat(),    "confidence": 0.78},
    {"agent": "Orchestrator",      "action": "Pipeline completed for S001 event",            "timestamp": (_now - timedelta(minutes=7)).isoformat(),  "confidence": 0.84},
]

def get_all_data():
    """Return a copy of all sample data."""
    return {
        "villages": list(VILLAGES),
        "sightings": list(SIGHTINGS),
        "incidents": list(INCIDENTS),
        "response_teams": list(RESPONSE_TEAMS),
        "risk_assessments": list(RISK_ASSESSMENTS),
        "agent_logs": list(AGENT_LOGS),
    }
