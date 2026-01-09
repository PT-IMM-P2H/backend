"""
Script untuk update password user yang sudah ada dengan format yang benar:
namadepanDDMMYYYY
"""
from app.database import SessionLocal
from app.models.user import User
from app.utils.password import hash_password

db = SessionLocal()

try:
    # Get all users
    users = db.query(User).all()
    
    print("🔄 Updating user passwords...")
    print("=" * 60)
    
    for user in users:
        if user.birth_date:
            # Generate password: namadepanDDMMYYYY
            first_name = user.full_name.split()[0].lower()
            date_part = user.birth_date.strftime("%d%m%Y")
            password = f"{first_name}{date_part}"
            
            # Update password
            user.password_hash = hash_password(password)
            
            print(f"✅ Updated: {user.full_name}")
            print(f"   Phone: {user.phone_number}")
            print(f"   Email: {user.email}")
            print(f"   Password: {password}")
            print("-" * 60)
    
    db.commit()
    print("\n🎉 All passwords updated successfully!")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {str(e)}")
finally:
    db.close()
