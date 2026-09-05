from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.security import hash_password
from app.database.mongo import connect_to_mongo, close_mongo_connection, get_database
from app.database.indexes import create_indexes
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.jobs import router as jobs_router
from app.api.matches import router as matches_router
from app.api.saved import router as saved_router
from app.api.applications import router as applications_router
from app.api.skill_gaps import router as skill_gaps_router
from app.api.pipeline import router as pipeline_router
from app.api.admin import router as admin_router

async def seed_initial_admin_and_sources():
    """Ensure default admin account exists for first run."""
    db = get_database()
    if db is None:
        return
        
    admin_user = await db.users.find_one({"email": settings.ADMIN_EMAIL.lower()})
    now = datetime.now(timezone.utc)
    if not admin_user:
        logger.info(f"Seeding default admin user: {settings.ADMIN_EMAIL}...")
        await db.users.insert_one({
            "name": settings.ADMIN_NAME,
            "email": settings.ADMIN_EMAIL.lower(),
            "hashed_password": hash_password(settings.ADMIN_PASSWORD),
            "role": "admin",
            "created_at": now,
            "updated_at": now
        })

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing JobFusion AI backend...")
    try:
        await connect_to_mongo()
        await create_indexes()
        await seed_initial_admin_and_sources()
    except Exception as e:
        logger.error(f"Startup initialization encountered an error: {e}")
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Multi-Agent Career Intelligence & Job Personalization Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )

# Health endpoint
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV
    }

# Mount API routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(matches_router, prefix=settings.API_V1_PREFIX)
app.include_router(saved_router, prefix=settings.API_V1_PREFIX)
app.include_router(applications_router, prefix=settings.API_V1_PREFIX)
app.include_router(skill_gaps_router, prefix=settings.API_V1_PREFIX)
app.include_router(pipeline_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
