"""
Script untuk verifikasi kredensial login yang ada di database
"""
from app.database import SessionLocal
from app.models.user import User
from app.utils.password import verify_password

db = SessionLocal()

# Kredensial yang akan dicek
credentials_to_check = [
    {
        "name": "Yunnifa (Superadmin)",
        "phone": "085754538366",
        "password": "yunnifa12062003"
    },
    {
        "name": "Budi (User)",
        "phone": "081234567890",
        "password": "budi15051990"
    },
    {
        "name": "Andi (Admin)",
        "phone": "081243569877",
        "password": "andi15011990"
    }
]

print("=" * 70)
print("VERIFIKASI KREDENSIAL LOGIN")
print("=" * 70)

try:
    for cred in credentials_to_check:
        print(f"\n🔍 Checking: {cred['name']}")
        print(f"   Phone: {cred['phone']}")
        
        # Cari user di database
        user = db.query(User).filter(User.phone_number == cred['phone']).first()
        
        if user:
            print(f"   ✅ User FOUND in database")
            print(f"      - Full Name: {user.full_name}")
            print(f"      - Email: {user.email}")
            print(f"      - Role: {user.role.value}")
            print(f"      - Birth Date: {user.birth_date}")
            
            # Verifikasi password
            is_password_correct = verify_password(cred['password'], user.password_hash)
            
            if is_password_correct:
                print(f"      - Password: ✅ CORRECT ({cred['password']})")
            else:
                print(f"      - Password: ❌ WRONG")
                print(f"        Expected: {cred['password']}")
                # Coba tampilkan password yang seharusnya
                first_name = user.full_name.split()[0].lower()
                if user.birth_date:
                    date_part = user.birth_date.strftime("%d%m%Y")
                    expected_password = f"{first_name}{date_part}"
                    print(f"        Should be: {expected_password}")
        else:
            print(f"   ❌ User NOT FOUND in database")
        
        print("-" * 70)
    
    # Tampilkan semua users yang ada
    print("\n" + "=" * 70)
    print("ALL USERS IN DATABASE:")
    print("=" * 70)
    
    all_users = db.query(User).all()
    for user in all_users:
        first_name = user.full_name.split()[0].lower()
        if user.birth_date:
            date_part = user.birth_date.strftime("%d%m%Y")
            expected_password = f"{first_name}{date_part}"
        else:
            expected_password = "N/A (no birth_date)"
            
        print(f"\n📋 {user.full_name}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role.value}")
        print(f"   Expected Password: {expected_password}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
finally:
    db.close()

print("\n" + "=" * 70)
