from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.methods import router as methods_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.exports import router as exports_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MVP engineering scaffold for the research-method-platform API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(methods_router)
app.include_router(uploads_router)
app.include_router(tasks_router)
app.include_router(exports_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "ready",
    }
