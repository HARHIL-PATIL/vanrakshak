"""
VanRakshak AI — ML Movement Predictor
=======================================
DEMO / SIMULATED MODEL — This predictor is trained on synthetic data and is
intended solely for prototype demonstration. It does NOT reflect real Gir
Forest wildlife movement patterns.

Architecture:
    - Algorithm  : RandomForestClassifier (scikit-learn)
    - Task       : 3-class classification → HIGH / MEDIUM / LOW risk zone
    - Features   : 7 features derived from sighting and village context
    - Training   : ~200 synthetic samples generated at module load time

Feature vector (7 dimensions):
    [0] recency_weighted_sighting_freq  – normalised sighting frequency (recent-weighted)
    [1] distance_to_settlement_norm     – normalised distance to nearest village
    [2] time_of_day_risk                – 0/0.5/0.9 time-band risk
    [3] seasonal_pattern                – 0–1 seasonal risk factor
    [4] historical_conflict_freq        – normalised 30-day incident count
    [5] livestock_density_norm          – normalised livestock count
    [6] environment_factor              – composite environment score
"""

from __future__ import annotations

import warnings
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Suppress sklearn convergence warnings in demo context
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Label definitions
# ---------------------------------------------------------------------------
RISK_CLASSES = ["LOW", "MEDIUM", "HIGH"]
FEATURE_NAMES = [
    "recency_weighted_sighting_freq",
    "distance_to_settlement_norm",
    "time_of_day_risk",
    "seasonal_pattern",
    "historical_conflict_freq",
    "livestock_density_norm",
    "environment_factor",
]

DISCLAIMER = (
    "DEMO / SIMULATED ML MODEL — Trained on synthetic data. "
    "NOT suitable for real operational wildlife management decisions."
)


# ---------------------------------------------------------------------------
# Synthetic training data generator
# ---------------------------------------------------------------------------

