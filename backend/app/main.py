from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.shared.response import build_success_response, build_failure_response, build_validation_error_response
from backend.app.shared.logger import logger
from backend.app.shared.exceptions import AgentFleetException

# Import API Routers
from backend.app.api.health import router as health_router

# Import Agent Routers
from backend.app.agents.dispatch import router as dispatch_router
from backend.app.agents.route import router as route_router
from backend.app.agents.maintenance import router as maintenance_router
from backend.app.agents.analytics import router as analytics_router
from backend.app.agents.customer import router as customer_router
from backend.app.agents.supervisor import router as supervisor_router
from backend.app.agents.cargo_validation import router as cargo_validation_router
from backend.app.agents.traffic import router as traffic_router
from backend.app.agents.weather import router as weather_router
from backend.app.agents.eta_updater import router as eta_updater_router
from backend.app.agents.compliance import router as compliance_router
from backend.app.agents.fuel import router as fuel_router
from backend.app.agents.driver_rating import router as driver_rating_router
from backend.app.agents.invoice import router as invoice_router
from backend.app.agents.fleet_summary import router as fleet_summary_router
from backend.app.agents.sos_alert import router as sos_alert_router

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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(AgentFleetException)
async def agentfleet_exception_handler(request, exc: AgentFleetException):
    """
    Catches custom application errors (e.g. VehicleUnavailableException, DriverUnavailableException).
    Formats and returns standardized failure payload.
    """
    logger.warning(f"Application error intercepted: {exc.message}")
    return build_failure_response(
        message=exc.message,
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Catches Pydantic schema validation failures.
    Translates loc tuples and error descriptors into a clean validation error list.
    """
    errors = exc.errors()
    parsed_errors = []
    for err in errors:
        loc = err.get("loc", [])
        field = loc[-1] if loc else "request"
        msg = err.get("msg", "Invalid parameter value.")
        parsed_errors.append({"field": str(field), "issue": msg})
    
    logger.warning(f"Request validation failed: {parsed_errors}")
    return build_validation_error_response(
        message="Request parameters failed schemas validation.",
        errors=parsed_errors
    )

# ============================================================================
# Routers Registration
# ============================================================================

# Register System Health Router
app.include_router(health_router, prefix="/health")

# Register Dispatch Agent Router at root level to support POST /dispatch
app.include_router(dispatch_router)

# Register Route Agent Router at root level to support POST /route
app.include_router(route_router)

# Register Maintenance Agent Router at root level to support POST /maintenance
app.include_router(maintenance_router)

# Register Analytics Agent Router at root level to support POST /analytics/report
app.include_router(analytics_router)

# Register Customer Agent Router at root level to support POST /customer/notify
app.include_router(customer_router)

# Register Supervisor Agent Router at root level to support POST /supervisor/execute
app.include_router(supervisor_router)

# Register New 10 Agent Routers at root level
app.include_router(cargo_validation_router)
app.include_router(traffic_router)
app.include_router(weather_router)
app.include_router(eta_updater_router)
app.include_router(compliance_router)
app.include_router(fuel_router)
app.include_router(driver_rating_router)
app.include_router(invoice_router)
app.include_router(fleet_summary_router)
app.include_router(sos_alert_router)

# Register versioned Agent Routers
app.include_router(dispatch_router, prefix="/api/v1/dispatch", tags=["Dispatch & Allocation"])
app.include_router(route_router, prefix="/api/v1/route", tags=["Route Intelligence"])
app.include_router(maintenance_router, prefix="/api/v1/maintenance", tags=["Vehicle Health & Maintenance"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Fleet Analytics & Optimization"])
app.include_router(customer_router, prefix="/api/v1/customer", tags=["Customer Communication"])
app.include_router(supervisor_router, prefix="/api/v1/supervisor", tags=["Fleet Supervisor"])
app.include_router(cargo_validation_router, prefix="/api/v1/cargo_validation", tags=["Cargo Validation"])
app.include_router(traffic_router, prefix="/api/v1/traffic", tags=["Traffic"])
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(eta_updater_router, prefix="/api/v1/eta_updater", tags=["ETA Updater"])
app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["Compliance"])
app.include_router(fuel_router, prefix="/api/v1/fuel", tags=["Fuel"])
app.include_router(driver_rating_router, prefix="/api/v1/driver_rating", tags=["Driver Rating"])
app.include_router(invoice_router, prefix="/api/v1/invoice", tags=["Invoice"])
app.include_router(fleet_summary_router, prefix="/api/v1/fleet_summary", tags=["Fleet Summary"])
app.include_router(sos_alert_router, prefix="/api/v1/sos_alert", tags=["SOS Alert"])

@app.get("/health", tags=["System"])
async def health_check():
    """
    Standard health check endpoint to verify backend service status.
    """
    return build_success_response(
        data={"environment": settings.APP_ENV},
        message="System is online and running."
    )
