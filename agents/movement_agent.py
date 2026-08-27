# ============================================================
# VanRakshak AI — Agent 1: Wildlife Movement Prediction Agent
# Analyzes temporal/spatial patterns from sightings and
# estimates movement probability using the risk engine.
# ============================================================

import math
from datetime import datetime, timedelta
from ml.risk_engine import compute_risk


class MovementAgent:
    """
    Agent 1 — Wildlife Movement Prediction Agent.
    Analyses historical sighting patterns, calculates recency-weighted
    sighting frequency, and estimates risk for a given wildlife event.
    """

    NAME = "MovementAgent"
    VERSION = "1.0-PROTOTYPE"

    def __init__(self):
        self.status = "IDLE"
        self.last_action = None
        self.last_confidence = None
        self.last_run = None
        self.total_processed = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def process(self, sighting: dict, village: dict,
                all_sightings: list, all_incidents: list) -> dict:
        """
        Analyse a new wildlife sighting and predict conflict risk.

        Parameters
        ----------
        sighting       : the incoming sighting dict
        village        : the nearest village dict
        all_sightings  : full historical sightings list (for pattern analysis)
        all_incidents  : full historical incidents list

        Returns
        -------
        dict with keys:
            predicted_risk_zone, movement_probability, confidence,
            feature_breakdown, risk_assessment, agent_meta
        """
        self.status = "PROCESSING"

        species      = sighting.get("species", "Unknown")
        distance_km  = sighting.get("distance_km", 2.0)
        time_of_day  = sighting.get("time_of_day", "night")

        # --- Core risk computation ---
        risk = compute_risk(
            village, all_sightings, all_incidents,
            species, distance_km, time_of_day
        )

        # --- Spatial pattern analysis ---
        movement_prob = self._calc_movement_probability(
            sighting, village, all_sightings, risk["components"]
        )

        # --- Predicted risk zone ---
        if risk["risk_score"] >= 0.70:
            risk_zone = f"{village['name']} IMMEDIATE PERIMETER — HIGH ALERT"
        elif risk["risk_score"] >= 0.40:
            risk_zone = f"{village['name']} BUFFER ZONE — ELEVATED WATCH"
        else:
            risk_zone = f"{village['name']} OUTER FOREST EDGE — ROUTINE MONITOR"

        feature_breakdown = {
            "species_threat_level": risk["components"]["environment"],
            "proximity_to_village": risk["components"]["proximity"],
            "recency_weighted_freq": risk["components"]["recent_movement"],
            "time_risk_factor":      risk["components"]["time_of_day"],
            "livestock_attractant":  risk["components"]["livestock_density"],
            "historical_pattern":    risk["components"]["historical_frequency"],
        }

        result = {
            "predicted_risk_zone":   risk_zone,
            "movement_probability":  round(movement_prob, 3),
            "confidence":            risk["confidence"],
            "risk_score":            risk["risk_score"],
            "risk_level":            risk["risk_level"],
            "feature_breakdown":     feature_breakdown,
            "risk_assessment":       risk,
            "agent_meta": {
                "agent":      self.NAME,
                "version":    self.VERSION,
                "timestamp":  datetime.utcnow().isoformat(),
                "disclaimer": "PROTOTYPE — predictions are indicative only",
            },
        }

        # Update agent state
        self.status = "IDLE"
        self.last_action = f"Analyzed {sighting.get('id','?')} — {species} near {village['name']}"
        self.last_confidence = risk["confidence"]
        self.last_run = datetime.utcnow().isoformat()
        self.total_processed += 1

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _calc_movement_probability(self, sighting: dict, village: dict,
                                   all_sightings: list, components: dict) -> float:
        """
        Estimate probability (0-1) that the animal will move closer
        to the village within the next 3 hours based on:
          - time of day (nocturnal = higher)
          - current distance
          - clustering with other recent sightings nearby
        """
        time_factor      = components.get("time_of_day", 0.5)
        proximity_factor = components.get("proximity", 0.5)
        cluster_factor   = self._cluster_factor(sighting, all_sightings)

        prob = 0.50 * time_factor + 0.30 * proximity_factor + 0.20 * cluster_factor
        return min(1.0, max(0.0, prob))

    def _cluster_factor(self, sighting: dict, all_sightings: list,
                        radius_km: float = 3.0, hours: int = 48) -> float:
        """
        If multiple sightings are clustered near this location recently,
        it indicates a territory or hunting pattern — increasing movement prob.
        """
        lat   = sighting.get("lat", 0)
        lon   = sighting.get("lon", 0)
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        nearby = 0

        for s in all_sightings:
            if s.get("id") == sighting.get("id"):
                continue
            try:
                ts = datetime.fromisoformat(s["timestamp"])
            except (KeyError, ValueError):
                continue
            if ts < cutoff:
                continue
            dist = _haversine(lat, lon, s.get("lat", 0), s.get("lon", 0))
            if dist <= radius_km:
                nearby += 1

        return min(1.0, nearby / 4.0)

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


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _haversine(lat1, lon1, lat2, lon2) -> float:
    """Return great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
