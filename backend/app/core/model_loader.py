"""Loads and caches all ASD models plus shared metadata at startup.

IMPORTANT: the shape of `asd_model_metadata.joblib` is whatever
`End_To_End.ipynb` actually saves (see its final cells):

    {
        "best_model_name": "Logistic Regression",
        "saved_model_paths": {"Logistic Regression": "asd_model_logistic_regression.joblib", ...},
        "features": [...],
        "categorical_features": [...],
        "numerical_features": [...],
        "all_model_test_metrics": {
            "Logistic Regression": {"test_accuracy": ..., "test_precision": ..., ...},
            ...
        },
    }

There is no "models" or "default_model" key — earlier versions of this
loader assumed a schema that the notebook never produced, which meant
`/models`, `/metadata`, and `/metrics` silently returned empty data. This
version reads the real keys and normalizes them into the shape the API
schemas (and the frontend) expect.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, Optional

import joblib

from app.config import Settings
from app.core.smote import SmotePipeline, smote_resample
from app.utils.logger import get_logger

logger = get_logger(__name__)

# The trained model artifacts were serialized from the notebook where
# `SmotePipeline` and `smote_resample` lived in `__main__`. Make those names
# available there before unpickling so joblib can resolve them.
sys.modules["__main__"].SmotePipeline = SmotePipeline
sys.modules["__main__"].smote_resample = smote_resample

MODEL_FILES = {
    "logistic_regression": "asd_model_logistic_regression.joblib",
    "random_forest": "asd_model_random_forest.joblib",
    "svm_rbf": "asd_model_svm_rbf.joblib",
    "decision_tree": "asd_model_decision_tree.joblib",
}

DISPLAY_NAMES = {
    "logistic_regression": "Logistic Regression",
    "random_forest": "Random Forest",
    "svm_rbf": "SVM (RBF)",
    "decision_tree": "Decision Tree",
}
# NOTE: the two dicts above are now only a FALLBACK for metadata that
# predates `saved_model_paths` (or is missing entirely). The normal path is
# ModelRegistry.load_all() reading the real, current model list out of
# asd_model_metadata.joblib every startup — see the comment there.

# The AQ-10 items aren't stored in the model metadata (the notebook only
# records feature/column names), so the canonical question text lives here.
AQ10_ITEMS = [
    "I often notice small sounds when others do not.",
    "I usually concentrate more on the whole picture, rather than the small details.",
    "I find it easy to do more than one thing at once.",
    "If there is an interruption, I can switch back to what I was doing very quickly.",
    "I find it easy to 'read between the lines' when someone is talking to me.",
    "I know how to tell if someone listening to me is getting bored.",
    "When I'm reading a story, I find it difficult to work out the characters' intentions.",
    "I like to collect information about categories of things (e.g. types of car, bird, train).",
    "I find it easy to work out what someone is thinking or feeling just by looking at their face.",
    "I find it difficult to work out people's intentions.",
]


def _slugify(name: str) -> str:
    """Matches the notebook's own slugify() used when saving model files."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


# Maps the notebook's metric field names -> the flat names the API/frontend use.
_METRIC_KEY_MAP = {
    "test_accuracy": "accuracy",
    "test_precision": "precision",
    "test_recall": "recall",
    "test_f1": "f1_score",
    "cv_f1": "cv_f1",
}


