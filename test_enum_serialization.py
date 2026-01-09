from app.models.vehicle import VehicleType
from sqlalchemy import create_engine, Column, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class TestVehicle(Base):
    __tablename__ = "test_vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)

# Test what value is sent
from sqlalchemy.sql import sqltypes
import sqlalchemy

print("VehicleType values:")
for vt in VehicleType:
    print(f"  {vt.name} = '{vt.value}' (type: {type(vt.value)})")

print("\nTest serialization:")
vt = VehicleType.LIGHT_VEHICLE
print(f"  str(vt) = {str(vt)}")
print(f"  vt.value = {vt.value}")
print(f"  repr(vt) = {repr(vt)}")

# Check SQLAlchemy enum type
from sqlalchemy import Enum as SQLEnum
enum_type = SQLEnum(VehicleType)
print(f"\nSQLAlchemy Enum type:")
print(f"  enum_class: {enum_type.enum_class}")
print(f"  name: {enum_type.name}")

# Try to get the literal processor
from app.database import engine
dialect = engine.dialect
type_compiler = dialect.type_compiler(dialect, None)

print(f"\nDialect: {dialect.name}")