def _generate_synthetic_training_data(n_samples: int = 200, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training samples that approximate plausible risk patterns.
    Each sample represents a wildlife-village proximity scenario.

    Label assignment heuristic (mirrors the risk_engine formula logic):
        - HIGH   : high proximity + recent sightings + night/dawn + high livestock
        - MEDIUM : moderate proximity or moderate activity
        - LOW    : distant, infrequent, daytime, low livestock
    """
    rng = np.random.default_rng(seed)

    X_list, y_list = [], []

    for _ in range(n_samples):
        # Feature 0: recency_weighted_sighting_freq  [0, 1]
        f0 = rng.beta(1.5, 3.0)

        # Feature 1: distance_to_settlement_norm  [0, 1]  (higher = farther = safer)
        f1 = rng.beta(2.0, 2.0)

        # Feature 2: time_of_day_risk  {0.5=day, 0.9=dawn/dusk/night}
        f2 = rng.choice([0.5, 0.9], p=[0.45, 0.55])

        # Feature 3: seasonal_pattern  [0, 1]  (summer drought → higher = riskier)
        f3 = rng.beta(2.0, 2.5)

        # Feature 4: historical_conflict_freq  [0, 1]
        f4 = rng.beta(1.5, 4.0)

        # Feature 5: livestock_density_norm  [0, 1]
        f5 = rng.beta(2.0, 3.0)

        # Feature 6: environment_factor  [0, 1]
        f6 = rng.beta(2.0, 2.0)

        # Heuristic label: weighted composite mirroring the risk formula
        composite = (
            0.30 * (1.0 - f1)     # proximity (inverse distance)
            + 0.20 * f0            # recent movement
            + 0.15 * f2            # time of day
            + 0.15 * f5            # livestock density
            + 0.10 * f4            # historical frequency
            + 0.10 * f6            # environment
        )

        if composite >= 0.65:
            label = "HIGH"
        elif composite >= 0.38:
            label = "MEDIUM"
        else:
            label = "LOW"

        X_list.append([f0, f1, f2, f3, f4, f5, f6])
        y_list.append(label)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list)
    return X, y


# ---------------------------------------------------------------------------
# Model class
# ---------------------------------------------------------------------------

class MovementPredictor:
    """
    RandomForest-based wildlife movement risk zone predictor.
    Trained on synthetic Gir Forest scenario data (DEMO ONLY).
    """

    def __init__(self):
        self._le = LabelEncoder().fit(RISK_CLASSES)
        self._model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            min_samples_leaf=3,
            random_state=42,
            class_weight="balanced",
        )
        self._trained = False
        self._feature_importances: dict[str, float] = {}
        self._train()

    def _train(self) -> None:
        """Train the model on synthetic data at initialisation time."""
        X, y = _generate_synthetic_training_data(n_samples=200, seed=42)
        y_enc = self._le.transform(y)
        self._model.fit(X, y_enc)
        self._trained = True

        # Store normalised feature importances
        importances = self._model.feature_importances_
        total = importances.sum()
        self._feature_importances = {
            name: round(float(imp / total), 4)
            for name, imp in zip(FEATURE_NAMES, importances)
        }

    def _build_feature_vector(
        self,
        recency_weighted_sighting_freq: float,
        distance_to_settlement_km: float,
        observation_time: Optional[datetime],
        seasonal_factor: float,
        historical_conflict_freq_norm: float,
        livestock_density_norm: float,
        environment_factor: float,
    ) -> np.ndarray:
        """Construct the 7-dimensional feature vector from raw inputs."""

        # Normalise distance: 0 km → 1.0 (closest), 10 km → 0.0 (far)
        distance_norm = max(0.0, 1.0 - distance_to_settlement_km / 10.0)

        # Time-of-day risk (IST = UTC+5:30)
        if observation_time is None:
            observation_time = datetime.now(timezone.utc)
        local_hour = (observation_time.hour + 5.5) % 24
        if 7 <= local_hour < 17:
            tod_risk = 0.5   # day
        else:
            tod_risk = 0.9   # dawn / dusk / night

        features = np.array([
            min(max(recency_weighted_sighting_freq, 0.0), 1.0),
            min(max(distance_norm, 0.0), 1.0),
            tod_risk,
            min(max(seasonal_factor, 0.0), 1.0),
            min(max(historical_conflict_freq_norm, 0.0), 1.0),
            min(max(livestock_density_norm, 0.0), 1.0),
            min(max(environment_factor, 0.0), 1.0),
        ], dtype=np.float32)
        return features

    def predict(
        self,
        recency_weighted_sighting_freq: float,
        distance_to_settlement_km: float,
        observation_time: Optional[datetime] = None,
        seasonal_factor: float = 0.5,
        historical_conflict_freq_norm: float = 0.2,
        livestock_density_norm: float = 0.4,
        environment_factor: float = 0.5,
    ) -> dict:
        """
        Predict the wildlife movement risk zone.

        Returns:
            predicted_risk_zone     – "HIGH" | "MEDIUM" | "LOW"
            movement_probability    – probability of the predicted class
            class_probabilities     – {LOW, MEDIUM, HIGH} probabilities
            confidence_score        – adjusted model confidence
            feature_importance      – dict of feature name → importance
            input_features          – echo of normalised input features
            disclaimer              – mandatory demo disclaimer
        """
        assert self._trained, "Model is not trained"

        fv = self._build_feature_vector(
            recency_weighted_sighting_freq=recency_weighted_sighting_freq,
            distance_to_settlement_km=distance_to_settlement_km,
            observation_time=observation_time,
            seasonal_factor=seasonal_factor,
            historical_conflict_freq_norm=historical_conflict_freq_norm,
            livestock_density_norm=livestock_density_norm,
            environment_factor=environment_factor,
        )

        proba = self._model.predict_proba(fv.reshape(1, -1))[0]
        # Map probabilities to class labels
        class_proba = {
            cls: round(float(p), 4)
            for cls, p in zip(self._le.classes_, proba)
        }

        # Predicted class label
        predicted_idx = int(np.argmax(proba))
        predicted_label = self._le.inverse_transform([predicted_idx])[0]
        movement_probability = round(float(proba[predicted_idx]), 4)

        # Confidence: scale raw probability by a demo factor (since training is synthetic)
        confidence_score = round(min(movement_probability * 0.92, 0.95), 4)

        return {
            "predicted_risk_zone": predicted_label,
            "movement_probability": movement_probability,
            "class_probabilities": class_proba,
            "confidence_score": confidence_score,
            "feature_importance": self._feature_importances,
            "input_features": {
                name: round(float(val), 4)
                for name, val in zip(FEATURE_NAMES, fv)
            },
            "disclaimer": DISCLAIMER,
            "is_demo": True,
        }


# ---------------------------------------------------------------------------
# Module-level singleton (instantiated once on import)
# ---------------------------------------------------------------------------
_predictor_instance: Optional[MovementPredictor] = None


def get_predictor() -> MovementPredictor:
    """Return the module-level singleton predictor, training it if needed."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = MovementPredictor()
    return _predictor_instance
