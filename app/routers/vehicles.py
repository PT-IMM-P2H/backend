from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleP2HStatus
from app.dependencies import get_current_user, require_role
from app.services.p2h_service import p2h_service
from app.utils.response import base_response  # Import wrapper response standar

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin))
):
    """
    Create a new vehicle (Superadmin only).
    """
    # Check if no_lambung already exists
    existing = db.query(Vehicle).filter(Vehicle.no_lambung == vehicle_data.no_lambung).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nomor lambung {vehicle_data.no_lambung} sudah terdaftar"
        )
    
    vehicle = Vehicle(**vehicle_data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    return base_response(
        message="Data kendaraan berhasil ditambahkan",
        payload=VehicleResponse.model_validate(vehicle).model_dump(),
        status_code=status.HTTP_201_CREATED
    )


@router.get("")
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by nomor lambung, plat, atau merk"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of vehicles with search and filter.
    """
    query = db.query(Vehicle)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vehicle.no_lambung.ilike(search_term)) |
            (Vehicle.plat_nomor.ilike(search_term)) |
            (Vehicle.merk.ilike(search_term))
        )
    
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    
    if is_active is not None:
        query = query.filter(Vehicle.is_active == is_active)
    
    vehicles = query.offset(skip).limit(limit).all()
    payload = [VehicleResponse.model_validate(v).model_dump() for v in vehicles]
    
    return base_response(
        message="Daftar kendaraan berhasil diambil",
        payload=payload
    )


@router.get("/lambung/{no_lambung}")
async def get_vehicle_by_lambung(
    no_lambung: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search vehicle by nomor lambung and get P2H status.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.no_lambung == no_lambung).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kendaraan dengan nomor lambung {no_lambung} tidak ditemukan"
        )
    
    p2h_status = p2h_service.get_vehicle_p2h_status(db, vehicle.id)
    
    # Gabungkan data kendaraan dan status P2H dalam satu payload rapi
    result = {
        "vehicle": VehicleResponse.model_validate(vehicle).model_dump(),
        "can_submit_p2h": p2h_status["can_submit_p2h"],
        "p2h_completed_today": p2h_status["p2h_completed_today"],
        "current_shift": p2h_status["current_shift"],
        "shifts_completed": p2h_status["shifts_completed"],
        "message": p2h_status["message"]
    }
    
    return base_response(
        message="Status P2H kendaraan berhasil diambil",
        payload=result
    )


@router.get("/{vehicle_id}")
async def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vehicle by ID.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kendaraan tidak ditemukan"
        )
    
    return base_response(
        message="Data kendaraan ditemukan",
        payload=VehicleResponse.model_validate(vehicle).model_dump()
    )


@router.put("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin))
):
    """
    Update vehicle (Superadmin only).
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kendaraan tidak ditemukan"
        )
    
    if vehicle_data.no_lambung and vehicle_data.no_lambung != vehicle.no_lambung:
        existing = db.query(Vehicle).filter(
            Vehicle.no_lambung == vehicle_data.no_lambung,
            Vehicle.id != vehicle_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nomor lambung {vehicle_data.no_lambung} sudah terdaftar"
            )
    
    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    return base_response(
        message="Data kendaraan berhasil diperbarui",
        payload=VehicleResponse.model_validate(vehicle).model_dump()
    )


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin))
):
    """
    Delete vehicle (soft delete, Superadmin only).
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kendaraan tidak ditemukan"
        )
    
    vehicle.is_active = False
    db.commit()
    
    return base_response(
        message="Kendaraan berhasil dinonaktifkan (soft delete)",
        payload={"vehicle_id": str(vehicle_id)}
    )