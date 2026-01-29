# backend/app/seed_admin.py
import sys
import os

# Menambahkan folder 'backend' ke path agar bisa import 'app' dan 'models'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
# PERBAIKAN DI SINI: Mengambil dari models.user
from app.models.user import User, UserRole, UserKategori 
from passlib.context import CryptContext
from datetime import date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_superadmin():
    db = SessionLocal()
    try:
        # Data Admin
        target_phone = "085754538366"
        target_email = "admin@p2h.com"
        
        # Cek user
        existing_user = db.query(User).filter(User.phone_number == target_phone).first()
        
        if existing_user:
            print(f"User dengan No HP {target_phone} sudah ada!")
        else:
            print("Membuat Superadmin Yunnifa...")
            
            raw_password = "yunnifa12062003"
            hashed = pwd_context.hash(raw_password)

            superadmin = User(
                full_name="Yunnifa Nur Lailli",
                email=target_email, 
                phone_number=target_phone,
                password_hash=hashed,
                birth_date=date(2003, 6, 12),
                role=UserRole.superadmin,       
                kategori_pengguna=UserKategori.IMM,
                is_active=True,
                department_id=None,
                position_id=None,
                work_status_id=None,
                company_id=None
            )
            
            db.add(superadmin)
            db.commit()
            
            print("---------------------------------------------")
            print("✅ Sukses! Superadmin berhasil dibuat.")
            print(f"👤 Nama : Yunnifa Nur Lailli")
            print(f"📱 Phone: {target_phone}")
            print(f"🔑 Pass : {raw_password}")
            print("---------------------------------------------")
            
    except Exception as e:
        print(f"❌ Terjadi error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_superadmin()