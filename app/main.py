from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import Base, engine
from app.utils.response import base_response 

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
    
    print("\n" + "="*60)
    print("                P2H SYSTEM PT. IMM BONTANG")
    print("="*60)
    print(f"🚀 Main API      : http://127.0.0.1:8000")
    print(f"📝 Swagger UI    : http://127.0.0.1:8000/docs")
    print("="*60 + "\n")

    try:
        from app.scheduler.scheduler import start_scheduler
        start_scheduler()
        logger.info("✅ Scheduler started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
    
    yield
    
    # --- SHUTDOWN ---
    logger.info("🛑 Shutting down P2H System API...")

# 1. Inisialisasi FastAPI dengan Metadata Lengkap
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## P2H (Pelaksanaan Pemeriksaan Harian) Vehicle Inspection System
    REST API dengan struktur response terstandarisasi.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 2. KONFIGURASI CORS (Update Sesuai Request Anda)
# Tentukan origin yang diizinkan (URL Frontend Vite Anda)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Menggunakan list origins yang sudah didefinisikan
    allow_credentials=True,          # WAJIB True untuk Cookie-based Auth
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Include OPTIONS for preflight
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],  # Add more headers
    expose_headers=["Content-Type", "Authorization"],  # Headers that browser can access
    max_age=3600,  # Cache preflight requests for 1 hour
)

# --- CUSTOM EXCEPTION HANDLERS ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field = errors[0]['loc'][-1]
    msg = f"Kesalahan pada field {field}: {errors[0]['msg']}"
    
    return base_response(
        message=msg,
        payload={"details": errors},
        status_code=422
    )

@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: Exception):
    return base_response(
        message="Resource atau data yang Anda cari tidak ditemukan",
        status_code=404
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
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
        payload={"version": settings.APP_VERSION, "docs": "/docs"}
    )

# Import and register routers
from app.routers import auth, users, vehicles, p2h, master_data

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(p2h.router, prefix="/p2h", tags=["P2H Inspection"])
app.include_router(master_data.router, prefix="/master-data", tags=["Master Data"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)