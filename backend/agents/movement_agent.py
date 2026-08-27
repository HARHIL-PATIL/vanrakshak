"""
VanRakshak AI — Agent 1: Wildlife Movement Prediction Agent
============================================================
Responsibilities:
  - Ingest a new sighting event
  - Extract contextual features from sample data
  - Call the RandomForest movement predictor
  - Call the weighted risk scoring engine
  - Return a structured prediction + risk assessment result

Every result is labelled as DEMO / SIMULATED.
Human officer review is required before any consequential field action.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from data.sample_data import (
    SAMPLE_SIGHTINGS,
    SAMPLE_INCIDENTS,
    get_village_by_id,
    get_sightings_near,
)
from ml.movement_predictor import get_predictor
from ml.risk_engine import compute_risk_score, haversine_km


class MovementPredictionAgent:
    """
    Agent 1 — Wildlife Movement Prediction.

    Combines ML movement prediction with the weighted risk formula to produce
    a unified risk assessment for a given sighting + target village pair.
    """

    AGENT_NAME = "movement_agent"

    def analyze(
        self,
        sighting_data: dict,
        village_id: str,
        seasonal_factor: float = 0.5,
    ) -> dict:
        """
        Full analysis pipeline for a wildlife sighting near a village.

        Steps:
            1. Load village and nearby sighting history from sample data
            2. Compute 7 ML features
            3. Call RandomForest movement predictor
            4. Call weighted risk scoring engine
            5. Merge results into a unified structured response

        Args:
            sighting_data:   Dict with keys: sighting_id, species, lat, lon,
                             timestamp, confidence, source, count
            village_id:      Target village identifier
            seasonal_factor: 0–1 seasonal risk modifier (0.5 default)

        Returns:
            Structured dict with prediction, risk_assessment, agent metadata
        """
        # ── Step 1: Resolve village ────────────────────────────────────────
        village = get_village_by_id(village_id)
        if village is None:
            # Graceful fallback — use sighting location as proxy
            village = {
                "village_id": village_id,
                "name": "Unknown Village",
                "lat": sighting_data["lat"],
                "lon": sighting_data["lon"],
                "livestock_count": 200,
                "population": 1000,
                "risk_zone": "UNKNOWN",
            }

        s_lat = sighting_data["lat"]
        s_lon = sighting_data["lon"]
        v_lat = village["lat"]
        v_lon = village["lon"]

        # ── Step 2: Compute features ───────────────────────────────────────
        # 2a. Recent sightings near the event location (within ~0.1° ≈ 10 km)
        nearby_sightings = get_sightings_near(s_lat, s_lon, radius_deg=0.1)
        obs_time = self._parse_time(sighting_data.get("timestamp"))
        sightings_24h = sum(
            1 for s in nearby_sightings
            if self._hours_ago(s["timestamp"], obs_time) <= 24
        )
        sightings_7d = sum(
            1 for s in nearby_sightings
            if self._hours_ago(s["timestamp"], obs_time) <= 168
        )

        # 2b. Recency-weighted sighting frequency (normalised to [0,1], cap 5)
        recency_freq = min((sightings_24h * 3 + sightings_7d) / (4.0 * 5.0), 1.0)

        # 2c. Distance from sighting to village
        distance_km = haversine_km(s_lat, s_lon, v_lat, v_lon)

        # 2d. Historical incident frequency for this village (last 30 days)
        village_incidents = [
            i for i in SAMPLE_INCIDENTS
            if i["village_id"] == village_id
            and self._days_ago(i["date"], obs_time) <= 30
        ]
        historical_freq_norm = min(len(village_incidents) / 10.0, 1.0)

        # 2e. Livestock density normalised
        livestock_norm = min(village.get("livestock_count", 200) / 600.0, 1.0)

        # 2f. Environment factor — villages near Gir edge are assumed forest-edge
        environment_factor = 0.7 if village.get("risk_zone") in ("HIGH", "MEDIUM") else 0.4

        # ── Step 3: ML Movement Predictor ──────────────────────────────────
        predictor = get_predictor()
        ml_result = predictor.predict(
            recency_weighted_sighting_freq=recency_freq,
            distance_to_settlement_km=distance_km,
            observation_time=obs_time,
            seasonal_factor=seasonal_factor,
            historical_conflict_freq_norm=historical_freq_norm,
            livestock_density_norm=livestock_norm,
            environment_factor=environment_factor,
        )

        # ── Step 4: Risk Scoring Engine ────────────────────────────────────
        risk_result = compute_risk_score(
            sighting_lat=s_lat,
            sighting_lon=s_lon,
            village_lat=v_lat,
            village_lon=v_lon,
            sightings_last_24h=sightings_24h,
            sightings_last_7d=sightings_7d,
            observation_time=obs_time,
            livestock_count=village.get("livestock_count", 200),
            incident_count_30d=len(village_incidents),
            is_near_water_body=False,
            is_forest_edge=(village.get("risk_zone") in ("HIGH", "MEDIUM")),
            vegetation_density=0.6,
        )

        # ── Step 5: Assemble structured result ─────────────────────────────
        assessment_id = f"ASSESS-{uuid.uuid4().hex[:8].upper()}"

        # Consensus risk level: take the more conservative of ML vs formula
        risk_level_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "UNKNOWN": 0}
        ml_risk = ml_result["predicted_risk_zone"]
        formula_risk = risk_result["risk_level"]
        consensus_risk = ml_risk if risk_level_order.get(ml_risk, 0) >= risk_level_order.get(formula_risk, 0) else formula_risk

        return {
            "assessment_id": assessment_id,
            "agent": self.AGENT_NAME,
            "sighting_id": sighting_data.get("sighting_id", "UNKNOWN"),
            "species": sighting_data.get("species", "Unknown"),
            "village_id": village_id,
            "village_name": village.get("name", "Unknown"),
            "distance_km": round(distance_km, 3),
            "consensus_risk_level": consensus_risk,
            "movement_prediction": {
                "predicted_risk_zone":  ml_result["predicted_risk_zone"],
                "movement_probability": ml_result["movement_probability"],
                "confidence_score":     ml_result["confidence_score"],
                "class_probabilities":  ml_result["class_probabilities"],
                "feature_importance":   ml_result["feature_importance"],
            },
            "risk_assessment": {
                "risk_score":           risk_result["risk_score"],
                "risk_level":           risk_result["risk_level"],
                "component_breakdown":  risk_result["component_breakdown"],
                "weighted_components":  risk_result["weighted_components"],
                "confidence":           risk_result["confidence"],
            },
            "context": {
                "sightings_last_24h":        sightings_24h,
                "sightings_last_7d":         sightings_7d,
                "village_incidents_30d":     len(village_incidents),
                "livestock_count":           village.get("livestock_count", 200),
                "recency_weighted_freq":     round(recency_freq, 4),
            },
            "human_approval_required": consensus_risk in ("HIGH", "MEDIUM"),
            "analyzed_at": obs_time.isoformat(),
            "disclaimer": (
                "PROTOTYPE MODEL — Results are indicative only. "
                "Validated Forest Officer review required before field action."
            ),
            "is_demo": True,
        }

    # ── Private helpers ────────────────────────────────────────────────────

    @staticmethod
    def _parse_time(ts) -> datetime:
        """Parse ISO timestamp string or return current UTC time."""
        if ts is None:
            return datetime.now(timezone.utc)
        if isinstance(ts, datetime):
            return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
        try:
            from dateutil.parser import parse as dateutil_parse
            dt = dateutil_parse(str(ts))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

    @staticmethod
    def _hours_ago(ts_str, reference: datetime) -> float:
        """Return how many hours before `reference` the timestamp is."""
        try:
            from dateutil.parser import parse as dateutil_parse
            dt = dateutil_parse(str(ts_str))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = reference - dt
            return max(delta.total_seconds() / 3600.0, 0.0)
        except Exception:
            return 9999.0

    @staticmethod
    def _days_ago(ts_str, reference: datetime) -> float:
        """Return how many days before `reference` the timestamp is."""
        try:
            from dateutil.parser import parse as dateutil_parse
            dt = dateutil_parse(str(ts_str))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = reference - dt
            return max(delta.total_seconds() / 86400.0, 0.0)
        except Exception:
            return 9999.0
