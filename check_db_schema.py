from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Cek userrole enum
    result = conn.execute(text("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole') 
        ORDER BY enumsortorder
    """))
    
    print("=== Enum 'userrole' values di database ===")
    for row in result:
        print(f"  '{row[0]}'")
    
    # Cek definisi kolom role di tabel users
    result2 = conn.execute(text("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    """))
    
    print("\n=== Definisi kolom 'role' di tabel 'users' ===")
    for row in result2:
        print(f"  column_name: {row[0]}, data_type: {row[1]}, udt_name: {row[2]}")
