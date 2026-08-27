# ============================================================
# VanRakshak AI — ML Risk Scoring Engine
# *** PROTOTYPE MODEL — FOR DEMONSTRATION ONLY ***
# Weighted formula:
#   Risk = 0.30×Proximity + 0.20×Recent_Movement + 0.15×Time_of_Day
#          + 0.15×Livestock_Density + 0.10×Historical_Frequency + 0.10×Environment
# ============================================================

from datetime import datetime, timedelta
import math

# Weights (must sum to 1.0)
WEIGHTS = {
    "proximity":           0.30,
    "recent_movement":     0.20,
    "time_of_day":         0.15,
    "livestock_density":   0.15,
    "historical_frequency":0.10,
    "environment":         0.10,
}

# Risk thresholds
HIGH_THRESHOLD   = 0.70
MEDIUM_THRESHOLD = 0.40


def _score_proximity(distance_km: float) -> float:
    """Normalise distance to [0,1] where 0 km = 1.0 and >=5 km = 0.0."""
    if distance_km <= 0:
        return 1.0
    if distance_km >= 5.0:
        return 0.0
    return max(0.0, 1.0 - (distance_km / 5.0))


def _score_time_of_day(time_label: str) -> float:
    """Night/dusk/dawn are higher risk for large predators."""
    mapping = {
        "night": 1.0,
        "dusk":  0.85,
        "dawn":  0.80,
        "morning": 0.35,
        "afternoon": 0.25,
        "midday": 0.20,
    }
    return mapping.get(time_label.lower(), 0.50)


def _score_recent_movement(sightings: list, village_id: str, hours_window: int = 24) -> float:
    """Recency-weighted sighting frequency near a village within the time window."""
    cutoff = datetime.utcnow() - timedelta(hours=hours_window)
    score = 0.0
    for s in sightings:
        if s.get("nearest_village") != village_id:
            continue
        try:
            ts = datetime.fromisoformat(s["timestamp"])
        except (KeyError, ValueError):
            continue
        if ts < cutoff:
            continue
        hours_ago = max(1, (datetime.utcnow() - ts).total_seconds() / 3600)
        recency_weight = math.exp(-0.1 * hours_ago)
        score += recency_weight
    return min(1.0, score / 3.0)  # cap at 3 sightings = full score


def _score_livestock_density(livestock_count: int) -> float:
    """Normalise to [0,1]: 0 animals = 0.0, >=400 = 1.0."""
    return min(1.0, livestock_count / 400.0)


def _score_historical_frequency(incidents: list, village_id: str, days_window: int = 90) -> float:
    """Number of incidents in the past N days normalised to [0,1]."""
    cutoff = datetime.utcnow() - timedelta(days=days_window)
    count = 0
    for inc in incidents:
        if inc.get("village_id") != village_id:
            continue
        try:
            ts = datetime.fromisoformat(inc["timestamp"])
        except (KeyError, ValueError):
            continue
        if ts >= cutoff:
            count += 1
    return min(1.0, count / 5.0)  # 5+ incidents = full score


def _score_environment(species: str) -> float:
    """Environmental/species-specific base risk factor."""
    mapping = {
        "Asiatic Lion":  0.90,
        "Leopard":       0.80,
        "Hyena":         0.55,
        "Wild Boar":     0.30,
        "Wolf":          0.60,
        "Sloth Bear":    0.65,
    }
    return mapping.get(species, 0.50)


def _risk_level(score: float) -> str:
    if score >= HIGH_THRESHOLD:
        return "HIGH"
    if score >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def _confidence(components: dict, n_sightings_used: int) -> float:
    """Simple confidence heuristic based on data completeness."""
    base = 0.70
    if n_sightings_used >= 3:
        base += 0.10
    if n_sightings_used >= 6:
        base += 0.05
    variance = max(components.values()) - min(components.values())
    if variance > 0.6:
        base -= 0.05
    return min(0.97, round(base, 2))


def compute_risk(
    village: dict,
    sightings: list,
    incidents: list,
    species: str,
    distance_km: float,
    time_of_day: str,
) -> dict:
    """
    Compute a conflict risk score for a village given a new wildlife event.

    Returns:
        {
            risk_score: float,
            risk_level: str,
            confidence: float,
            components: { proximity, recent_movement, time_of_day,
                          livestock_density, historical_frequency, environment },
            model_version: str,
            disclaimer: str,
        }
    """
    village_id = village["id"]
    livestock_count = village.get("livestock_count", 100)

    components = {
        "proximity":            _score_proximity(distance_km),
        "recent_movement":      _score_recent_movement(sightings, village_id),
        "time_of_day":          _score_time_of_day(time_of_day),
        "livestock_density":    _score_livestock_density(livestock_count),
        "historical_frequency": _score_historical_frequency(incidents, village_id),
        "environment":          _score_environment(species),
    }

    risk_score = sum(WEIGHTS[k] * v for k, v in components.items())
    risk_score = round(min(1.0, max(0.0, risk_score)), 3)

    n_sightings = sum(1 for s in sightings if s.get("nearest_village") == village_id)

    return {
        "risk_score":   risk_score,
        "risk_level":   _risk_level(risk_score),
        "confidence":   _confidence(components, n_sightings),
        "components":   {k: round(v, 3) for k, v in components.items()},
        "weights":      WEIGHTS,
        "model_version": "VanRakshak-RiskEngine-v0.1-PROTOTYPE",
        "disclaimer":   "PROTOTYPE MODEL — Results are indicative only. Do not use for real field decisions.",
    }


def batch_assess_villages(villages: list, sightings: list, incidents: list) -> list:
    """
    Quick batch risk assessment for all villages using dominant species
    from recent sightings.  Returns list of assessment dicts.
    """
    results = []
    for village in villages:
        vid = village["id"]
        # find most recent sighting near village
        local_sightings = [s for s in sightings if s.get("nearest_village") == vid]
        if local_sightings:
            local_sightings.sort(key=lambda s: s.get("timestamp", ""), reverse=True)
            latest = local_sightings[0]
            species = latest["species"]
            distance_km = latest.get("distance_km", 2.0)
            time_of_day = latest.get("time_of_day", "night")
        else:
            species = "Asiatic Lion"
            distance_km = 4.0
            time_of_day = "morning"

        result = compute_risk(village, sightings, incidents, species, distance_km, time_of_day)
        result["village_id"] = vid
        result["village_name"] = village["name"]
        results.append(result)
    return results
