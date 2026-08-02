"""Pydantic request/response schemas for the prediction API."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

BinaryScore = Literal[0, 1]


class ASDInput(BaseModel):
    """A single AQ-10 screening submission."""

    A1_Score: BinaryScore
    A2_Score: BinaryScore
    A3_Score: BinaryScore
    A4_Score: BinaryScore
    A5_Score: BinaryScore
    A6_Score: BinaryScore
    A7_Score: BinaryScore
    A8_Score: BinaryScore
    A9_Score: BinaryScore
    A10_Score: BinaryScore

    age: float = Field(..., ge=1, le=120, description="Age in years")
    gender: Literal["m", "f"]
    ethnicity: str = Field(default="Others")
    jaundice: Literal["yes", "no"] = "no"
    austim: Literal["yes", "no"] = Field(
        "no", description="Family history of autism"
    )
    contry_of_res: str = Field(default="Others", alias="country_of_res")
    used_app_before: Literal["yes", "no"] = "no"
    relation: str = Field(default="Self")

    model_config = {"populate_by_name": True}

    @field_validator("ethnicity", "contry_of_res", "relation", mode="before")
    @classmethod
    def _default_blank(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return "Others"
        return v

    def to_feature_dict(self) -> Dict:
        """Builds the row the trained sklearn pipelines actually expect.

        The pipelines were fit (see End_To_End.ipynb) on a dataframe where:
        - the jaundice column is named "jundice" (the typo present across
          every source CSV, kept instead of "fixed" so it matches what the
          ColumnTransformer was fit on),
        - gender / jundice / austim / used_app_before were label-encoded to
          0/1 before fitting (gender: m=0, f=1; the rest: no=0, yes=1) --
          they are NOT string columns, so passing "yes"/"no"/"m"/"f" straight
          into predict_proba() would crash the ColumnTransformer's
          StandardScaler step,
        - the redundant "result" (sum of A1..A10) column was dropped before
          training, so it must not be included here.
        """
        yes_no = {"yes": 1, "no": 0}
        return {
            **{f"A{i}_Score": getattr(self, f"A{i}_Score") for i in range(1, 11)},
            "age": self.age,
            "gender": 1 if self.gender == "f" else 0,
            "ethnicity": self.ethnicity,
            "jundice": yes_no[self.jaundice],
            "austim": yes_no[self.austim],
            "contry_of_res": self.contry_of_res,
            "used_app_before": yes_no[self.used_app_before],
            "relation": self.relation,
        }


class PredictionResult(BaseModel):
    model_key: str
    model_name: str
    predicted_class: Literal["YES", "NO"]
    confidence: float = Field(..., ge=0, le=1)
    probability_asd: float = Field(..., ge=0, le=1)
    probability_no_asd: float = Field(..., ge=0, le=1)
    accuracy: Optional[float] = None
    risk_percentage: float
    recommendation: str
    processing_time_ms: float
    model_version: str
    predicted_at: datetime


class PredictionResponse(BaseModel):
    result: PredictionResult
    aq10_total_score: int


class MultiModelPredictionResponse(BaseModel):
    results: List[PredictionResult]
    best_model_key: str
    aq10_total_score: int
    consensus_class: Literal["YES", "NO"]
    agreement_ratio: float


class ModelInfo(BaseModel):
    key: str
    display_name: str
    is_default: bool
    metrics: Dict[str, float]


class ModelsResponse(BaseModel):
    models: List[ModelInfo]
    default_model: str


class MetadataResponse(BaseModel):
    feature_columns: List[str]
    numeric_features: List[str]
    categorical_features: List[str]
    aq10_items: List[str]
    target: str
    dataset_size: int
    train_size: int
    test_size: int
    generated_at: str
    default_model: str


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: int
    timestamp: datetime


class MetricsResponse(BaseModel):
    models: Dict[str, Dict]
