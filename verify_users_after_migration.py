"""Script untuk verifikasi data users setelah migration"""
from sqlalchemy import create_engine, text
from app.config import settings
from app.utils.password import verify_password

def main():
    engine = create_engine(settings.DATABASE_URL)
    
    print("\n" + "="*60)
    print("🔍 VERIFIKASI DATA USERS SETELAH MIGRATION")
    print("="*60 + "\n")
    
    with engine.connect() as conn:
        # 1. Cek jumlah users
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"📊 Total users di database: {user_count}")
        
        # 2. Cek detail semua users
        result = conn.execute(text("""
            SELECT 
                id,
                phone_number,
                full_name,
                email,
                role,
                is_active,
                created_at
            FROM users
            ORDER BY created_at
        """))
        
        print("\n📋 Detail Users:\n")
        users = result.fetchall()
        
        if not users:
            print("❌ MASALAH: Tidak ada user di database!")
            print("   Migration mungkin menghapus data yang salah!")
            return
        
        for i, user in enumerate(users, 1):
            uid, phone, name, email, role, active, created = user
            status = "✅ AKTIF" if active else "❌ NONAKTIF"
            print(f"{i}. {status}")
            print(f"   Phone: {phone}")
            print(f"   Name:  {name}")
            print(f"   Email: {email}")
            print(f"   Role:  {role}")
            print(f"   ID:    {uid}")
            print()
        
        # 3. Cek password hash untuk superadmin
        print("🔐 Verifikasi Password Hash:\n")
        result = conn.execute(text("""
            SELECT phone_number, password_hash, full_name
            FROM users
            WHERE role = 'superadmin'
        """))
        
        superadmin = result.fetchone()
        if superadmin:
            phone, pwd_hash, name = superadmin
            print(f"Superadmin: {name}")
            print(f"Phone:      {phone}")
            print(f"Hash:       {pwd_hash[:50]}...")
            print(f"Hash Length: {len(pwd_hash)} chars")
            
            # Expected password
            expected_pwd = "yunnifa12062003"
            print(f"\nExpected password: {expected_pwd}")
            print("Hash exists: ✅" if pwd_hash else "❌ KOSONG!")
        else:
            print("❌ Superadmin tidak ditemukan!")
        
        # 4. Cek vehicles yang dihapus
        print("\n" + "="*60)
        print("🚗 Status Vehicles Setelah Migration:")
        print("="*60 + "\n")
        
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN NOT is_active THEN 1 ELSE 0 END) as inactive
            FROM vehicles
        """))
        
        row = result.fetchone()
        total, active, inactive = row
        
        print(f"Total vehicles: {total}")
        print(f"  - Aktif:      {active}")
        print(f"  - Nonaktif:   {inactive}")
        
        # 5. Cek apakah ada vehicle dengan enum legacy
        result = conn.execute(text("""
            SELECT no_lambung, vehicle_type::text, is_active
            FROM vehicles
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
        """))
        
        legacy = result.fetchall()
        if legacy:
            print(f"\n⚠️ Masih ada {len(legacy)} kendaraan dengan enum legacy:")
            for lambung, vtype, active in legacy:
                status = "Aktif" if active else "Nonaktif"
                print(f"  - {lambung}: {vtype} ({status})")
        else:
            print("\n✅ Tidak ada kendaraan dengan enum legacy")
        
        print("\n" + "="*60)
        print("✅ Verifikasi selesai!")
        print("="*60)

if __name__ == "__main__":
    main()
