# ============================================================
# VanRakshak AI — Agent 2: Village Alert & Early Warning Agent
# Converts risk info into calm, actionable bilingual warnings.
# IBM Granite LLM — Natural Language Generation
#   *** Proposed Integration (Simulated in Prototype) ***
# ============================================================

import uuid
from datetime import datetime

# ---------------------------------------------------------------------------
# Gujarati alert templates (hardcoded Unicode)
# ---------------------------------------------------------------------------

_GUJ_TEMPLATES = {
    "HIGH": {
        "Asiatic Lion": (
            "⚠️ ઉચ્ચ જોખમ ચેતવણી: {village} નજીક સિંહ જોવા મળ્યો છે. "
            "તમારા પ્રાણીઓને ઘરની અંદર રાખો. "
            "રાત્રે ઘરની બહાર ન નીકળો. "
            "વન વિભાગ: {contact}."
        ),
        "Leopard": (
            "⚠️ ઉચ્ચ જોખમ ચેતવણી: {village} નજીક દીપડો જોવા મળ્યો છે. "
            "બાળકોને ઘરની અંદર રાખો. ઢોરને સલામત સ્થળે બાંધો. "
            "વન વિભાગ: {contact}."
        ),
        "default": (
            "⚠️ ઉચ્ચ જોખમ ચેતવણી: {village} નજીક {species} જોવા મળ્યા છે. "
            "સાવચેત રહો. વન વિભાગ: {contact}."
        ),
    },
    "MEDIUM": {
        "default": (
            "🟡 સાધારણ ચેતવણી: {village} ક્ષેત્રમાં {species} ની ગતિ નોંધાઈ છે. "
            "સાંજ પછી ઘરની બહાર ન જવો. "
            "ઢોર સલામત રહે તે જુઓ. "
            "વન વિભાગ: {contact}."
        ),
    },
    "LOW": {
        "default": (
            "ℹ️ સામાન્ય સૂચના: {village} ક્ષેત્રમાં {species} ની હાજરી. "
            "નિયમ અને સતર્કતા જાળવો. "
            "સ્થિતિ વન વિભાગ દ્વારા અવલોકન હેઠળ છે."
        ),
    },
}

_EN_TEMPLATES = {
    "HIGH": {
        "Asiatic Lion": (
            "HIGH RISK ALERT — A lion has been sighted near {village} "
            "({distance_km:.1f} km away). "
            "Keep all livestock secured indoors. Do NOT venture outside after dark. "
            "Stay in groups. Contact Forest Dept: {contact}."
        ),
        "Leopard": (
            "HIGH RISK ALERT — A leopard has been sighted near {village} "
            "({distance_km:.1f} km away). "
            "Keep children indoors. Secure all livestock. Avoid jungle paths. "
            "Contact Forest Dept: {contact}."
        ),
        "default": (
            "HIGH RISK ALERT — {species} sighted near {village} "
            "({distance_km:.1f} km away). "
            "Exercise extreme caution. Secure livestock and stay indoors at night. "
            "Contact Forest Dept: {contact}."
        ),
    },
    "MEDIUM": {
        "default": (
            "ELEVATED ALERT — {species} movement recorded near {village}. "
            "Avoid open fields after dusk. Secure livestock in pens. "
            "Monitor your surroundings and report any sightings. "
            "Contact Forest Dept: {contact}."
        ),
    },
    "LOW": {
        "default": (
            "ROUTINE ADVISORY — {species} presence noted in outer forest zones near {village}. "
            "Situation under routine forest department monitoring. "
            "Follow standard precautions. Contact Forest Dept: {contact}."
        ),
    },
}

_SAFETY_ACTIONS = {
    "HIGH": [
        "Immediately secure all livestock in locked pens",
        "Do not leave home alone after dusk",
        "Keep children inside until further notice",
        "Use torches and make noise when moving at night",
        "Report any sighting immediately to 1926 (Forest Dept)",
        "Do not attempt to scare or confront the animal",
    ],
    "MEDIUM": [
        "Secure livestock in pens by early evening",
        "Avoid jungle edges and water bodies after sunset",
        "Keep an eye on children and elderly",
        "Report any unusual animal activity to local Forest Guard",
    ],
    "LOW": [
        "Follow standard wildlife safety precautions",
        "Monitor your livestock at regular intervals",
        "Report any sightings to nearest Forest Guard post",
    ],
}

