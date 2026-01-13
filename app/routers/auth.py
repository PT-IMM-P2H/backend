from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
from app.utils.jwt import create_access_token
from app.utils.response import base_response  # Wrapper response standar
from app.dependencies import get_current_user 
from app.models.user import User

router = APIRouter()

@router.post("/login")
async def login(
    data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Endpoint Login: Memvalidasi kredensial, membuat JWT, 
    dan menyimpannya di HttpOnly Cookie untuk keamanan Anti-XSS.
    """
    # 1. Validasi user melalui service
    user = auth_service.authenticate_user(db, data.username, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Generate token (berisi ID user dan role)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    # 3. Siapkan data user untuk payload (menggunakan schema UserResponse)
    user_data = UserResponse.model_validate(user).model_dump(mode='json')
    
    # 4. Buat objek response menggunakan wrapper base_response
    # Token tetap dikirim di payload agar FE bisa menyimpannya jika diperlukan (opsional)
    response = base_response(
        message="Login Berhasil", 
        payload={
            "user": user_data, 
            "access_token": access_token,
            "token_type": "bearer"
        }
    )

    # 5. Set HttpOnly Cookie (Saran Expert)
    # Ini adalah lapisan keamanan utama untuk mencegah pencurian token via XSS
    response.set_cookie(
        key="access_token",      # Nama cookie yang akan dicari oleh server
        value=access_token,      # Isi JWT token
        httponly=True,           # WAJIB: Mencegah akses JavaScript ke cookie
        max_age=3600,            # Berlaku selama 1 jam (3600 detik)
        samesite="lax",          # Mencegah pengiriman cookie pada Cross-Site Request yang berisiko
        secure=True              # Set True untuk menghindari security warning
    )

    return response

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint Me: Mengambil profil user yang sedang aktif.
    Bergantung pada validasi token (baik dari Header maupun Cookie).
    """
    user_data = UserResponse.model_validate(current_user).model_dump(mode='json')
    
    return base_response(
        message="Data profil berhasil diambil", 
        payload=user_data
    )