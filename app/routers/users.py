from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth_service import auth_service
from app.dependencies import get_current_user, require_role
from app.utils.response import base_response 

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Menambah Karyawan/User Baru (Superadmin dan Admin).
    Password akan otomatis dibuat: namadepan + DDMMYYYY jika dikosongkan.
    """
    try:
        user = auth_service.create_user(db, user_data)
        return base_response(
            message="User berhasil didaftarkan ke sistem",
            payload=UserResponse.model_validate(user).model_dump(mode='json'),
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Melihat Daftar Semua User (Superadmin dan Admin).
    """
    users = auth_service.get_all_users(db, skip=skip, limit=limit)
    # Data dikonversi ke UserResponse agar password_hash tidak ikut terkirim
    payload = [UserResponse.model_validate(u).model_dump(mode='json') for u in users]
    
    return base_response(
        message="Daftar user berhasil diambil",
        payload=payload
    )

@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Melihat Detail User berdasarkan ID.
    """
    user = auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    return base_response(
        message="Data user ditemukan",
        payload=UserResponse.model_validate(user).model_dump(mode='json')
    )

@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Memperbarui Data User (Superadmin dan Admin).
    """
    try:
        user = auth_service.update_user(db, user_id, user_data)
        return base_response(
            message="Data user berhasil diperbarui",
            payload=UserResponse.model_validate(user).model_dump(mode='json')
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Menonaktifkan User (Soft Delete, Superadmin dan Admin).
    """
    success = auth_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    return base_response(
        message="User berhasil dinonaktifkan",
        payload={"user_id": str(user_id)}
    )