"""All API endpoints for the ASD Prediction Platform."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.core.model_loader import AQ10_ITEMS, get_registry
from app.schemas.prediction import (
    ASDInput,
    HealthResponse,
    MetadataResponse,
    MetricsResponse,
    ModelInfo,
    ModelsResponse,
    MultiModelPredictionResponse,
    PredictionResponse,
)
from app.services.predictor import run_all_predictions, run_single_prediction
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _safe_error_detail(exc: Exception, generic: str) -> str:
    """Full exception detail is always logged server-side. It's only put in
    the HTTP response body when DEBUG is on, so a production deployment
    never leaks stack traces, file paths, or internal exception text to API
    clients — the previous version always returned f"...: {exc}" verbatim."""
    return f"{generic}: {exc}" if get_settings().DEBUG else generic


@router.get("/", tags=["General"])
def root():
    return {
        "message": "ASD Prediction Platform API",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health", response_model=HealthResponse, tags=["General"])
def health():
    registry = get_registry()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        models_loaded=len(registry.available_keys()),
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/models", response_model=ModelsResponse, tags=["Models"])
def list_models():
    registry = get_registry()
    infos = [
        ModelInfo(
            key=key,
            display_name=registry.display_name(key),
            is_default=(key == registry.default_model_key),
            metrics=registry.metrics_for(key),
        )
        for key in registry.available_keys()
    ]
    return ModelsResponse(models=infos, default_model=registry.default_model_key)


@router.get("/metadata", response_model=MetadataResponse, tags=["Models"])
def get_metadata():
    registry = get_registry()
    meta = registry.metadata
    if not meta:
        raise HTTPException(status_code=404, detail="Metadata not available")
    return MetadataResponse(
        feature_columns=meta.get("features", []),
        numeric_features=meta.get("numerical_features", []),
        categorical_features=meta.get("categorical_features", []),
        aq10_items=AQ10_ITEMS,
        target="Class/ASD",
        dataset_size=registry.dataset_size,
        train_size=registry.train_size,
        test_size=registry.test_size,
        generated_at=meta.get("generated_at", "unknown"),
        default_model=registry.default_model_key,
    )


@router.get("/metrics", response_model=MetricsResponse, tags=["Models"])
def get_metrics():
    registry = get_registry()
    models = {
        key: {
            "display_name": registry.display_name(key),
            "is_default": key == registry.default_model_key,
            "metrics": registry.metrics_for(key),
        }
        for key in registry.available_keys()
    }
    return MetricsResponse(models=models)


@router.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(
    payload: ASDInput,
    model: str = Query("default", description="Model key, or 'default'"),
):
    registry = get_registry()
    try:
        result = run_single_prediction(registry, payload, model)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500, detail=_safe_error_detail(exc, "Prediction failed")
        ) from exc

    aq_total = sum(getattr(payload, f"A{i}_Score") for i in range(1, 11))
    return PredictionResponse(result=result, aq10_total_score=aq_total)


@router.post(
    "/predict/all", response_model=MultiModelPredictionResponse, tags=["Prediction"]
)
def predict_all(payload: ASDInput):
    registry = get_registry()
    try:
        results = run_all_predictions(registry, payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Multi-model prediction failed")
        raise HTTPException(
            status_code=500, detail=_safe_error_detail(exc, "Prediction failed")
        ) from exc

    if not results:
        raise HTTPException(status_code=500, detail="No models available for prediction")

    votes = Counter(r.predicted_class for r in results)
    consensus_class, consensus_count = votes.most_common(1)[0]
    agreement_ratio = round(consensus_count / len(results), 4)

    best_key = max(results, key=lambda r: r.confidence).model_key
    aq_total = sum(getattr(payload, f"A{i}_Score") for i in range(1, 11))

    return MultiModelPredictionResponse(
        results=results,
        best_model_key=best_key,
        aq10_total_score=aq_total,
        consensus_class=consensus_class,
        agreement_ratio=agreement_ratio,
    )