class ModelRegistry:
    """Holds every loaded model pipeline plus metadata, ready for inference."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.models: Dict[str, object] = {}
        self.metadata: dict = {}
        self.default_model_key: str = "logistic_regression"
        # key (e.g. "logistic_regression") -> display name (e.g. "Logistic Regression")
        self._display_by_key: Dict[str, str] = dict(DISPLAY_NAMES)
        # key -> normalized metrics dict (accuracy/precision/recall/f1_score/cv_f1)
        self._metrics_by_key: Dict[str, dict] = {}
        self.dataset_size: int = 0
        self.train_size: int = 0
        self.test_size: int = 0

    def load_all(self) -> None:
        models_dir = self.settings.models_path
        logger.info("Loading models from %s", models_dir)

        # Load metadata FIRST: it's the source of truth for which models
        # actually exist (`saved_model_paths`, written by End_To_End.ipynb
        # every time it's re-run). Deriving the model list from here means
        # adding, removing, or retraining models in the notebook is picked
        # up automatically on the next backend restart — previously this
        # loop only ever looked for the same 4 hardcoded filenames, so a
        # changed model lineup in the notebook never reached the GUI.
        meta_path = models_dir / self.settings.METADATA_FILE
        if meta_path.exists():
            self.metadata = joblib.load(meta_path)
        else:
            logger.warning("Metadata file not found at %s", meta_path)

        saved_paths = self.metadata.get("saved_model_paths", {}) if self.metadata else {}
        dynamic_targets: Dict[str, str] = {}
        for display_name, saved_path in saved_paths.items():
            if display_name.startswith("Best ("):
                continue
            # saved_path may be an absolute/relative path from the notebook's
            # own machine — only the filename is portable, so resolve it
            # fresh against this machine's models_dir.
            filename = Path(saved_path).name
            dynamic_targets[_slugify(display_name)] = filename

        # Fallback for a first run / older metadata that predates
        # saved_model_paths — keeps existing setups working unchanged.
        load_targets = dynamic_targets or dict(MODEL_FILES)

        for key, filename in load_targets.items():
            path = models_dir / filename
            if path.exists():
                try:
                    self.models[key] = joblib.load(path)
                    logger.info("Loaded model '%s' from %s", key, filename)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Failed loading model '%s': %s", key, exc)
            else:
                logger.warning("Model file not found, skipping: %s", path)

        if self.metadata:
            self._normalize_metadata()
            logger.info("Loaded metadata. Default model: %s", self.default_model_key)

        # Ensure the "best" model is also reachable under its own key even if
        # the default key above points at one of the named pipelines.
        best_path = models_dir / self.settings.DEFAULT_MODEL_FILE
        if best_path.exists():
            try:
                self.models.setdefault("best", joblib.load(best_path))
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed loading best model: %s", exc)

        if not self.models:
            raise RuntimeError(
                f"No ASD models could be loaded from {models_dir}. "
                "Run End_To_End.ipynb (or scripts/) to generate them."
            )

    def _normalize_metadata(self) -> None:
        """Turns the notebook's raw metadata dict into lookups keyed by our
        slug keys (logistic_regression, random_forest, svm_rbf, decision_tree)."""
        meta = self.metadata

        # Build display-name lookup from whichever saved_model_paths keys are
        # real model names (skip the "Best (...)" convenience entry).
        saved_paths = meta.get("saved_model_paths", {})
        for display_name in saved_paths:
            if display_name.startswith("Best ("):
                continue
            key = _slugify(display_name)
            self._display_by_key[key] = display_name

        # Normalize per-model test metrics, keyed by our slug.
        raw_metrics = meta.get("all_model_test_metrics", {})
        for display_name, m in raw_metrics.items():
            key = _slugify(display_name)
            normalized = {
                _METRIC_KEY_MAP.get(k, k): v
                for k, v in m.items()
                if k in _METRIC_KEY_MAP
            }
            self._metrics_by_key[key] = normalized

        # Default model: notebook stores "best_model_name" (a display name),
        # not a "default_model" slug.
        best_name = meta.get("best_model_name")
        if best_name:
            self.default_model_key = _slugify(best_name)

        # Dataset size isn't recorded in the metadata file either — the
        # notebook prints it but never saves it. These are the true values
        # from the notebook's own run (1880 rows after cleaning, 80/20
        # stratified split -> 1504 train / 376 test) and are used as a
        # sensible fallback if nothing better is available.
        self.dataset_size = meta.get("dataset_size", 1880)
        self.train_size = meta.get("train_size", 1504)
        self.test_size = meta.get("test_size", 376)

    def get(self, key: str):
        if key == "default":
            key = self.default_model_key
        model = self.models.get(key)
        if model is None:
            raise KeyError(f"Model '{key}' is not loaded/available")
        return model

    def display_name(self, key: str) -> str:
        if key == "default":
            key = self.default_model_key
        return self._display_by_key.get(key, DISPLAY_NAMES.get(key, key))

    def metrics_for(self, key: str) -> dict:
        if key == "default":
            key = self.default_model_key
        return self._metrics_by_key.get(key, {})

    def available_keys(self):
        return [k for k in self.models.keys() if k != "best"]


_registry: Optional[ModelRegistry] = None


def init_registry(settings: Settings) -> ModelRegistry:
    global _registry
    _registry = ModelRegistry(settings)
    _registry.load_all()
    return _registry


def get_registry() -> ModelRegistry:
    if _registry is None:
        raise RuntimeError("Model registry has not been initialized yet")
    return _registry
