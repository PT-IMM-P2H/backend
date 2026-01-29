from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
import time
import subprocess

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database import engine
from app.utils.response import base_response

# Alembic Imports
from alembic.config import Config
from alembic import command
from sqlalchemy import inspect

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# PORT (Railway injects PORT)
# =========================================================
PORT = int(os.getenv("PORT", 8000))

# =========================================================
# DATABASE READINESS CHECK
# =========================================================
def wait_for_database(max_retries: int = 10, delay: int = 2) -> bool:
    """
    Tunggu database Railway siap sebelum migration
    """
    logger.info("⏳ Waiting for database to be ready...")
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database is ready")
            return True
        except OperationalError:
            logger.warning(
                f"Database not ready (attempt {attempt}/{max_retries})"
            )
            time.sleep(delay)

    logger.error("❌ Database not ready after retries")
    return False

# =========================================================
# SAFE ALEMBIC AUTO MIGRATION
# =========================================================
def run_alembic_migration():
    """
    Jalankan alembic upgrade head secara aman.
    Tidak akan mematikan app jika gagal.
    """
    if not wait_for_database():
        logger.error("Skipping Alembic migration (DB not ready)")
        return

    try:
        # Create Alembic configuration object
        alembic_cfg = Config("alembic.ini")
        
        # Check if database needs stamping (Tables exist but no alembic_version)
        with engine.connect() as connection:
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            
            has_alembic = "alembic_version" in tables
            has_tables = "users" in tables or "checklist_templates" in tables
            
            if has_tables and not has_alembic:
                logger.warning("⚠️  Database has tables but no alembic_version! Stamping head...")
                command.stamp(alembic_cfg, "head")
                logger.info("✅ Database stamped to head")
        
        logger.info("🧬 Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Alembic migration completed")

    except Exception as e:
        logger.error("❌ Alembic migration failed")
        logger.error(str(e))
        # ❗ JANGAN raise → app tetap jalan

# =========================================================
# FASTAPI LIFESPAN
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------------- STARTUP ----------------
    logger.info("🚀 Starting P2H System API...")

    print("\n" + "=" * 60)
    print("                P2H SYSTEM PT. IMM BONTANG")
    print("=" * 60)
    print(f"🚀 Main API      : http://0.0.0.0:{PORT}")
    print(f"📝 Swagger UI    : /docs")
    print(f"🌍 Environment   : {settings.ENVIRONMENT}")
    print(f"🔧 Railway Mode  : {'Yes' if os.getenv('RAILWAY_ENVIRONMENT_NAME') else 'No (Local)'}")
    print("=" * 60 + "\n")

    # ✅ AUTO MIGRATE - Now handled internally
    # Migration runs BEFORE app starts
    run_alembic_migration()

    # Scheduler
    try:
        from app.scheduler.scheduler import start_scheduler
        start_scheduler()
        logger.info("✅ Scheduler started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")

    yield

    # ---------------- SHUTDOWN ----------------
    logger.info("🛑 Shutting down P2H System API...")

# =========================================================
# FASTAPI APP
# =========================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## P2H (Pelaksanaan Pemeriksaan Harian)
    Vehicle Inspection System API
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# =========================================================
# CORS
# =========================================================
# Environment-aware CORS: wildcard in dev, specific origins in production
try:
    if settings.ENVIRONMENT == "development":
        allow_origins = ["*"]  # Allow all origins in development
        allow_origin_regex = None
        logger.info("🔓 CORS: Development mode - allowing all origins")
    else:
        # In production, use configured origins with wildcard support
        logger.info(f"🔍 CORS: Raw CORS_ORIGINS value: {settings.CORS_ORIGINS}")
        origins_list = settings.cors_origins_list
        logger.info(f"🔍 CORS: Parsed origins list: {origins_list}")
        
        # Check if any origin contains wildcard
        has_wildcard = any("*" in origin for origin in origins_list)
        
        if has_wildcard:
            # Convert wildcard patterns to regex
            import re
            patterns = []
            for origin in origins_list:
                if "*" in origin:
                    # Convert wildcard to regex pattern
                    pattern = origin.replace(".", r"\.").replace("*", ".*")
                    patterns.append(pattern)
                else:
                    # Escape exact origins for regex
                    patterns.append(re.escape(origin))
            
            # Combine all patterns
            allow_origin_regex = "|".join(f"({p})" for p in patterns)
            allow_origins = []  # Empty list when using regex
            logger.info(f"🔒 CORS: Production mode with wildcard - pattern: {allow_origin_regex}")
        else:
            # No wildcard, use simple list
            allow_origins = origins_list
            allow_origin_regex = None
            logger.info(f"🔒 CORS: Production mode - allowing origins: {allow_origins}")

except Exception as e:
    # Fallback to safe defaults if CORS configuration fails
    logger.error(f"❌ CORS configuration error: {str(e)}")
    logger.warning("⚠️ Falling back to allow all origins due to config error")
    allow_origins = ["*"]
    allow_origin_regex = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =========================================================
# EXCEPTION HANDLERS
# =========================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field = errors[0]["loc"][-1] if errors and errors[0].get("loc") else "Unknown"
    msg = f"Kesalahan pada field {field}: {errors[0]['msg']}"

    return base_response(
        message=msg,
        payload={"details": errors},
        status_code=422
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", str(exc.detail))

    return base_response(
        message=message,
        payload=None,
        status_code=exc.status_code
    )

@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: Exception):
    return base_response(
        message="Resource atau data yang Anda cari tidak ditemukan",
        payload=None,
        status_code=404
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled internal error: {str(exc)}")
    return base_response(
        message="Terjadi kesalahan pada sistem, silahkan hubungi administrator",
        payload={"error": str(exc)} if settings.ENVIRONMENT == "development" else None,
        status_code=500
    )

# =========================================================
# ROOT
# =========================================================
@app.get("/", tags=["Root"])
async def root():
    return base_response(
        message=f"Welcome to {settings.APP_NAME} API",
        payload={
            "version": settings.APP_VERSION,
            "docs": "/docs"
        }
    )

# =========================================================
# ROUTERS
# =========================================================
from app.routers import (
    auth,
    users,
    vehicles,
    p2h,
    master_data,
    dashboard,
    vehicle_type,
    bulk_upload,
    admin,
)

from app.routers.export import router as export_router
from app.routers.health import router as health_router

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(vehicle_type.router)
app.include_router(p2h.router, prefix="/p2h", tags=["P2H Inspection"])
app.include_router(master_data.router, prefix="/master-data", tags=["Master Data"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(bulk_upload.router)
app.include_router(export_router)
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(admin.router)  # Admin endpoints for seeding

# =========================================================
# LOCAL RUN
# =========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )
