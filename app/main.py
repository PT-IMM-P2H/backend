from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import Base, engine
from app.utils.response import base_response  # Import wrapper response baru

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager untuk startup dan shutdown events.
    """
    # --- STARTUP ---
    logger.info("🚀 Starting P2H System API...")
    
    # Menampilkan Link Akses di Terminal agar mudah diklik
    print("\n" + "="*60)
    print("                P2H SYSTEM PT. IMM BONTANG")
    print("="*60)
    print(f"🚀 Main API      : http://127.0.0.1:8000")
    print(f"📝 Swagger UI    : http://127.0.0.1:8000/docs")
    print(f"📖 ReDoc Docs    : http://127.0.0.1:8000/redoc")
    print("="*60 + "\n")

    # Import scheduler
    try:
        from app.scheduler.scheduler import start_scheduler
        start_scheduler()
        logger.info("✅ Scheduler started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
    
    logger.info("✅ P2H System API started successfully")
    
    yield
    
    # --- SHUTDOWN ---
    logger.info("🛑 Shutting down P2H System API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## P2H (Pelaksanaan Pemeriksaan Harian) Vehicle Inspection System
    
    REST API dengan struktur response terstandarisasi untuk memudahkan integrasi Front-End.
    
    ### Fitur Utama:
    - 🔐 **Authentication**: JWT & Cookie-based (Superadmin, Admin, User)
    - 🚗 **Vehicle Management**: Data kendaraan & Expiry Alerts
    - 📋 **P2H Forms**: Standarisasi payload & validation mapping
    - 📱 **Notifications**: Integrasi Telegram Alert
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CUSTOM EXCEPTION HANDLERS (Standardized for FE) ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Menangani error validasi Pydantic (422) dengan format yang rapi untuk FE.
    """
    errors = exc.errors()
    # Mengambil pesan error pertama dan lokasi fieldnya agar FE bisa langsung menampilkan alert
    field = errors[0]['loc'][-1]
    msg = f"Kesalahan pada field {field}: {errors[0]['msg']}"
    
    return base_response(
        message=msg,
        payload={"details": errors},
        status_code=422
    )

@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: Exception):
    """
    Menangani error resource tidak ditemukan (404).
    """
    return base_response(
        message="Resource atau data yang Anda cari tidak ditemukan",
        status_code=404
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Menangani semua internal server error (500) agar tidak mengirim traceback mentah ke FE.
    """
    logger.error(f"Internal Error Unhandled: {str(exc)}")
    return base_response(
        message="Terjadi kesalahan pada sistem, silahkan hubungi administrator",
        payload={"error": str(exc)} if settings.ENVIRONMENT == "development" else None,
        status_code=500
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return base_response(
        message=f"Welcome to {settings.APP_NAME} API",
        payload={
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs"
        }
    )


# Import and register routers
from app.routers import auth, users, vehicles, p2h

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(p2h.router, prefix="/p2h", tags=["P2H Inspection"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1", 
        port=8000,
        reload=True
    )