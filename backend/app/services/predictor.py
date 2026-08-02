"""Core prediction logic shared by all API endpoints."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import List

import pandas as pd

from app.core.model_loader import ModelRegistry
from app.schemas.prediction import ASDInput, PredictionResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _recommendation(predicted_class: str, risk_pct: float) -> str:
    if predicted_class == "YES" and risk_pct >= 75:
        return (
            "The screening result indicates a strong likelihood of "
            "autistic traits. We strongly recommend a comprehensive "
            "evaluation by a licensed clinical psychologist or "
            "developmental pediatrician."
        )
    if predicted_class == "YES":
        return (
            "The screening result indicates some likelihood of autistic "
            "traits. Consider following up with a qualified healthcare "
            "professional for a formal assessment."
        )
    if risk_pct >= 35:
        return (
            "The screening result leans negative, but a moderate number "
            "of traits were flagged. If you have ongoing concerns, a "
            "professional evaluation can provide clarity."
        )
    return (
        "The screening result does not indicate significant autistic "
        "traits at this time. This tool is not a diagnosis — consult a "
        "professional if you have concerns."
    )


def run_single_prediction(
    registry: ModelRegistry, payload: ASDInput, model_key: str = "default"
) -> PredictionResult:
    start = time.perf_counter()

    pipeline = registry.get(model_key)
    resolved_key = registry.default_model_key if model_key == "default" else model_key

    features = pd.DataFrame([payload.to_feature_dict()])

    proba = pipeline.predict_proba(features)[0]
    # class order is [0, 1] == [NO, YES] since target was encoded that way
    p_no, p_yes = float(proba[0]), float(proba[1])
    predicted_class = "YES" if p_yes >= p_no else "NO"
    confidence = max(p_yes, p_no)
    risk_pct = round(p_yes * 100, 2)
    accuracy = registry.metrics_for(resolved_key).get("accuracy")

    elapsed_ms = (time.perf_counter() - start) * 1000

    return PredictionResult(
        model_key=resolved_key,
        model_name=registry.display_name(resolved_key),
        predicted_class=predicted_class,
        confidence=round(confidence, 4),
        probability_asd=round(p_yes, 4),
        probability_no_asd=round(p_no, 4),
        accuracy=accuracy,
        risk_percentage=risk_pct,
        recommendation=_recommendation(predicted_class, risk_pct),
        processing_time_ms=round(elapsed_ms, 3),
        model_version=registry.metadata.get("generated_at", "unknown"),
        predicted_at=datetime.now(timezone.utc),
    )


def run_all_predictions(
    registry: ModelRegistry, payload: ASDInput
) -> List[PredictionResult]:
    results = []
    for key in registry.available_keys():
        try:
            results.append(run_single_prediction(registry, payload, key))
        except Exception as exc:  # noqa: BLE001
            logger.error("Prediction failed for model '%s': %s", key, exc)
    return results
