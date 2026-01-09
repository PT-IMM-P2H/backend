from app.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.user import User

db = SessionLocal()

try:
    # Cek user yang baru dibuat
    users = db.query(User).all()
    print("=" * 60)
    print("USERS:")
    print("=" * 60)
    for user in users:
        print(f"  Name: {user.full_name}")
        print(f"  Email: {user.email}")
        print(f"  Phone: {user.phone_number}")
        print(f"  Role: {user.role.value}")
        print(f"  Kategori: {user.kategori_pengguna.value}")
        print("-" * 60)
    
    # Cek vehicle yang baru dibuat
    vehicles = db.query(Vehicle).all()
    print("\n" + "=" * 60)
    print("VEHICLES:")
    print("=" * 60)
    for vehicle in vehicles:
        print(f"  No Lambung: {vehicle.no_lambung}")
        print(f"  Plat Nomor: {vehicle.plat_nomor}")
        print(f"  Vehicle Type: {vehicle.vehicle_type.value}")
        print(f"  Merk: {vehicle.merk}")
        print(f"  Kategori Unit: {vehicle.kategori_unit.value}")
        print(f"  Shift Type: {vehicle.shift_type.value}")
        print("-" * 60)
        
finally:
    db.close()
