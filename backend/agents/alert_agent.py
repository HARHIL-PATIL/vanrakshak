"""
VanRakshak AI — Agent 2: Village Alert & Early Warning Agent
=============================================================
Responsibilities:
  - Determine whether a risk assessment warrants a public alert
  - Generate bilingual (English + Gujarati) alert messages from templates
  - Specify safety actions appropriate for the species
  - Return structured alert with severity badge and confidence

NOTE: IBM Granite LLM is proposed for production to generate dynamic,
context-aware multilingual messages. This prototype uses pre-defined
templates as a functional fallback.

All alerts are labelled DEMO and must be reviewed by a Forest Officer
before actual broadcast to villagers.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Gujarati species translations
# ---------------------------------------------------------------------------
SPECIES_GUJARATI: dict[str, str] = {
    "Asiatic Lion":  "સિંહ",
    "Leopard":       "દીપડો",
    "Hyena":         "લકડબઘ્ઘો",
    "Nilgai":        "નીલગાય",
    "Wild Boar":     "જંગલી ભૂંડ",
}

# ---------------------------------------------------------------------------
# Safety actions by species group
# ---------------------------------------------------------------------------
SAFETY_ACTIONS_LARGE_CARNIVORE = [
    "Secure livestock immediately — bring animals inside before dark",
    "Do not go out alone at night or dawn",
    "Contact Forest Department helpline: 1800-XXX-XXXX",
    "Use torch/flashlight if moving outside",
    "Follow Forest Department instructions at all times",
    "Alert neighbours and village panchayat",
]

SAFETY_ACTIONS_HERBIVORE = [
    "Keep livestock secured and crops fenced",
    "Avoid the mentioned area until cleared by Forest Department",
    "Report further sightings to the nearest forest post",
    "Do not attempt to chase or drive away the animal",
]

SAFETY_ACTIONS_HYENA = [
    "Secure small livestock and poultry immediately",
    "Avoid leaving livestock unattended at night",
    "Contact Forest Department helpline: 1800-XXX-XXXX",
    "Report further sightings to the nearest forest post",
]

def _get_safety_actions(species: str) -> list[str]:
    if species in ("Asiatic Lion", "Leopard"):
        return SAFETY_ACTIONS_LARGE_CARNIVORE
    elif species == "Hyena":
        return SAFETY_ACTIONS_HYENA
    else:
        return SAFETY_ACTIONS_HERBIVORE


# ---------------------------------------------------------------------------
# Message template builders
# ---------------------------------------------------------------------------

def _english_message(risk_level: str, species: str, village_name: str, risk_score: float) -> str:
    """
    Build an English alert message from a template.
    NOTE: IBM Granite LLM PROPOSED for production — dynamic contextual messaging.
    """
    score_pct = round(risk_score * 100, 1)
    if risk_level == "HIGH":
        return (
            f"⚠️ HIGH ALERT — {species} sighted near {village_name}. "
            f"Conflict risk score: {score_pct}%. "
            f"Please secure livestock and follow safety guidelines immediately. "
            f"Forest Department has been notified. [DEMO ALERT]"
        )
    elif risk_level == "MEDIUM":
        return (
            f"⚡ CAUTION — {species} activity detected near {village_name} area. "
            f"Conflict risk score: {score_pct}%. "
            f"Please remain vigilant and secure livestock. "
            f"Forest Department is monitoring the situation. [DEMO ALERT]"
        )
    else:  # LOW
        return (
            f"ℹ️ INFO — {species} movement logged near {village_name} area. "
            f"Risk is currently LOW ({score_pct}%). "
            f"No immediate action required — continue normal precautions. [DEMO LOG]"
        )


def _gujarati_message(risk_level: str, species: str, village_name: str) -> str:
    """
    Build a Gujarati alert message from template.
    NOTE: IBM Granite LLM PROPOSED for production — dynamic Gujarati generation.

    Templates:
      HIGH   : "ઉચ્ચ ચેતવણી: {species_guj} {village_guj} ગામ નજીક જોવા મળ્યા છે."
      MEDIUM : "સાવચેતી: {species_guj} {village_guj} વિસ્તારમાં ગતિ-વિધિ નોંધાઈ છે."
      LOW    : internal log only — no public broadcast
    """
    species_guj = SPECIES_GUJARATI.get(species, species)
    if risk_level == "HIGH":
        return (
            f"ઉચ્ચ ચેતવણી: {species_guj} {village_name} ગામ નજીક જોવા મળ્યા છે. "
            f"કૃપા કરી સાવચેત રહો. પશુઓને સુરક્ષિત સ્થળે રાખો. "
            f"વન વિભાગને જાણ કરવામાં આવી છે. [ડેમો ચેતવણી]"
        )
    elif risk_level == "MEDIUM":
        return (
            f"સાવચેતી: {species_guj} {village_name} વિસ્તારમાં ગતિ-વિધિ નોંધાઈ છે. "
            f"પશુઓને સુરક્ષિત રાખો. "
            f"વન વિભાગ નજર રાખી રહ્યો છે. [ડેમો ચેતવણી]"
        )
    else:
        return f"[ડેમો નોંધ] {species_guj} {village_name} વિસ્તારમાં નોંધ્યા. જોખમ ઓછું છે."


# ---------------------------------------------------------------------------
# Alert Agent
# ---------------------------------------------------------------------------

class AlertAgent:
    """
    Agent 2 — Village Alert & Early Warning.

    Generates bilingual (English + Gujarati) alerts based on risk assessment
    output from Agent 1. Uses template-based message generation for the
    prototype; IBM Granite LLM is the proposed production replacement.
    """

    AGENT_NAME = "alert_agent"

    # Minimum risk score to issue a public broadcast alert
    BROADCAST_THRESHOLD_HIGH   = 0.70
    BROADCAST_THRESHOLD_MEDIUM = 0.40

    def generate_alert(
        self,
        risk_assessment: dict,
        village: dict,
        species: str,
    ) -> dict:
        """
        Determine alert need and generate a structured bilingual alert.

        Steps:
            1. Evaluate risk level against broadcast thresholds
            2. Generate English template message
            3. Generate Gujarati template message
            4. Select appropriate safety actions for the species
            5. Assemble and return structured alert dict

        Args:
            risk_assessment : Output dict from MovementPredictionAgent.analyze()
                              (must contain risk_assessment.risk_score, consensus_risk_level)
            village         : Village dict (name, village_id, contact_number, …)
            species         : Wildlife species string

        Returns:
            Alert dict with severity_badge, messages, actions, broadcast_required, etc.
        """
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"

        # Extract risk info — support both flat and nested result formats
        if "risk_assessment" in risk_assessment:
            risk_score = risk_assessment["risk_assessment"]["risk_score"]
            risk_level = risk_assessment.get("consensus_risk_level",
                         risk_assessment["risk_assessment"]["risk_level"])
            confidence = risk_assessment["risk_assessment"].get("confidence", 0.75)
        else:
            risk_score = risk_assessment.get("risk_score", 0.5)
            risk_level = risk_assessment.get("risk_level", "MEDIUM")
            confidence = risk_assessment.get("confidence", 0.75)

        village_name = village.get("name", "Unknown Village")
        village_id   = village.get("village_id", "UNKNOWN")

        # ── Step 1: Broadcast decision ─────────────────────────────────────
        broadcast_required = risk_level in ("HIGH", "MEDIUM")
        public_broadcast   = risk_level == "HIGH"

        # ── Step 2: English message ────────────────────────────────────────
        msg_en = _english_message(risk_level, species, village_name, risk_score)

        # ── Step 3: Gujarati message ───────────────────────────────────────
        msg_gu = _gujarati_message(risk_level, species, village_name)

        # ── Step 4: Safety actions ─────────────────────────────────────────
        safety_actions = _get_safety_actions(species)

        # ── Step 5: Severity badge ─────────────────────────────────────────
        severity_badge_map = {
            "HIGH":   "🔴 HIGH",
            "MEDIUM": "🟡 MEDIUM",
            "LOW":    "🟢 LOW",
        }
        severity_badge = severity_badge_map.get(risk_level, "⚪ UNKNOWN")

        return {
            "alert_id":           alert_id,
            "agent":              self.AGENT_NAME,
            "species":            species,
            "village_id":         village_id,
            "village_name":       village_name,
            "severity":           risk_level,
            "severity_badge":     severity_badge,
            "risk_score":         round(risk_score, 4),
            "confidence":         round(float(confidence), 4),
            "broadcast_required": broadcast_required,
            "public_broadcast":   public_broadcast,
            "message_english":    msg_en,
            "message_gujarati":   msg_gu,
            "safety_actions":     safety_actions,
            "contact_number":     village.get("contact_number", "N/A"),
            "issued_at":          datetime.now(timezone.utc).isoformat(),
            "llm_note": (
                "PROPOSED INTEGRATION: IBM Granite LLM would generate dynamic, "
                "context-aware multilingual messages in production. "
                "Template-based fallback used in this prototype."
            ),
            "human_approval_required": True,
            "approval_note": (
                "Alert content must be reviewed by Forest Officer before "
                "broadcast to villagers."
            ),
            "is_demo": True,
        }

    def should_alert(self, risk_score: float) -> bool:
        """Quick check: is a risk score above the alert threshold?"""
        return risk_score >= self.BROADCAST_THRESHOLD_MEDIUM
