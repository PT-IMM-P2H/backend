"""Script untuk memeriksa nilai enum vehicletype di database"""
from sqlalchemy import create_engine, text
from app.config import settings

def main():
    engine = create_engine(settings.DATABASE_URL)
    
    print("\n🔍 Memeriksa nilai enum 'vehicletype' di PostgreSQL...\n")
    
    with engine.connect() as conn:
        # Query untuk mendapatkan semua nilai enum
        result = conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'vehicletype') 
            ORDER BY enumsortorder
        """))
        
        values = [row[0] for row in result]
        
        print(f"Total nilai enum: {len(values)}\n")
        print("Nilai enum yang tersedia:")
        for i, value in enumerate(values, 1):
            is_legacy = value in ['LV', 'EV', 'DC', 'SC', 'BIS']
            marker = "🔸 [LEGACY]" if is_legacy else "✅ [BARU]   "
            print(f"  {i:2d}. {marker} '{value}'")
        
        # Cek data kendaraan
        print("\n\n📊 Data kendaraan di database:\n")
        result = conn.execute(text("""
            SELECT 
                vehicle_type::text,
                COUNT(*) as jumlah,
                SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as aktif,
                SUM(CASE WHEN NOT is_active THEN 1 ELSE 0 END) as nonaktif
            FROM vehicles
            GROUP BY vehicle_type::text
            ORDER BY vehicle_type::text
        """))
        
        for row in result:
            vtype, total, aktif, nonaktif = row
            is_legacy = vtype in ['LV', 'EV', 'DC', 'SC', 'BIS']
            marker = "🔸" if is_legacy else "✅"
            print(f"  {marker} {vtype:20s} | Total: {total:2d} | Aktif: {aktif:2d} | Nonaktif: {nonaktif:2d}")
        
        print("\n✅ Enum check selesai!")

if __name__ == "__main__":
    main()
