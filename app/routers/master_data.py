from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole, Company, Department, Position, WorkStatus
from app.dependencies import require_role
from app.utils.response import base_response
from pydantic import BaseModel

router = APIRouter()

# --- SCHEMAS ---
class CompanyBase(BaseModel):
    nama_perusahaan: str
    status: str | None = None

class CompanyResponse(CompanyBase):
    id: UUID
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    nama_department: str

class DepartmentResponse(DepartmentBase):
    id: UUID
    class Config:
        from_attributes = True

class PositionBase(BaseModel):
    nama_posisi: str

class PositionResponse(PositionBase):
    id: UUID
    class Config:
        from_attributes = True

class WorkStatusBase(BaseModel):
    nama_status: str

class WorkStatusResponse(WorkStatusBase):
    id: UUID
    class Config:
        from_attributes = True


# --- COMPANIES ENDPOINTS ---
@router.get("/companies")
async def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Get all active companies (soft delete aware)"""
    companies = db.query(Company).filter(Company.is_active == True).all()
    payload = [CompanyResponse.model_validate(c).model_dump(mode='json') for c in companies]
    return base_response(message="Data perusahaan berhasil diambil", payload=payload)

@router.post("/companies", status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Create new company"""
    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return base_response(
        message="Perusahaan berhasil ditambahkan",
        payload=CompanyResponse.model_validate(company).model_dump(mode='json')
    )

@router.put("/companies/{company_id}")
async def update_company(
    company_id: UUID,
    company_data: CompanyBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Update company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    
    for key, value in company_data.model_dump().items():
        setattr(company, key, value)
    
    db.commit()
    db.refresh(company)
    return base_response(
        message="Perusahaan berhasil diupdate",
        payload=CompanyResponse.model_validate(company).model_dump(mode='json')
    )

@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Soft delete company"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.is_active == True
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    
    # Soft delete: update is_active and deleted_at
    company.soft_delete()
    db.commit()
    return base_response(message="Perusahaan berhasil dihapus", payload=None)


# --- DEPARTMENTS ENDPOINTS ---
@router.get("/departments")
async def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Get all active departments (soft delete aware)"""
    departments = db.query(Department).filter(Department.is_active == True).all()
    payload = [DepartmentResponse.model_validate(d).model_dump(mode='json') for d in departments]
    return base_response(message="Data departemen berhasil diambil", payload=payload)

@router.post("/departments", status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_data: DepartmentBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Create new department"""
    dept = Department(**dept_data.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return base_response(
        message="Departemen berhasil ditambahkan",
        payload=DepartmentResponse.model_validate(dept).model_dump(mode='json')
    )

@router.put("/departments/{dept_id}")
async def update_department(
    dept_id: UUID,
    dept_data: DepartmentBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Update department"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departemen tidak ditemukan")
    
    dept.nama_department = dept_data.nama_department
    db.commit()
    db.refresh(dept)
    return base_response(
        message="Departemen berhasil diupdate",
        payload=DepartmentResponse.model_validate(dept).model_dump(mode='json')
    )

@router.delete("/departments/{dept_id}")
async def delete_department(
    dept_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Soft delete department"""
    dept = db.query(Department).filter(
        Department.id == dept_id,
        Department.is_active == True
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departemen tidak ditemukan")
    
    # Soft delete
    dept.soft_delete()
    db.commit()
    return base_response(message="Departemen berhasil dihapus", payload=None)


# --- POSITIONS ENDPOINTS ---
@router.get("/positions")
async def get_positions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Get all active positions (soft delete aware)"""
    positions = db.query(Position).filter(Position.is_active == True).all()
    payload = [PositionResponse.model_validate(p).model_dump(mode='json') for p in positions]
    return base_response(message="Data posisi berhasil diambil", payload=payload)

@router.post("/positions", status_code=status.HTTP_201_CREATED)
async def create_position(
    pos_data: PositionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Create new position"""
    pos = Position(**pos_data.model_dump())
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return base_response(
        message="Posisi berhasil ditambahkan",
        payload=PositionResponse.model_validate(pos).model_dump(mode='json')
    )

@router.put("/positions/{pos_id}")
async def update_position(
    pos_id: UUID,
    pos_data: PositionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Update position"""
    pos = db.query(Position).filter(Position.id == pos_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Posisi tidak ditemukan")
    
    pos.nama_posisi = pos_data.nama_posisi
    db.commit()
    db.refresh(pos)
    return base_response(
        message="Posisi berhasil diupdate",
        payload=PositionResponse.model_validate(pos).model_dump(mode='json')
    )

@router.delete("/positions/{pos_id}")
async def delete_position(
    pos_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Soft delete position"""
    pos = db.query(Position).filter(
        Position.id == pos_id,
        Position.is_active == True
    ).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Posisi tidak ditemukan")
    
    # Soft delete
    pos.soft_delete()
    db.commit()
    return base_response(message="Posisi berhasil dihapus", payload=None)


# --- WORK STATUSES ENDPOINTS ---
@router.get("/work-statuses")
async def get_work_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Get all active work statuses (soft delete aware)"""
    statuses = db.query(WorkStatus).filter(WorkStatus.is_active == True).all()
    payload = [WorkStatusResponse.model_validate(s).model_dump(mode='json') for s in statuses]
    return base_response(message="Data status kerja berhasil diambil", payload=payload)

@router.post("/work-statuses", status_code=status.HTTP_201_CREATED)
async def create_work_status(
    status_data: WorkStatusBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Create new work status"""
    work_status = WorkStatus(**status_data.model_dump())
    db.add(work_status)
    db.commit()
    db.refresh(work_status)
    return base_response(
        message="Status kerja berhasil ditambahkan",
        payload=WorkStatusResponse.model_validate(work_status).model_dump(mode='json')
    )

@router.put("/work-statuses/{status_id}")
async def update_work_status(
    status_id: UUID,
    status_data: WorkStatusBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Update work status"""
    work_status = db.query(WorkStatus).filter(WorkStatus.id == status_id).first()
    if not work_status:
        raise HTTPException(status_code=404, detail="Status kerja tidak ditemukan")
    
    work_status.nama_status = status_data.nama_status
    db.commit()
    db.refresh(work_status)
    return base_response(
        message="Status kerja berhasil diupdate",
        payload=WorkStatusResponse.model_validate(work_status).model_dump(mode='json')
    )

@router.delete("/work-statuses/{status_id}")
async def delete_work_status(
    status_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """Soft delete work status"""
    work_status = db.query(WorkStatus).filter(
        WorkStatus.id == status_id,
        WorkStatus.is_active == True
    ).first()
    if not work_status:
        raise HTTPException(status_code=404, detail="Status kerja tidak ditemukan")
    
    # Soft delete
    work_status.soft_delete()
    db.commit()
    return base_response(message="Status kerja berhasil dihapus", payload=None)
