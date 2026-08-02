from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central app configuration. Values are read from environment variables
    or a `.env` file in the `backend/` directory (see .env.example).
    """

    APP_NAME: str = "ASD Prediction Platform API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Comma-separated origins allowed to call the API (the Next.js frontend).
    # Add the deployed Vercel URL(s) here in production, e.g. via the
    # ALLOWED_ORIGINS env var: "https://your-app.vercel.app,http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Trained model artifact filenames — all resolved inside `models_path`.
    # Must match app/core/model_loader.py's MODEL_FILES dict and the actual
    # filenames in the project's top-level models/ folder.
    METADATA_FILE: str = "asd_model_metadata.joblib"
    DEFAULT_MODEL_FILE: str = "asd_best_model.joblib"

    # Optional override — if left blank, resolved relative to the project
    # root (two levels above backend/), i.e. ASD_Prediction/models/
    MODELS_DIR: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def models_path(self) -> Path:
        if self.MODELS_DIR:
            return Path(self.MODELS_DIR).resolve()
        # app/config.py -> app/ -> backend/ -> ASD_Prediction/ -> models/
        project_root = Path(__file__).resolve().parent.parent.parent
        return project_root / "models"

    def validate(self) -> None:
        """Fail fast with a clear message if the models directory is
        missing entirely, instead of letting each individual joblib.load()
        fail one at a time deep inside ModelRegistry.load_all()."""
        path = self.models_path
        if not path.exists():
            raise RuntimeError(
                f"Models directory not found at {path}. Run End_To_End.ipynb "
                "first to train and save the model artifacts, or set "
                "MODELS_DIR in backend/.env to point at the right folder."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
