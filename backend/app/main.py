from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.shared.response import success_response
from backend.app.shared.logger import logger

# Import API Routers
from backend.app.api.health import router as health_router

# Import Agent Routers
from backend.app.agents.dispatch import router as dispatch_router
from backend.app.agents.route import router as route_router
from backend.app.agents.maintenance import router as maintenance_router
from backend.app.agents.analytics import router as analytics_router
from backend.app.agents.customer import router as customer_router
from backend.app.agents.supervisor import router as supervisor_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(f"Starting {settings.APP_NAME} in environment: {settings.APP_ENV}")
    yield
    # Shutdown actions
    logger.info(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI-Based Intelligent Fleet Management System Backend Gateway",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware to support React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in staging/production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register System Health Router
app.include_router(health_router, prefix="/health")

# Register Agent Routers
app.include_router(dispatch_router, prefix="/api/v1/dispatch", tags=["Dispatch & Allocation"])
app.include_router(route_router, prefix="/api/v1/route", tags=["Route Intelligence"])
app.include_router(maintenance_router, prefix="/api/v1/maintenance", tags=["Vehicle Health & Maintenance"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Fleet Analytics & Optimization"])
app.include_router(customer_router, prefix="/api/v1/customer", tags=["Customer Communication"])
app.include_router(supervisor_router, prefix="/api/v1/supervisor", tags=["Fleet Supervisor"])

@app.get("/health", tags=["System"])
async def health_check():
    """
    Standard health check endpoint to verify backend service status.
    """
    return success_response(
        data={"status": "healthy", "environment": settings.APP_ENV},
        message="System is online and running."
    )
