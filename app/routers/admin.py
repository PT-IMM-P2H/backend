# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole, UserKategori
from app.utils.password import hash_password
from datetime import date
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/seed-users")
def seed_users_endpoint(
    secret_key: str,
    db: Session = Depends(get_db)
):
    """
    🌱 Endpoint untuk seed initial users ke database production
    
    **HANYA BOLEH DIPANGGIL SEKALI SAAT SETUP AWAL!**
    
    Membutuhkan secret_key untuk keamanan.
    """
    
    # Simple security check
    SEED_SECRET = "IMM-P2H-SEED-2026"  # Ganti dengan secret yang aman
    
    if secret_key != SEED_SECRET:
        logger.warning(f"❌ Unauthorized seed attempt with key: {secret_key}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret key"
        )
    
    users_data = [
        # --- SUPERADMIN ---
        {
            "full_name": "Yunnifa Nur Lailli",
            "phone_number": "085754538366",
            "email": "yunnifa@imm.co.id",
            "birth_date": date(2003, 6, 12),
            "role": UserRole.superadmin,
            "kategori_pengguna": UserKategori.IMM
        },
        # --- USER BIASA (Driver) ---
        {
            "full_name": "Budi Santoso",
            "phone_number": "081234567890",
            "email": "budi@imm.co.id",
            "birth_date": date(1990, 5, 15),
            "role": UserRole.user,
            "kategori_pengguna": UserKategori.IMM
        }
    ]
    
    created_users = []
    updated_users = []
    
    try:
        for data in users_data:
            # Logika Password: namadepanDDMMYYYY
            first_name = data["full_name"].split()[0].lower()
            date_part = data["birth_date"].strftime("%d%m%Y")
            password = f"{first_name}{date_part}"
            password_hash = hash_password(password)
            
            # Cek apakah user sudah ada
            user = db.query(User).filter(User.phone_number == data["phone_number"]).first()
            
            if not user:
                # Buat user baru
                new_user = User(
                    full_name=data["full_name"],
                    email=data["email"],
                    phone_number=data["phone_number"],
                    birth_date=data["birth_date"],
                    password_hash=password_hash,
                    role=data["role"],
                    kategori_pengguna=data["kategori_pengguna"],
                    is_active=True
                )
                db.add(new_user)
                created_users.append({
                    "name": data["full_name"],
                    "phone": data["phone_number"],
                    "password": password,
                    "role": data["role"].value
                })
                logger.info(f"✅ Created new user: {data['full_name']}")
            else:
                # Update user yang sudah ada
                user.password_hash = password_hash
                user.full_name = data["full_name"]
                user.email = data["email"]
                user.birth_date = data["birth_date"]
                user.role = data["role"]
                user.kategori_pengguna = data["kategori_pengguna"]
                updated_users.append({
                    "name": data["full_name"],
                    "phone": data["phone_number"],
                    "password": password,
                    "role": data["role"].value
                })
                logger.info(f"🔄 Updated existing user: {data['full_name']}")
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Users seeded successfully",
            "data": {
                "created": created_users,
                "updated": updated_users,
                "total": len(created_users) + len(updated_users)
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Seed error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed users: {str(e)}"
        )
