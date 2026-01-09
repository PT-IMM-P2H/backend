# app/seeds/seed_users.py
from app.database import SessionLocal
from app.models.user import User, UserRole, UserKategori
from app.models.vehicle import Vehicle # Import ini penting agar SQLAlchemy mengenali relasi Vehicle
# Import model lain yang memiliki relasi (terutama yang menyebabkan error sebelumnya)
try:
    from app.models.p2h import P2HReport, TelegramNotification 
except ImportError:
    # Jika letak file p2h berbeda atau belum ada, pass saja
    pass

from app.utils.password import hash_password
from datetime import date

def seed_users():
    db = SessionLocal()
    
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

    try:
        for data in users_data:
            # Logika Password: namadepanDDMMYYYY
            first_name = data["full_name"].split()[0].lower()
            date_part = data["birth_date"].strftime("%d%m%Y")
            password = f"{first_name}{date_part}"
            password_hash = hash_password(password)

            # Cek apakah user sudah ada berdasarkan Nomor HP
            user = db.query(User).filter(User.phone_number == data["phone_number"]).first()
            
            if not user:
                # JIKA BELUM ADA: Buat User Baru
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
                print(f"✅ Akun {data['role'].value} baru berhasil dibuat: {data['full_name']}")
            else:
                # JIKA SUDAH ADA: Update data & password
                user.password_hash = password_hash
                user.full_name = data["full_name"]
                user.email = data["email"]
                user.birth_date = data["birth_date"]
                user.role = data["role"]
                user.kategori_pengguna = data["kategori_pengguna"]
                print(f"🔄 Akun ditemukan, data diperbarui: {data['full_name']}")
            
            print("="*50)
            print(f"User     : {data['full_name']}")
            print(f"Role     : {data['role'].value}")
            print(f"Phone    : {data['phone_number']}")
            print(f"Password : {password}")
            print("="*50 + "\n")
            
        db.commit()
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()