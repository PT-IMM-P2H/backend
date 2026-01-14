"""
Custom Exception Classes
Centralized exception handling for better error management
"""

from fastapi import HTTPException, status
from app.constants import ResponseMessages


class BaseAPIException(HTTPException):
    """Base exception for all API exceptions"""
    def __init__(self, status_code: int, message: str, detail: str = None):
        super().__init__(
            status_code=status_code,
            detail={"message": message, "detail": detail} if detail else {"message": message}
        )


class NotFoundException(BaseAPIException):
    """Resource not found exception"""
    def __init__(self, resource: str = None):
        message = f"{resource} tidak ditemukan" if resource else ResponseMessages.NOT_FOUND
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class UnauthorizedException(BaseAPIException):
    """Authentication failed exception"""
    def __init__(self, message: str = ResponseMessages.UNAUTHORIZED):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class ForbiddenException(BaseAPIException):
    """Access forbidden exception"""
    def __init__(self, message: str = ResponseMessages.FORBIDDEN):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class BadRequestException(BaseAPIException):
    """Bad request exception"""
    def __init__(self, message: str = ResponseMessages.INVALID_DATA, detail: str = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message, detail=detail)


class ConflictException(BaseAPIException):
    """Resource conflict exception"""
    def __init__(self, message: str = ResponseMessages.DUPLICATE_ENTRY):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message)


class ValidationException(BaseAPIException):
    """Validation error exception"""
    def __init__(self, message: str, detail: str = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message=message, detail=detail)


class InternalServerException(BaseAPIException):
    """Internal server error exception"""
    def __init__(self, message: str = ResponseMessages.INTERNAL_ERROR, detail: str = None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message, detail=detail)


# Specific domain exceptions
class UserNotFoundException(NotFoundException):
    """User not found exception"""
    def __init__(self):
        super().__init__(resource="Pengguna")


class VehicleNotFoundException(NotFoundException):
    """Vehicle not found exception"""
    def __init__(self):
        super().__init__(resource="Kendaraan")


class P2HReportNotFoundException(NotFoundException):
    """P2H Report not found exception"""
    def __init__(self):
        super().__init__(resource="Laporan P2H")


class InvalidCredentialsException(UnauthorizedException):
    """Invalid login credentials exception"""
    def __init__(self):
        super().__init__(message=ResponseMessages.LOGIN_FAILED)


class TokenExpiredException(UnauthorizedException):
    """Token expired exception"""
    def __init__(self):
        super().__init__(message=ResponseMessages.TOKEN_EXPIRED)


class InvalidTokenException(UnauthorizedException):
    """Invalid token exception"""
    def __init__(self):
        super().__init__(message=ResponseMessages.TOKEN_INVALID)


class InsufficientPermissionsException(ForbiddenException):
    """Insufficient permissions exception"""
    def __init__(self, required_role: str = None):
        message = f"Akses ditolak. Diperlukan role: {required_role}" if required_role else ResponseMessages.FORBIDDEN
        super().__init__(message=message)


class DuplicateEntryException(ConflictException):
    """Duplicate entry exception"""
    def __init__(self, field: str = None):
        message = f"{field} sudah terdaftar" if field else ResponseMessages.DUPLICATE_ENTRY
        super().__init__(message=message)
