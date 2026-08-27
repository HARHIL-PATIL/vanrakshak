"""
VanRakshak AI — Synthetic Sample Data
======================================
ALL DATA IS SYNTHETIC / DEMO ONLY.
Coordinates are approximate and do NOT represent live or verified locations.
This file is for demonstration and prototype purposes only.
"""

from datetime import datetime, timedelta
import random

# ---------------------------------------------------------------------------
# Villages near Gir Forest, Gujarat, India (approximate lat/lon — DEMO ONLY)
# ---------------------------------------------------------------------------
SAMPLE_VILLAGES = [
    {
        "village_id": "VLG001",
        "name": "Sasan Gir",
        "lat": 21.1242,
        "lon": 70.5521,
        "livestock_count": 320,
        "population": 2400,
        "contact_number": "+91-98765-00001",
        "district": "Gir Somnath",
        "risk_zone": "HIGH",
    },
    {
        "village_id": "VLG002",
        "name": "Jamvala",
        "lat": 21.0850,
        "lon": 70.6100,
        "livestock_count": 180,
        "population": 1100,
        "contact_number": "+91-98765-00002",
        "district": "Gir Somnath",
        "risk_zone": "HIGH",
    },
    {
        "village_id": "VLG003",
        "name": "Dhari",
        "lat": 21.3240,
        "lon": 71.0200,
        "livestock_count": 410,
        "population": 3800,
        "contact_number": "+91-98765-00003",
        "district": "Amreli",
        "risk_zone": "MEDIUM",
    },
    {
        "village_id": "VLG004",
        "name": "Visavadar",
        "lat": 21.3480,
        "lon": 70.7330,
        "livestock_count": 290,
        "population": 2100,
        "contact_number": "+91-98765-00004",
        "district": "Junagadh",
        "risk_zone": "MEDIUM",
    },
    {
        "village_id": "VLG005",
        "name": "Una",
        "lat": 20.8230,
        "lon": 71.0380,
        "livestock_count": 500,
        "population": 5200,
        "contact_number": "+91-98765-00005",
        "district": "Gir Somnath",
        "risk_zone": "MEDIUM",
    },
    {
        "village_id": "VLG006",
        "name": "Talala",
        "lat": 20.9560,
        "lon": 70.4560,
        "livestock_count": 220,
        "population": 1600,
        "contact_number": "+91-98765-00006",
        "district": "Gir Somnath",
        "risk_zone": "HIGH",
    },
    {
        "village_id": "VLG007",
        "name": "Mendarda",
        "lat": 21.3200,
        "lon": 70.4200,
        "livestock_count": 150,
        "population": 900,
        "contact_number": "+91-98765-00007",
        "district": "Junagadh",
        "risk_zone": "LOW",
    },
    {
        "village_id": "VLG008",
        "name": "Kodinar",
        "lat": 20.7950,
        "lon": 70.7050,
        "livestock_count": 380,
        "population": 4100,
        "contact_number": "+91-98765-00008",
        "district": "Gir Somnath",
        "risk_zone": "LOW",
    },
]

# ---------------------------------------------------------------------------
# Wildlife Sightings — last 30 days (DEMO / SIMULATED)
# ---------------------------------------------------------------------------
_now = datetime.utcnow()

