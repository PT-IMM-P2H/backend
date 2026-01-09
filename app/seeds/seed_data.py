import sys
from pathlib import Path
from datetime import date
from sqlalchemy.orm import Session

# 1. Tambahkan root directory ke sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import SessionLocal
# Import models dan Enums
from app.models.user import User, Company, Department, Position, WorkStatus, UserRole, UserKategori
from app.models.vehicle import Vehicle, VehicleType, UnitKategori
from app.models.notification import TelegramNotification 
from app.models.p2h import P2HReport, P2HDetail, P2HDailyTracker 
from app.models.checklist import ChecklistTemplate 
from app.utils.password import hash_password

def seed_master_data(db: Session):
    print("🏗️ Seeding Master Data...")
    
    # Seed Companies
    companies = [
        {"nama_perusahaan": "PT Indominco Mandiri", "status": "User"},
        {"nama_perusahaan": "PT Bara Usaha Mandiri", "status": "Driver"},
        {"nama_perusahaan": "PT Gelora Lintas Maharitas", "status": "Driver"},
        {"nama_perusahaan": "PT Sabda Tunggal", "status": "Driver Truk Sampah"},
    ]
    for co in companies:
        if not db.query(Company).filter_by(nama_perusahaan=co["nama_perusahaan"]).first():
            db.add(Company(**co))

    # Seed Departments
    departments = ["Asset & Inventory Management", "Port Maintenance", "Mine Operation", "Information Technology"]
    for dept in departments:
        if not db.query(Department).filter_by(nama_department=dept).first():
            db.add(Department(nama_department=dept))

    # Seed Positions
    positions = ["Assistant Vice President", "Department Head", "Direktur", "Driver"]
    for pos in positions:
        if not db.query(Position).filter_by(nama_posisi=pos).first():
            db.add(Position(nama_posisi=pos))

    # Seed Work Statuses
    statuses = ["Karyawan", "Kontraktor"]
    for stat in statuses:
        if not db.query(WorkStatus).filter_by(nama_status=stat).first():
            db.add(WorkStatus(nama_status=stat))

    db.commit()
    print("✅ Master Data seeded.")

def seed_users(db: Session):
    print("👥 Seeding Users...")
    
    imm_co = db.query(Company).filter_by(nama_perusahaan="PT Indominco Mandiri").first()
    dept_port = db.query(Department).filter_by(nama_department="Port Maintenance").first()
    pos_head = db.query(Position).filter_by(nama_posisi="Department Head").first()
    stat_karyawan = db.query(WorkStatus).filter_by(nama_status="Karyawan").first()

    users_data = [
        {
            "email": "andi.aldo@imm.co.id",
            "full_name": "Andi Aldo",
            "phone_number": "081243569877",
            "birth_date": date(1990, 1, 15),
            "department_id": dept_port.id if dept_port else None,
            "position_id": pos_head.id if pos_head else None,
            "work_status_id": stat_karyawan.id if stat_karyawan else None,
            "company_id": imm_co.id if imm_co else None,
            "kategori_pengguna": UserKategori.IMM,
            "role": UserRole.admin
        }
    ]

    for u_data in users_data:
        # Generate password: namadepanDDMMYYYY
        first_name = u_data["full_name"].split()[0].lower()
        date_part = u_data["birth_date"].strftime("%d%m%Y")
        password = f"{first_name}{date_part}"
        
        if not db.query(User).filter_by(phone_number=u_data["phone_number"]).first():
            new_user = User(
                email=u_data["email"],
                password_hash=hash_password(password),
                full_name=u_data["full_name"],
                phone_number=u_data["phone_number"],
                birth_date=u_data["birth_date"],
                department_id=u_data["department_id"],
                position_id=u_data["position_id"],
                work_status_id=u_data["work_status_id"],
                company_id=u_data["company_id"],
                kategori_pengguna=u_data["kategori_pengguna"],
                role=u_data["role"]
            )
            db.add(new_user)
            print(f"✅ User created: {u_data['full_name']}")
            print(f"   Phone: {u_data['phone_number']}")
            print(f"   Password: {password}")
    
    db.commit()
    print("✅ Users seeded.")

def seed_vehicles(db: Session):
    print("🚗 Seeding Vehicles...")
    
    imm_co = db.query(Company).filter_by(nama_perusahaan="PT Indominco Mandiri").first()
    user_andi = db.query(User).filter_by(phone_number="081243569877").first()

    vehicles = [
        {
            "no_lambung": "P.309",
            "warna_no_lambung": "Kuning",
            "plat_nomor": "KT 1234 ZM",
            "vehicle_type": VehicleType.LIGHT_VEHICLE,
            "merk": "Toyota Innova reborn 2.4G",
            "user_id": user_andi.id if user_andi else None,
            "company_id": imm_co.id if imm_co else None,
            "stnk_expiry": date(2028, 12, 28),
            "pajak_expiry": date(2025, 12, 28),
            "kir_expiry": date(2028, 12, 28),
            "no_rangka": "MK2KSWPNUJJ000338",
            "no_mesin": "4N15UCP7140",
            "kategori_unit": UnitKategori.IMM
        }
    ]

    for v_data in vehicles:
        if not db.query(Vehicle).filter_by(no_lambung=v_data["no_lambung"]).first():
            db.add(Vehicle(**v_data))

    db.commit()
    print("✅ Vehicles seeded.")

def main():
    db = SessionLocal()
    try:
        seed_master_data(db)
        seed_users(db)
        seed_vehicles(db)
        print("\n🎉 Seeding process finished successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()