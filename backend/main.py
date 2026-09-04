from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.recovery import router as recovery_router


app = FastAPI(
    title="Vaidya API",
    description="AI-powered revenue recovery agent",
    version="0.1.0",
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    health_router
)

app.include_router(
    recovery_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Vaidya API is running",
        "service": "AI-powered revenue recovery agent",
        "version": "0.1.0",
    }