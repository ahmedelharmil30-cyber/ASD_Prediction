from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.core.model_loader import init_registry
from app.utils.logger import configure_logging, get_logger

settings = get_settings()
configure_logging(level=settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AQ-10 based ASD screening predictions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No prefix — the frontend's utils/api_client.py calls /health, /models,
# /metadata, /metrics, /predict, /predict/all directly against the root.
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info(
        "%s starting up (environment=%s)", settings.APP_NAME, settings.ENVIRONMENT
    )
    settings.validate()
    init_registry(settings)
