from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.jwt import decode_access_token

# Security scheme tetap dipertahankan agar ikon gembok di Swagger tetap muncul
# auto_error=False agar kita bisa menangani error secara kustom (misal jika token ada di cookie)
security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency untuk mendapatkan user yang sedang login.
    Mendukung pengecekan via Header Authorization (Swagger/Mobile) 
    dan HttpOnly Cookie (Front-End Web).
    """
    token = None

    # 1. Cek token di Header Authorization (untuk Swagger UI)
    if credentials:
        token = credentials.credentials
    
    # 2. Jika di Header tidak ada, cek di Cookie (untuk Front-End Web)
    if not token:
        token = request.cookies.get("access_token")

    # Jika sama sekali tidak ada token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi login tidak ditemukan. Silahkan login kembali.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau telah kadaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. Ambil user_id dari payload
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format token tidak dikenali",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 5. Ambil user dari database
    try:
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID Pengguna tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan dalam sistem",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun Anda sedang dinonaktifkan. Hubungi admin."
        )
    
    return user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory untuk membatasi akses berdasarkan Role.
    Tetap dipertahankan sesuai kode asli Anda.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Peran yang diizinkan: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    
    return role_checker