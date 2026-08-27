"""
VanRakshak AI — Risk Scoring Engine
=====================================
DISCLAIMER: PROTOTYPE RISK-SCORING MODEL — NOT AN OFFICIALLY VALIDATED FORMULA.
This module implements a weighted composite risk score for human-wildlife conflict
likelihood estimation near Gir Forest villages. Results are indicative only and
MUST be reviewed by a qualified Forest Officer before any field action is taken.

Formula:
    Conflict Risk Score =
      0.30 × Proximity_Score
    + 0.20 × Recent_Movement_Score
    + 0.15 × Time_of_Day_Score
    + 0.15 × Livestock_Density_Score
    + 0.10 × Historical_Frequency_Score
    + 0.10 × Environment_Score

All component scores are normalised to [0, 1].
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Constants — formula weights (must sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHT_PROXIMITY          = 0.30
WEIGHT_RECENT_MOVEMENT    = 0.20
WEIGHT_TIME_OF_DAY        = 0.15
WEIGHT_LIVESTOCK_DENSITY  = 0.15
WEIGHT_HISTORICAL_FREQ    = 0.10
WEIGHT_ENVIRONMENT        = 0.10

assert abs(
    WEIGHT_PROXIMITY + WEIGHT_RECENT_MOVEMENT + WEIGHT_TIME_OF_DAY +
    WEIGHT_LIVESTOCK_DENSITY + WEIGHT_HISTORICAL_FREQ + WEIGHT_ENVIRONMENT - 1.0
) < 1e-9, "Risk formula weights must sum to 1.0"

# Risk level thresholds
THRESHOLD_HIGH   = 0.70
THRESHOLD_MEDIUM = 0.40

# Proximity — distance at which score reaches maximum
PROXIMITY_FULL_SCORE_KM = 0.5   # ≤0.5 km → score = 1.0
PROXIMITY_ZERO_SCORE_KM = 5.0   # ≥5.0 km → score = 0.0

# Livestock density normalisation ceiling
LIVESTOCK_DENSITY_MAX = 600     # livestock count above which score saturates at 1.0

# Historical frequency normalisation ceiling
HISTORICAL_FREQ_MAX = 10        # incidents above which score saturates at 1.0

DISCLAIMER = (
    "PROTOTYPE RISK-SCORING MODEL — NOT AN OFFICIALLY VALIDATED FORMULA. "
    "For demonstration and research purposes only. "
    "Do not use for operational wildlife management decisions without "
    "validation by qualified ecologists and Forest Department officers."
)


# ---------------------------------------------------------------------------
# Individual component calculators
# ---------------------------------------------------------------------------

def compute_proximity_score(distance_km: float) -> float:
    """
    Score = 1.0  if distance ≤ PROXIMITY_FULL_SCORE_KM
    Score scales linearly from 1.0 down to 0.0 between full and zero thresholds.
    Score = 0.0  if distance ≥ PROXIMITY_ZERO_SCORE_KM
    """
    if distance_km <= PROXIMITY_FULL_SCORE_KM:
        return 1.0
    if distance_km >= PROXIMITY_ZERO_SCORE_KM:
        return 0.0
    # Linear interpolation in the intermediate range
    range_km = PROXIMITY_ZERO_SCORE_KM - PROXIMITY_FULL_SCORE_KM
    return 1.0 - (distance_km - PROXIMITY_FULL_SCORE_KM) / range_km


def compute_recent_movement_score(
    sightings_last_24h: int,
    sightings_last_7d: int,
) -> float:
    """
    Weighted recency: recent sightings contribute more.
    Normalised so that 3 sightings in 24 h → 1.0.
    """
    # 24-hour sightings carry triple weight over weekly average
    combined = (sightings_last_24h * 3 + sightings_last_7d) / 4.0
    # Cap at 5 equivalent sightings → score 1.0
    return min(combined / 5.0, 1.0)


def compute_time_of_day_score(hour_utc: int, utc_offset_hours: float = 5.5) -> float:
    """
    Convert UTC hour to local IST hour and apply risk profile:
      - Dawn  (05:00–07:00 IST): 0.9 (HIGH)
      - Day   (07:00–17:00 IST): 0.5 (MEDIUM)
      - Dusk  (17:00–20:00 IST): 0.9 (HIGH)
      - Night (20:00–05:00 IST): 0.9 (HIGH)
    """
    local_hour = (hour_utc + utc_offset_hours) % 24
    if 5 <= local_hour < 7:    # Dawn
        return 0.9
    elif 7 <= local_hour < 17:  # Day
        return 0.5
    elif 17 <= local_hour < 20:  # Dusk
        return 0.9
    else:                        # Night (20–05)
        return 0.9


def compute_livestock_density_score(livestock_count: int) -> float:
    """
    Normalise livestock count against the defined ceiling.
    Higher livestock density → higher attractiveness to predators → higher risk.
    """
    return min(livestock_count / LIVESTOCK_DENSITY_MAX, 1.0)


def compute_historical_frequency_score(incident_count_30d: int) -> float:
    """
    Normalise recent historical incident count.
    More incidents in last 30 days → higher baseline risk.
    """
    return min(incident_count_30d / HISTORICAL_FREQ_MAX, 1.0)


def compute_environment_score(
    is_near_water_body: bool = False,
    is_forest_edge: bool = False,
    vegetation_density: float = 0.5,  # 0=open, 1=dense
) -> float:
    """
    Environment factors that increase wildlife movement into settlements:
    - Proximity to water body (especially in dry season)
    - Forest edge effect
    - Dense vegetation (cover for predators)
    Normalised to [0, 1].
    """
    score = vegetation_density * 0.4  # vegetation contributes up to 0.4
    if is_near_water_body:
        score += 0.35
    if is_forest_edge:
        score += 0.25
    return min(score, 1.0)


# ---------------------------------------------------------------------------
# Haversine distance helper
# ---------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometres between two WGS-84 points."""
    R = 6371.0  # Earth radius km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def compute_risk_score(
    sighting_lat: float,
    sighting_lon: float,
    village_lat: float,
    village_lon: float,
    sightings_last_24h: int,
    sightings_last_7d: int,
    observation_time: Optional[datetime] = None,
    livestock_count: int = 200,
    incident_count_30d: int = 2,
    is_near_water_body: bool = False,
    is_forest_edge: bool = True,
    vegetation_density: float = 0.6,
) -> dict:
    """
    Compute the composite conflict risk score using the VanRakshak formula.

    Returns a dict with:
        risk_score            – float in [0, 1]
        risk_level            – "HIGH" | "MEDIUM" | "LOW"
        component_breakdown   – dict of each weighted component
        confidence            – heuristic confidence value
        disclaimer            – mandatory disclaimer string
    """
    if observation_time is None:
        observation_time = datetime.now(timezone.utc)

    # ---- Compute raw component scores ----------------------------------------
    distance_km = haversine_km(sighting_lat, sighting_lon, village_lat, village_lon)

    proximity          = compute_proximity_score(distance_km)
    recent_movement    = compute_recent_movement_score(sightings_last_24h, sightings_last_7d)
    time_of_day        = compute_time_of_day_score(observation_time.hour)
    livestock_density  = compute_livestock_density_score(livestock_count)
    historical_freq    = compute_historical_frequency_score(incident_count_30d)
    environment        = compute_environment_score(
        is_near_water_body=is_near_water_body,
        is_forest_edge=is_forest_edge,
        vegetation_density=vegetation_density,
    )

    # ---- Apply weights (exact formula) ----------------------------------------
    risk_score = (
        WEIGHT_PROXIMITY         * proximity
        + WEIGHT_RECENT_MOVEMENT * recent_movement
        + WEIGHT_TIME_OF_DAY     * time_of_day
        + WEIGHT_LIVESTOCK_DENSITY * livestock_density
        + WEIGHT_HISTORICAL_FREQ * historical_freq
        + WEIGHT_ENVIRONMENT     * environment
    )

    # Clamp to [0, 1] for floating-point safety
    risk_score = max(0.0, min(1.0, risk_score))

    # ---- Derive risk level ------------------------------------------------
    if risk_score >= THRESHOLD_HIGH:
        risk_level = "HIGH"
    elif risk_score >= THRESHOLD_MEDIUM:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # ---- Heuristic confidence -----------------------------------------------
    # Confidence is higher when more data sources contribute non-zero scores.
    non_zero_components = sum(
        1 for v in [proximity, recent_movement, time_of_day, livestock_density, historical_freq, environment]
        if v > 0
    )
    confidence = 0.5 + 0.08 * non_zero_components  # 0.5 – 0.98 range

    return {
        "risk_score": round(risk_score, 4),
        "risk_level": risk_level,
        "distance_km": round(distance_km, 3),
        "component_breakdown": {
            "proximity_score":            round(proximity, 4),
            "recent_movement_score":      round(recent_movement, 4),
            "time_of_day_score":          round(time_of_day, 4),
            "livestock_density_score":    round(livestock_density, 4),
            "historical_frequency_score": round(historical_freq, 4),
            "environment_score":          round(environment, 4),
        },
        "weighted_components": {
            "proximity":           round(WEIGHT_PROXIMITY * proximity, 4),
            "recent_movement":     round(WEIGHT_RECENT_MOVEMENT * recent_movement, 4),
            "time_of_day":         round(WEIGHT_TIME_OF_DAY * time_of_day, 4),
            "livestock_density":   round(WEIGHT_LIVESTOCK_DENSITY * livestock_density, 4),
            "historical_frequency":round(WEIGHT_HISTORICAL_FREQ * historical_freq, 4),
            "environment":         round(WEIGHT_ENVIRONMENT * environment, 4),
        },
        "confidence": round(min(confidence, 0.98), 4),
        "disclaimer": DISCLAIMER,
        "is_demo": True,
    }
