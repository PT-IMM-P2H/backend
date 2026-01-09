"""Script to deactivate vehicles with old enum values"""
from sqlalchemy import create_engine, text
from app.config import settings

def main():
    engine = create_engine(settings.DATABASE_URL)
    
    # Check current state
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, no_lambung, vehicle_type::text as vtype, is_active 
            FROM vehicles 
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
        """))
        rows = result.fetchall()
        
        print(f"\n🔍 Found {len(rows)} vehicles with old enum values:")
        for row in rows:
            print(f"  - ID: {row[0]}, Lambung: {row[1]}, Type: {row[2]}, Active: {row[3]}")
        
        if not rows:
            print("\n✅ No vehicles with old enum values found. Database is clean!")
            return
        
        # Deactivate them
        print("\n🔄 Deactivating vehicles with old enum values...")
        result = conn.execute(text("""
            UPDATE vehicles
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
        """))
        conn.commit()
        
        print(f"✅ Deactivated {result.rowcount} vehicles")
        
        # Verify
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM vehicles 
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS') AND is_active = true
        """))
        count = result.scalar()
        
        if count == 0:
            print("✅ Verification successful: All old vehicles are now inactive")
        else:
            print(f"⚠️  Warning: Still {count} active vehicles with old enum values")

if __name__ == "__main__":
    main()
