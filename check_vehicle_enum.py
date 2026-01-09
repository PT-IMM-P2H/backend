from app.database import engine
import sqlalchemy as sa

with engine.connect() as conn:
    result = conn.execute(sa.text(
        "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'vehicletype')"
    ))
    enum_values = [row[0] for row in result]
    print("Database VehicleType enum values:")
    for val in enum_values:
        print(f"  - {val}")