SAMPLE_SIGHTINGS = [
    {
        "sighting_id": "SGT001",
        "species": "Asiatic Lion",
        "lat": 21.1300,
        "lon": 70.5600,
        "timestamp": (_now - timedelta(hours=3)).isoformat(),
        "confidence": 0.95,
        "source": "camera_trap",
        "count": 2,
        "nearest_village_id": "VLG001",
        "notes": "Adult male and female pair moving east",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT002",
        "species": "Leopard",
        "lat": 21.0900,
        "lon": 70.6200,
        "timestamp": (_now - timedelta(hours=7)).isoformat(),
        "confidence": 0.88,
        "source": "ranger_report",
        "count": 1,
        "nearest_village_id": "VLG002",
        "notes": "Single adult spotted near forest edge",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT003",
        "species": "Asiatic Lion",
        "lat": 20.9600,
        "lon": 70.4600,
        "timestamp": (_now - timedelta(hours=14)).isoformat(),
        "confidence": 0.92,
        "source": "villager_report",
        "count": 3,
        "nearest_village_id": "VLG006",
        "notes": "Pride of 3 near village boundary",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT004",
        "species": "Hyena",
        "lat": 21.1100,
        "lon": 70.5800,
        "timestamp": (_now - timedelta(hours=20)).isoformat(),
        "confidence": 0.80,
        "source": "camera_trap",
        "count": 2,
        "nearest_village_id": "VLG001",
        "notes": "Two hyenas near livestock pen",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT005",
        "species": "Wild Boar",
        "lat": 21.3300,
        "lon": 71.0300,
        "timestamp": (_now - timedelta(days=1)).isoformat(),
        "confidence": 0.75,
        "source": "villager_report",
        "count": 6,
        "nearest_village_id": "VLG003",
        "notes": "Herd of boars in crop field",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT006",
        "species": "Nilgai",
        "lat": 21.3500,
        "lon": 70.7400,
        "timestamp": (_now - timedelta(days=1, hours=4)).isoformat(),
        "confidence": 0.85,
        "source": "ranger_report",
        "count": 4,
        "nearest_village_id": "VLG004",
        "notes": "Nilgai grazing near agricultural fields",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT007",
        "species": "Leopard",
        "lat": 21.1250,
        "lon": 70.5500,
        "timestamp": (_now - timedelta(days=2)).isoformat(),
        "confidence": 0.91,
        "source": "camera_trap",
        "count": 1,
        "nearest_village_id": "VLG001",
        "notes": "Leopard on forest trail camera",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT008",
        "species": "Asiatic Lion",
        "lat": 20.9500,
        "lon": 70.4700,
        "timestamp": (_now - timedelta(days=3)).isoformat(),
        "confidence": 0.96,
        "source": "camera_trap",
        "count": 1,
        "nearest_village_id": "VLG006",
        "notes": "Sub-adult male lion",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT009",
        "species": "Hyena",
        "lat": 21.0800,
        "lon": 70.6300,
        "timestamp": (_now - timedelta(days=4)).isoformat(),
        "confidence": 0.78,
        "source": "villager_report",
        "count": 1,
        "nearest_village_id": "VLG002",
        "notes": "Spotted near goat pen at dusk",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT010",
        "species": "Asiatic Lion",
        "lat": 21.3100,
        "lon": 70.4100,
        "timestamp": (_now - timedelta(days=5)).isoformat(),
        "confidence": 0.90,
        "source": "ranger_report",
        "count": 2,
        "nearest_village_id": "VLG007",
        "notes": "Lioness with cub near water body",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT011",
        "species": "Wild Boar",
        "lat": 20.8300,
        "lon": 71.0400,
        "timestamp": (_now - timedelta(days=6)).isoformat(),
        "confidence": 0.70,
        "source": "villager_report",
        "count": 8,
        "nearest_village_id": "VLG005",
        "notes": "Crop damage reported",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT012",
        "species": "Leopard",
        "lat": 20.7900,
        "lon": 70.7100,
        "timestamp": (_now - timedelta(days=7)).isoformat(),
        "confidence": 0.83,
        "source": "camera_trap",
        "count": 1,
        "nearest_village_id": "VLG008",
        "notes": "Leopard near outskirts",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT013",
        "species": "Nilgai",
        "lat": 21.1200,
        "lon": 70.5700,
        "timestamp": (_now - timedelta(days=8)).isoformat(),
        "confidence": 0.88,
        "source": "ranger_report",
        "count": 5,
        "nearest_village_id": "VLG001",
        "notes": "Nilgai near boundary",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT014",
        "species": "Asiatic Lion",
        "lat": 21.0870,
        "lon": 70.6050,
        "timestamp": (_now - timedelta(days=10)).isoformat(),
        "confidence": 0.94,
        "source": "camera_trap",
        "count": 4,
        "nearest_village_id": "VLG002",
        "notes": "Full pride captured on camera trap",
        "is_demo": True,
    },
    {
        "sighting_id": "SGT015",
        "species": "Hyena",
        "lat": 21.3250,
        "lon": 71.0150,
        "timestamp": (_now - timedelta(days=12)).isoformat(),
        "confidence": 0.76,
        "source": "villager_report",
        "count": 3,
        "nearest_village_id": "VLG003",
        "notes": "Three hyenas near cattle pen",
        "is_demo": True,
    },
]

