# ============================================================
# VanRakshak AI — Agent 4: Livestock Compensation Assistant
# Collects incident + loss details, checks documentation,
# generates preliminary claim summary.
# NEVER approves or rejects — only prepares for human review.
# ============================================================

import uuid
from datetime import datetime

# ---------------------------------------------------------------------------
# Compensation rates (indicative — based on Gujarat govt. guidelines)
# [SAMPLE / INDICATIVE RATES — NOT OFFICIAL]
# ---------------------------------------------------------------------------
_COMP_RATES = {
    "buffalo": 25000,
    "cow":     20000,
    "ox":      20000,
    "horse":   18000,
    "camel":   22000,
    "sheep":   4000,
    "goat":    3500,
    "pig":     2500,
    "dog":     1000,
    "poultry": 200,
    "other":   5000,
}

_REQUIRED_DOCS = [
    "FIR / Forest Guard Witness Report",
    "Panchanama (scene inspection report)",
    "Veterinary Officer certificate (cause of death)",
    "Photograph of dead/injured animal",
    "Village Sarpanch certificate",
    "Bank passbook copy (account details)",
    "Aadhaar card / identity proof",
    "Land / livestock ownership proof",
]


class CompensationAgent:
    """
    Agent 4 — Livestock Compensation Assistant Agent.
    Guides the preparation of compensation claims for livestock loss.
    All claims are submitted for human (officer) review only.
    """

    NAME = "CompensationAgent"
    VERSION = "1.0-PROTOTYPE"

    def __init__(self):
        self.status = "IDLE"
        self.last_action = None
        self.last_confidence = None
        self.last_run = None
        self.total_processed = 0

    # ------------------------------------------------------------------

    def process(self, claim_data: dict, pending_approvals: list) -> dict:
        """
        Generate a preliminary compensation claim summary.

        Parameters
        ----------
        claim_data : {
            incident_id, claimant_name, village_id, village_name,
            species_responsible, livestock_type, livestock_count,
            estimated_loss_inr,  # optional override
            documents_available: [list of doc names],
            notes
        }

        Returns
        -------
        claim dict with checklist, preliminary amount, and approval queue entry.
        """
        self.status = "PROCESSING"

        claim_id      = f"CLM-{uuid.uuid4().hex[:6].upper()}"
        livestock_type = claim_data.get("livestock_type", "other").lower()
        livestock_count = int(claim_data.get("livestock_count", 1))
        rate          = _COMP_RATES.get(livestock_type, _COMP_RATES["other"])
        prelim_amount = claim_data.get("estimated_loss_inr") or (rate * livestock_count)

        docs_available = [d.lower() for d in claim_data.get("documents_available", [])]
        doc_checklist  = self._build_checklist(docs_available)
        docs_complete  = all(item["available"] for item in doc_checklist)
        missing_docs   = [item["document"] for item in doc_checklist if not item["available"]]

        confidence = 0.90 if docs_complete else max(0.50, 0.90 - 0.06 * len(missing_docs))

        claim = {
            "claim_id":           claim_id,
            "incident_id":        claim_data.get("incident_id"),
            "claimant_name":      claim_data.get("claimant_name", "Unknown"),
            "village_id":         claim_data.get("village_id"),
            "village_name":       claim_data.get("village_name"),
            "species_responsible":claim_data.get("species_responsible", "Unknown"),
            "livestock_type":     livestock_type,
            "livestock_count":    livestock_count,
            "rate_per_animal_inr": rate,
            "preliminary_amount_inr": int(prelim_amount),
            "doc_checklist":      doc_checklist,
            "docs_complete":      docs_complete,
            "missing_docs":       missing_docs,
            "confidence":         round(confidence, 2),
            "status":             "DRAFT",
            "timestamp":          datetime.utcnow().isoformat(),
            "notes":              claim_data.get("notes", ""),
            "disclaimer": (
                "PRELIMINARY ASSESSMENT ONLY — Final compensation decision "
                "by authorized Forest Department / Revenue officer. "
                "Amounts are indicative and subject to official verification."
            ),
            "agent_meta": {
                "agent":      self.NAME,
                "version":    self.VERSION,
                "timestamp":  datetime.utcnow().isoformat(),
            },
        }

        # Queue for officer review
        approval_item = {
            "action_id":    f"APR-{uuid.uuid4().hex[:6].upper()}",
            "action_type":  "COMPENSATION_CLAIM",
            "claim_id":     claim_id,
            "ai_recommendation": (
                f"Process compensation claim for {claim_data.get('claimant_name','Unknown')} "
                f"from {claim_data.get('village_name','?')}. "
                f"Preliminary amount: ₹{int(prelim_amount):,}. "
                f"{'All documents present.' if docs_complete else f'Missing {len(missing_docs)} document(s).'}"
            ),
            "confidence":   round(confidence, 2),
            "reasoning": (
                f"{livestock_count} {livestock_type}(s) lost to "
                f"{claim_data.get('species_responsible','wildlife')}. "
                f"Rate: ₹{rate:,}/animal. "
                f"Docs status: {'COMPLETE' if docs_complete else 'INCOMPLETE'}."
            ),
            "status":      "PENDING",
            "timestamp":   datetime.utcnow().isoformat(),
            "village_id":  claim_data.get("village_id"),
        }
        pending_approvals.append(approval_item)
        claim["approval_id"] = approval_item["action_id"]

        self.status = "IDLE"
        self.last_action = (
            f"Drafted claim {claim_id} — ₹{int(prelim_amount):,} "
            f"for {claim_data.get('claimant_name','?')}"
        )
        self.last_confidence = round(confidence, 2)
        self.last_run = datetime.utcnow().isoformat()
        self.total_processed += 1

        return claim

    # ------------------------------------------------------------------

    def _build_checklist(self, docs_available: list) -> list:
        checklist = []
        for doc in _REQUIRED_DOCS:
            available = any(
                word in docs_available
                for word in doc.lower().split()
                if len(word) > 4
            )
            checklist.append({"document": doc, "available": available})
        return checklist

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

    @staticmethod
    def get_required_docs() -> list:
        return list(_REQUIRED_DOCS)

    @staticmethod
    def get_compensation_rates() -> dict:
        return dict(_COMP_RATES)