_FOREST_CONTACT = "+91-2877-285540 / 1926"


class AlertAgent:
    """
    Agent 2 — Village Alert & Early Warning Agent.
    Generates bilingual (English + Gujarati) alert messages for villages
    based on risk assessment output from Agent 1.

    LOW risk = logged only, not broadcast.
    IBM Granite LLM integration is proposed; NLG is simulated in this prototype.
    """

    NAME = "AlertAgent"
    VERSION = "1.0-PROTOTYPE"

    def __init__(self):
        self.status = "IDLE"
        self.last_action = None
        self.last_confidence = None
        self.last_run = None
        self.total_processed = 0
        self.alerts_generated = []

    # ------------------------------------------------------------------

    def process(self, movement_result: dict, sighting: dict, village: dict) -> dict:
        """
        Generate an alert from movement-agent output.

        Returns
        -------
        dict with keys:
            alert_id, severity, village, species, risk_score, confidence,
            broadcast, en_text, gu_text, safety_actions, agent_meta
        """
        self.status = "PROCESSING"

        risk_level  = movement_result.get("risk_level", "LOW")
        risk_score  = movement_result.get("risk_score", 0.0)
        confidence  = movement_result.get("confidence", 0.70)
        species     = sighting.get("species", "Unknown")
        distance_km = sighting.get("distance_km", 2.0)
        village_name = village["name"]

        broadcast = risk_level != "LOW"

        en_text = self._render_en(risk_level, species, village_name, distance_km)
        gu_text = self._render_gu(risk_level, species, village_name)

        alert = {
            "alert_id":      f"ALT-{uuid.uuid4().hex[:6].upper()}",
            "severity":      risk_level,
            "village_id":    village["id"],
            "village_name":  village_name,
            "species":       species,
            "risk_score":    risk_score,
            "confidence":    confidence,
            "broadcast":     broadcast,
            "en_text":       en_text,
            "gu_text":       gu_text,
            "safety_actions": _SAFETY_ACTIONS.get(risk_level, _SAFETY_ACTIONS["LOW"]),
            "timestamp":     datetime.utcnow().isoformat(),
            "nlg_note":      "IBM Granite LLM — Natural Language Generation (Proposed Integration — Simulated in Prototype)",
            "agent_meta": {
                "agent":      self.NAME,
                "version":    self.VERSION,
                "timestamp":  datetime.utcnow().isoformat(),
                "disclaimer": "PROTOTYPE — alert text is template-generated",
            },
        }

        self.alerts_generated.append(alert)
        self.status = "IDLE"
        self.last_action = f"{'Broadcast' if broadcast else 'Logged'} {risk_level} alert for {village_name}"
        self.last_confidence = confidence
        self.last_run = datetime.utcnow().isoformat()
        self.total_processed += 1

        return alert

    # ------------------------------------------------------------------

    def _render_en(self, level: str, species: str,
                   village_name: str, distance_km: float) -> str:
        bucket = _EN_TEMPLATES.get(level, _EN_TEMPLATES["LOW"])
        template = bucket.get(species, bucket.get("default", ""))
        return template.format(
            village=village_name,
            species=species,
            distance_km=distance_km,
            contact=_FOREST_CONTACT,
        )

    def _render_gu(self, level: str, species: str, village_name: str) -> str:
        bucket = _GUJ_TEMPLATES.get(level, _GUJ_TEMPLATES["LOW"])
        template = bucket.get(species, bucket.get("default", ""))
        return template.format(
            village=village_name,
            species=species,
            contact=_FOREST_CONTACT,
        )

    def get_status(self) -> dict:
        return {
            "agent":            self.NAME,
            "status":           self.status,
            "last_action":      self.last_action,
            "last_confidence":  self.last_confidence,
            "last_run":         self.last_run,
            "total_processed":  self.total_processed,
            "escalation_state": "NONE",
        }
