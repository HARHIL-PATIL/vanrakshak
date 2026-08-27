"""
VanRakshak AI — Agent 4: Livestock Compensation Assistant Agent
===============================================================
Responsibilities:
  - Collect claim information from the villager/officer
  - Generate a document checklist based on loss type
  - Produce a structured preliminary claim draft
  - Route draft for mandatory Forest Officer review

CRITICAL: This AI NEVER approves or rejects compensation claims.
It only prepares a structured draft. All final decisions are the
sole responsibility of the authorised Forest Department officer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Document checklists by loss type
# ---------------------------------------------------------------------------

DOCUMENT_CHECKLISTS: dict[str, list[str]] = {
    "livestock_predation": [
        "FIR / Police Report copy",
        "Forest Department Incident Report (signed by Range Forest Officer)",
        "Veterinary Certificate (if animal injured; post-mortem report if killed)",
        "Photographs of loss (minimum 3, with date/location stamp)",
        "Livestock ownership proof (Gram Panchayat certificate or purchase receipt)",
        "Bank account details of claimant (passbook copy or cancelled cheque)",
        "Panchnama report (signed by 5 witnesses including village sarpanch)",
        "Aadhaar card copy of claimant",
    ],
    "crop_damage": [
        "Forest Department Crop Damage Inspection Report",
        "Revenue Department Girdavar Report",
        "Photographs of crop damage (minimum 5, with date/location stamp)",
        "Land ownership / tenancy proof (7/12 extract or lease agreement)",
        "Bank account details of claimant",
        "Aadhaar card copy of claimant",
        "Village sarpanch declaration",
    ],
    "human_injury": [
        "FIR / Police Report copy",
        "Hospital / Medical Records (doctor's certificate, treatment summary)",
        "Forest Department Incident Report",
        "Photographs (of injury and incident site)",
        "Disability certificate (if applicable)",
        "Bank account details of claimant or next-of-kin",
        "Aadhaar card copy",
        "Panchnama report",
    ],
    "property_damage": [
        "Forest Department Incident Report",
        "Photographs of property damage",
        "Estimate of repair cost (from registered contractor or PWD)",
        "Property ownership proof",
        "Bank account details of claimant",
        "Aadhaar card copy",
        "Village sarpanch declaration",
    ],
}

# Government compensation rate guidelines (DEMO — indicative only)
COMPENSATION_RATES: dict[str, dict] = {
    "livestock_predation": {
        "cattle":   25000,   # INR
        "buffalo":  30000,
        "goat":      5000,
        "sheep":     4500,
        "poultry":    500,
        "note":     "Rates are indicative per Gujarat Forest Department guidelines (DEMO)",
    },
    "crop_damage": {
        "per_acre": 15000,
        "note":     "Rates are indicative per state agricultural guidelines (DEMO)",
    },
    "human_injury": {
        "minor":    50000,
        "major":   200000,
        "death":   500000,
        "note":     "Rates are indicative per Gujarat compensation scheme (DEMO)",
    },
    "property_damage": {
        "per_incident": 10000,
        "note":          "Assessed case by case by Revenue Department (DEMO)",
    },
}


class CompensationAssistantAgent:
    """
    Agent 4 — Livestock / Crop Compensation Assistant.

    Prepares compensation claim drafts and document checklists.
    NEVER makes approval/rejection decisions — officer-only action.
    """

    AGENT_NAME = "compensation_agent"

    def __init__(self):
        # In-memory claim store (keyed by claim_id)
        self._claims: dict[str, dict] = {}

    def start_claim(
        self,
        incident_id: str,
        villager_info: dict,
        loss_details: dict,
    ) -> dict:
        """
        Initialise a compensation claim draft.

        Steps:
            1. Collect and validate claim information
            2. Retrieve document checklist for the loss type
            3. Look up indicative compensation rates
            4. Build preliminary claim summary
            5. Return structured draft flagged for officer review

        CRITICAL: Returned object is a DRAFT only — requires officer approval.

        Args:
            incident_id   : Related incident ID
            villager_info : {claimant_name, village_id, contact_number}
            loss_details  : {loss_type, loss_description, species_responsible,
                             estimated_loss_value (optional)}

        Returns:
            claim_draft dict
        """
        claim_id  = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        loss_type = loss_details.get("loss_type", "livestock_predation")

        # ── Document checklist ────────────────────────────────────────────
        checklist = self.get_document_checklist(loss_type)

        # ── Indicative compensation rate lookup ───────────────────────────
        rate_info = COMPENSATION_RATES.get(loss_type, {})

        # ── Estimated value fallback ──────────────────────────────────────
        estimated_value = loss_details.get("estimated_loss_value")

        # ── Build claim draft ─────────────────────────────────────────────
        claim_draft = {
            "claim_id":          claim_id,
            "incident_id":       incident_id,
            "agent":             self.AGENT_NAME,
            "claimant_name":     villager_info.get("claimant_name", "Unknown"),
            "claimant_village_id": villager_info.get("village_id", "UNKNOWN"),
            "contact_number":    villager_info.get("contact_number", "N/A"),
            "loss_type":         loss_type,
            "species_responsible": loss_details.get("species_responsible", "Unknown"),
            "loss_description":  loss_details.get("loss_description", "Not provided"),
            "estimated_loss_value": estimated_value,
            "indicative_compensation_rates": rate_info,
            "document_checklist":  checklist,
            "missing_documents":   checklist,     # All docs initially outstanding
            "submitted_documents": [],
            "status":              "DRAFT",
            "created_at":          datetime.now(timezone.utc).isoformat(),
            "updated_at":          datetime.now(timezone.utc).isoformat(),
            "officer_id":          None,
            "officer_notes":       None,
            "human_approval_required": True,
            "disclaimer": (
                "AI-GENERATED DRAFT ONLY — Final approval, rejection, or "
                "disbursement is the sole responsibility of the authorised "
                "Forest Department officer. This AI system never approves or "
                "rejects compensation claims."
            ),
            "next_steps": [
                "Gather all documents from the checklist above",
                "Submit documents to the nearest Forest Department office",
                "Await assigned officer review (typically 15–30 working days)",
                "Forest Officer will verify the claim and incident report on-site",
                "Approved amounts are disbursed directly to bank account",
            ],
            "llm_note": (
                "PROPOSED INTEGRATION: IBM Granite LLM would assist in "
                "auto-filling claim forms and translating document instructions "
                "to Gujarati in production. Template-based fallback used here."
            ),
            "is_demo": True,
        }

        self._claims[claim_id] = claim_draft
        return claim_draft

    def get_document_checklist(self, loss_type: str) -> list[str]:
        """
        Return the required document list for the given loss type.

        Args:
            loss_type : One of: livestock_predation, crop_damage,
                        human_injury, property_damage

        Returns:
            List of required document strings
        """
        return DOCUMENT_CHECKLISTS.get(
            loss_type,
            DOCUMENT_CHECKLISTS["livestock_predation"],   # safe fallback
        )

    def update_claim_documents(
        self,
        claim_id: str,
        submitted_docs: list[str],
        officer_id: Optional[str] = None,
    ) -> dict:
        """
        Mark documents as received and update outstanding checklist.

        Args:
            claim_id       : Target claim
            submitted_docs : List of document names that have been submitted
            officer_id     : Officer processing the update (optional)

        Returns:
            Updated claim summary dict
        """
        claim = self._claims.get(claim_id)
        if claim is None:
            return {"success": False, "error": f"Claim {claim_id} not found", "is_demo": True}

        claim["submitted_documents"] = list(set(claim["submitted_documents"] + submitted_docs))
        claim["missing_documents"]   = [
            d for d in claim["document_checklist"]
            if d not in claim["submitted_documents"]
        ]
        claim["updated_at"] = datetime.now(timezone.utc).isoformat()
        if officer_id:
            claim["officer_id"] = officer_id
        if not claim["missing_documents"]:
            claim["status"] = "SUBMITTED"

        return {
            "success":             True,
            "claim_id":            claim_id,
            "submitted_documents": claim["submitted_documents"],
            "missing_documents":   claim["missing_documents"],
            "status":              claim["status"],
            "is_demo":             True,
        }

    def get_claim(self, claim_id: str) -> Optional[dict]:
        """Retrieve a claim by ID from in-memory store."""
        return self._claims.get(claim_id)

    def list_claims(self, village_id: Optional[str] = None) -> list[dict]:
        """List claims, optionally filtered by village."""
        claims = list(self._claims.values())
        if village_id:
            claims = [c for c in claims if c["claimant_village_id"] == village_id]
        return claims
