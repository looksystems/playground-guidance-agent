"""FastAPI application initialization.

Main application with:
- CORS configuration
- Router registration
- Middleware setup
- Health check endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import os

from guidance_agent.api.routers import consultations, customers, admin
from guidance_agent.api import schemas
from guidance_agent.core.database import get_session

# Initialize Phoenix tracing before any LLM calls
from guidance_agent.core import llm_config  # noqa: F401

# Create FastAPI application
app = FastAPI(
    title="Pension Guidance Chat API",
    description="API for FCA-compliant pension guidance consultations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vue dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative Vue port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(consultations.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# Health check endpoint
@app.get("/health", response_model=schemas.HealthCheckResponse)
async def health_check():
    """Health check endpoint.

    Returns:
        Health status of the application
    """
    # Check database connection
    db_healthy = True
    try:
        session = get_session()
        session.execute("SELECT 1")
        session.close()
    except Exception:
        db_healthy = False

    # Check LLM connection (simplified - just check env vars)
    llm_healthy = True
    try:
        llm_healthy = bool(os.getenv("LITELLM_MODEL_ADVISOR"))
    except Exception:
        llm_healthy = False

    # Determine overall status
    if db_healthy and llm_healthy:
        status = "healthy"
    elif db_healthy or llm_healthy:
        status = "degraded"
    else:
        status = "unhealthy"

    return schemas.HealthCheckResponse(
        status=status,
        database=db_healthy,
        llm=llm_healthy,
        timestamp=datetime.now(timezone.utc),
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information.

    Returns:
        API welcome message
    """
    return {
        "message": "Pension Guidance Chat API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
