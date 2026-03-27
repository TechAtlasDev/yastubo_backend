from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.database import get_db, engine
from app.core.redis import redis_client, check_redis_connection
from app.core.logging import setup_logging
from app.shared.exceptions import validation_exception_handler, global_exception_handler
from fastapi.exceptions import RequestValidationError

from app.modules.auth.router import router as auth_router
from app.modules.plans.router import router as plans_router
from app.modules.emission.router import router as emission_router
from app.modules.payments.router import router as payments_router
from app.modules.audit.router import router as audit_router
from app.modules.portal.router import router as portal_router
from app.modules.leads.router import router as leads_router
from app.modules.ai.router import router as ai_router
from app.modules.voice.router import router as voice_router
from app.modules.dashboard.router import router as dashboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    
    # Verify DB connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        
    # Verify Redis connection
    if await check_redis_connection():
        logger.info("Redis connection established")
    else:
        logger.error("Redis connection failed")
        
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await redis_client.close()
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# API Router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(plans_router)
api_v1_router.include_router(emission_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(portal_router)
api_v1_router.include_router(leads_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(voice_router)
api_v1_router.include_router(dashboard_router)

@api_v1_router.get("/health", tags=["Infrastructure"])
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
        
    redis_status = "ok" if await check_redis_connection() else "error"
    
    return {
        "status": "ok",
        "db": db_status,
        "redis": redis_status,
        "env": settings.APP_ENV,
        "version": "0.2.0"
    }

app.include_router(api_v1_router)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}