# ---------------------------------------------------------------------------
# Historical Conflict Incidents (DEMO / SIMULATED)
# ---------------------------------------------------------------------------
SAMPLE_INCIDENTS = [
    {"incident_id": "INC001", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG001", "species": "Asiatic Lion",  "date": (_now - timedelta(days=2)).isoformat(),  "losses": "2 cattle killed",         "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC002", "type": "human_injury",        "severity": "HIGH",   "village_id": "VLG006", "species": "Asiatic Lion",  "date": (_now - timedelta(days=5)).isoformat(),  "losses": "1 person injured",        "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC003", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG002", "species": "Leopard",       "date": (_now - timedelta(days=6)).isoformat(),  "losses": "3 goats killed",          "status": "IN_PROGRESS",  "is_demo": True},
    {"incident_id": "INC004", "type": "crop_damage",         "severity": "MEDIUM", "village_id": "VLG003", "species": "Wild Boar",     "date": (_now - timedelta(days=8)).isoformat(),  "losses": "1.5 acres crop damaged",  "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC005", "type": "property_damage",     "severity": "MEDIUM", "village_id": "VLG004", "species": "Nilgai",        "date": (_now - timedelta(days=10)).isoformat(), "losses": "Fence broken",            "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC006", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG001", "species": "Hyena",         "date": (_now - timedelta(days=12)).isoformat(), "losses": "1 sheep killed",          "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC007", "type": "crop_damage",         "severity": "LOW",    "village_id": "VLG005", "species": "Wild Boar",     "date": (_now - timedelta(days=14)).isoformat(), "losses": "Minor crop damage",       "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC008", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG006", "species": "Asiatic Lion",  "date": (_now - timedelta(days=15)).isoformat(), "losses": "4 cattle killed",         "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC009", "type": "human_injury",        "severity": "HIGH",   "village_id": "VLG002", "species": "Leopard",       "date": (_now - timedelta(days=18)).isoformat(), "losses": "1 person injured",        "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC010", "type": "livestock_predation", "severity": "MEDIUM", "village_id": "VLG007", "species": "Leopard",       "date": (_now - timedelta(days=20)).isoformat(), "losses": "2 goats killed",          "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC011", "type": "crop_damage",         "severity": "MEDIUM", "village_id": "VLG003", "species": "Nilgai",        "date": (_now - timedelta(days=22)).isoformat(), "losses": "2 acres crop damaged",    "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC012", "type": "property_damage",     "severity": "LOW",    "village_id": "VLG008", "species": "Wild Boar",     "date": (_now - timedelta(days=23)).isoformat(), "losses": "Minor fence damage",      "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC013", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG001", "species": "Asiatic Lion",  "date": (_now - timedelta(days=24)).isoformat(), "losses": "1 buffalo killed",        "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC014", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG006", "species": "Hyena",         "date": (_now - timedelta(days=25)).isoformat(), "losses": "2 sheep killed",          "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC015", "type": "human_injury",        "severity": "HIGH",   "village_id": "VLG001", "species": "Asiatic Lion",  "date": (_now - timedelta(days=26)).isoformat(), "losses": "1 person injured",        "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC016", "type": "crop_damage",         "severity": "LOW",    "village_id": "VLG005", "species": "Nilgai",        "date": (_now - timedelta(days=27)).isoformat(), "losses": "0.5 acres crop",          "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC017", "type": "livestock_predation", "severity": "MEDIUM", "village_id": "VLG004", "species": "Leopard",       "date": (_now - timedelta(days=28)).isoformat(), "losses": "1 goat killed",           "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC018", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG002", "species": "Asiatic Lion",  "date": (_now - timedelta(days=29)).isoformat(), "losses": "3 cattle killed",         "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC019", "type": "crop_damage",         "severity": "MEDIUM", "village_id": "VLG003", "species": "Wild Boar",     "date": (_now - timedelta(days=30)).isoformat(), "losses": "3 acres crop damaged",    "status": "RESOLVED",     "is_demo": True},
    {"incident_id": "INC020", "type": "property_damage",     "severity": "LOW",    "village_id": "VLG007", "species": "Wild Boar",     "date": (_now - timedelta(days=30)).isoformat(), "losses": "Boundary wall damaged",   "status": "RESOLVED",     "is_demo": True},
    # Two active/new incidents for demo workflow
    {"incident_id": "INC021", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG001", "species": "Asiatic Lion",  "date": (_now - timedelta(hours=3)).isoformat(), "losses": "Under assessment",        "status": "NEW",          "is_demo": True},
    {"incident_id": "INC022", "type": "livestock_predation", "severity": "HIGH",   "village_id": "VLG006", "species": "Asiatic Lion",  "date": (_now - timedelta(hours=14)).isoformat(),"losses": "Under assessment",        "status": "ASSIGNED",     "is_demo": True},
]

# ---------------------------------------------------------------------------
# Response Teams (DEMO)
# ---------------------------------------------------------------------------
SAMPLE_RESPONSE_TEAMS = [
    {
        "team_id": "TM001",
        "name": "Gir Rapid Response Alpha",
        "base_lat": 21.1200,
        "base_lon": 70.5600,
        "availability": True,
        "current_status": "STANDBY",
        "specialization": "Large Carnivore Rescue",
        "member_count": 5,
        "contact": "+91-99900-00101",
        "is_demo": True,
    },
    {
        "team_id": "TM002",
        "name": "Gir Forest Guard Bravo",
        "base_lat": 21.0900,
        "base_lon": 70.6100,
        "availability": True,
        "current_status": "STANDBY",
        "specialization": "Community Liaison & Patrol",
        "member_count": 4,
        "contact": "+91-99900-00102",
        "is_demo": True,
    },
    {
        "team_id": "TM003",
        "name": "Wildlife Vet & Rescue Charlie",
        "base_lat": 21.3300,
        "base_lon": 71.0200,
        "availability": False,
        "current_status": "ON_MISSION",
        "specialization": "Veterinary & Tranquilization",
        "member_count": 3,
        "contact": "+91-99900-00103",
        "is_demo": True,
    },
    {
        "team_id": "TM004",
        "name": "Southern Zone Delta",
        "base_lat": 20.8200,
        "base_lon": 71.0400,
        "availability": True,
        "current_status": "STANDBY",
        "specialization": "Crop Conflict & Barrier Repair",
        "member_count": 4,
        "contact": "+91-99900-00104",
        "is_demo": True,
    },
]

# ---------------------------------------------------------------------------
# Sample Agent Logs (DEMO)
# ---------------------------------------------------------------------------
SAMPLE_AGENT_LOGS = [
    {"log_id": "LOG001", "agent": "movement_agent",     "action": "analyze_sighting",       "input_ref": "SGT001", "output_summary": "High risk predicted for VLG001, confidence 0.89", "timestamp": (_now - timedelta(hours=3)).isoformat(),  "escalation_required": True,  "is_demo": True},
    {"log_id": "LOG002", "agent": "alert_agent",        "action": "generate_alert",         "input_ref": "SGT001", "output_summary": "HIGH alert issued for Sasan Gir in English + Gujarati", "timestamp": (_now - timedelta(hours=3)).isoformat(), "escalation_required": True, "is_demo": True},
    {"log_id": "LOG003", "agent": "response_agent",     "action": "create_incident_ticket", "input_ref": "SGT001", "output_summary": "Ticket INC021 created, TM001 recommended — AWAITING OFFICER APPROVAL", "timestamp": (_now - timedelta(hours=3)).isoformat(), "escalation_required": True, "is_demo": True},
    {"log_id": "LOG004", "agent": "compensation_agent", "action": "start_claim",            "input_ref": "INC003", "output_summary": "Claim draft CLM-INC003 prepared — PENDING OFFICER REVIEW", "timestamp": (_now - timedelta(days=6)).isoformat(), "escalation_required": False, "is_demo": True},
    {"log_id": "LOG005", "agent": "hotspot_agent",      "action": "analyze_hotspots",       "input_ref": "ALL",    "output_summary": "Top 3 hotspots identified: Sasan Gir, Talala, Jamvala zones", "timestamp": (_now - timedelta(hours=1)).isoformat(), "escalation_required": False, "is_demo": True},
]

# ---------------------------------------------------------------------------
# Helper: get village by ID
# ---------------------------------------------------------------------------
def get_village_by_id(village_id: str) -> dict | None:
    return next((v for v in SAMPLE_VILLAGES if v["village_id"] == village_id), None)

def get_sightings_near(lat: float, lon: float, radius_deg: float = 0.1) -> list:
    """Return sightings within ~radius_deg degrees of the given coordinate."""
    return [
        s for s in SAMPLE_SIGHTINGS
        if abs(s["lat"] - lat) <= radius_deg and abs(s["lon"] - lon) <= radius_deg
    ]

def get_incidents_for_village(village_id: str) -> list:
    return [i for i in SAMPLE_INCIDENTS if i["village_id"] == village_id]
