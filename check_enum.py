from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole') 
        ORDER BY enumsortorder
    """))
    
    print("Enum 'userrole' values di database:")
    for row in result:
        print(f"  - {row[0]}")
