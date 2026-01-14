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

# --- KONFIGURASI PORT ---
# Kita set ke 8000 sebagai port default aplikasi
PORT = 8000 

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
    print(f"🚀 Main API      : http://127.0.0.1:{PORT}")
    print(f"📝 Swagger UI    : http://127.0.0.1:{PORT}/docs")
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

# 2. KONFIGURASI CORS - Menggunakan settings dari .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Ambil dari .env
    allow_credentials=True,     # WAJIB True untuk Cookie-based Auth & JWT
    allow_methods=["*"],        # Izinkan semua method (GET, POST, PUT, DELETE, OPTIONS, dll)
    allow_headers=["*"],        # Izinkan semua header (termasuk Authorization)
    expose_headers=["*"],       # Expose semua headers ke frontend
)

# --- CUSTOM EXCEPTION HANDLERS ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Handle case where loc might be empty
    field = errors[0]['loc'][-1] if errors[0]['loc'] else "Unknown"
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
from app.routers import auth, users, vehicles, p2h, master_data, dashboard

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(p2h.router, prefix="/p2h", tags=["P2H Inspection"])
app.include_router(master_data.router, prefix="/master-data", tags=["Master Data"])
app.include_router(dashboard.router, tags=["Dashboard"])

# Alias: Tambahkan route /checklist tanpa prefix untuk kompatibilitas frontend
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.models.user import User
from app.models.checklist import ChecklistTemplate
from app.schemas.p2h import ChecklistItemResponse, ChecklistItemCreate
from app.dependencies import get_current_user, require_role
from app.models.user import UserRole
from fastapi import Depends, HTTPException

@app.get("/checklist", tags=["P2H Inspection"])
async def get_checklist_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Alias endpoint untuk /p2h/checklist.
    Mendapatkan semua checklist items yang aktif.
    """
    items = db.query(ChecklistTemplate).filter(
        ChecklistTemplate.is_active == True
    ).order_by(
        ChecklistTemplate.section_name,
        ChecklistTemplate.item_order
    ).all()
    
    payload = [ChecklistItemResponse.model_validate(item).model_dump(mode='json') for item in items]
    
    return base_response(
        message="Semua checklist items berhasil diambil",
        payload=payload
    )

@app.post("/checklist", status_code=status.HTTP_201_CREATED, tags=["P2H Inspection"])
async def post_checklist_alias(
    item_data: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Alias endpoint untuk POST /p2h/checklist.
    Menambah pertanyaan baru langsung dari UI Front-End.
    """
    new_item = ChecklistTemplate(
        item_name=item_data.question_text,
        section_name=item_data.section_name,
        vehicle_tags=item_data.vehicle_tags,
        applicable_shifts=item_data.applicable_shifts,
        options=item_data.options,
        item_order=item_data.item_order,
        is_active=True
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return base_response(
        message="Pertanyaan baru berhasil ditambahkan ke database",
        payload={
            "id": str(new_item.id),
            "question_text": new_item.item_name,
            "vehicle_tags": new_item.vehicle_tags
        },
        status_code=201
    )

@app.delete("/checklist/{checklist_id}", status_code=status.HTTP_200_OK, tags=["P2H Inspection"])
async def delete_checklist_alias(
    checklist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Alias endpoint untuk DELETE /p2h/checklist/{id}.
    Menghapus (soft delete) pertanyaan.
    """
    item = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    
    # Soft delete - set is_active to False
    item.is_active = False
    db.commit()
    
    return base_response(
        message="Pertanyaan berhasil dihapus",
        payload={"id": str(item.id)}
    )

@app.put("/checklist/{checklist_id}", status_code=status.HTTP_200_OK, tags=["P2H Inspection"])
async def update_checklist_alias(
    checklist_id: UUID,
    item_data: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Alias endpoint untuk PUT /p2h/checklist/{id}.
    Mengupdate pertanyaan yang sudah ada.
    """
    item = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    
    # Update fields
    item.item_name = item_data.question_text
    item.section_name = item_data.section_name
    item.vehicle_tags = item_data.vehicle_tags
    item.applicable_shifts = item_data.applicable_shifts
    item.options = item_data.options
    item.item_order = item_data.item_order
    
    db.commit()
    db.refresh(item)
    
    payload = ChecklistItemResponse.model_validate(item).model_dump(mode='json')
    return base_response(
        message="Pertanyaan berhasil diupdate",
        payload=payload
    )

if __name__ == "__main__":
    import uvicorn
    # Port 8000 sebagai default aplikasi
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT, reload=True)