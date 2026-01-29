"""
Export endpoints for Users, Vehicles, and P2H Reports
Supports Excel, PDF, and CSV formats
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import pandas as pd
import io
from datetime import date, datetime
from typing import Optional, List
from reportlab.lib import colors
from app.utils.datetime import get_current_datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import xlsxwriter

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User, UserRole, UserKategori
from app.models.vehicle import Vehicle, UnitKategori, ShiftType
from app.models.p2h import P2HReport, InspectionStatus

router = APIRouter(
    prefix="/export",
    tags=["Export"],
    dependencies=[Depends(get_current_user)]
)


def format_datetime(dt):
    """Format datetime to string"""
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M")
    if isinstance(dt, date):
        return dt.strftime("%Y-%m-%d")
    return str(dt)


@router.get("/users")
async def export_users(
    format: str = Query(..., description="Format: excel, pdf, or csv"),
    role: Optional[str] = Query(None, description="Filter by role"),
    kategori: Optional[str] = Query(None, description="Filter by kategori"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export users data to Excel, PDF, or CSV
    [ADMIN & SUPERADMIN ONLY]
    
    Filters:
    - role: superadmin/admin/user/viewer
    - kategori: IMM/TRAVEL
    - is_active: true/false
    - search: Search in name, email, phone
    """
    
    # Authorization: Only admin and superadmin can export
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Superadmin yang dapat mengekspor data"
        )
    
    # Build query
    query = db.query(User)
    
    # Apply filters
    filters = []
    if role:
        try:
            filters.append(User.role == UserRole(role.lower()))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}"
            )
    
    if kategori:
        kategori_upper = kategori.upper()
        if kategori_upper == 'PT':
            kategori_upper = 'IMM'
        try:
            filters.append(User.kategori_pengguna == UserKategori(kategori_upper))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid kategori: {kategori}"
            )
    
    if is_active is not None:
        filters.append(User.is_active == is_active)
    
    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.phone_number.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get users
    users = query.order_by(User.created_at.desc()).all()
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tidak ada data untuk diekspor"
        )
    
    # Prepare data
    data = []
    for user in users:
        data.append({
            'Email': user.email,
            'Nama Lengkap': user.full_name,
            'Nomor Telepon': user.phone_number,
            'Tanggal Lahir': format_datetime(user.birth_date),
            'Role': user.role.value if user.role else '',
            'Kategori': user.kategori_pengguna.value if user.kategori_pengguna else '',
            'Department': user.department.nama_department if user.department else '',
            'Position': user.position.nama_posisi if user.position else '',
            'Status': 'Aktif' if user.is_active else 'Tidak Aktif',
            'Tanggal Dibuat': format_datetime(user.created_at)
        })
    
    df = pd.DataFrame(data)
    
    # Generate file based on format
    timestamp = get_current_datetime().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data Pengguna', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Data Pengguna']
            
            # Format header
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            # Format cells
            cell_format = workbook.add_format({
                'border': 1,
                'align': 'left',
                'valign': 'vcenter'
            })
            
            # Apply formats
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)
        
        output.seek(0)
        filename = f"data_pengguna_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format.lower() == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        filename = f"data_pengguna_{timestamp}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format.lower() == "pdf":
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#4472C4'),
            spaceAfter=12,
            alignment=1  # Center
        )
        
        # Title
        title = Paragraph("Data Pengguna", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Convert DataFrame to list for table
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Adjust column widths
        col_widths = [1*inch, 1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch]
        
        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        filename = f"data_pengguna_{timestamp}.pdf"
        
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format tidak valid. Gunakan: excel, pdf, atau csv"
        )


@router.get("/vehicles")
async def export_vehicles(
    format: str = Query(..., description="Format: excel, pdf, or csv"),
    kategori: Optional[str] = Query(None, description="Filter by kategori"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    shift_type: Optional[str] = Query(None, description="Filter by shift type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by plat or lambung"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export vehicles data to Excel, PDF, or CSV
    [ADMIN & SUPERADMIN ONLY]
    
    Filters:
    - kategori: IMM/TRAVEL
    - vehicle_type: Vehicle type name
    - shift_type: shift/non_shift
    - is_active: true/false
    - search: Search in plat_nomor, no_lambung
    """
    
    # Authorization: Only admin and superadmin can export
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Superadmin yang dapat mengekspor data"
        )
    
    # Build query
    query = db.query(Vehicle)
    
    # Apply filters
    filters = []
    
    if kategori:
        kategori_upper = kategori.upper()
        if kategori_upper == 'PT':
            kategori_upper = 'IMM'
        try:
            filters.append(Vehicle.kategori_unit == UnitKategori(kategori_upper))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid kategori: {kategori}"
            )
    
    if vehicle_type:
        filters.append(Vehicle.vehicle_type == vehicle_type)
    
    if shift_type:
        try:
            filters.append(Vehicle.shift_type == ShiftType(shift_type.lower()))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid shift_type: {shift_type}"
            )
    
    if is_active is not None:
        filters.append(Vehicle.is_active == is_active)
    
    if search:
        search_filter = or_(
            Vehicle.plat_nomor.ilike(f"%{search}%"),
            Vehicle.no_lambung.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get vehicles
    vehicles = query.order_by(Vehicle.created_at.desc()).all()
    
    if not vehicles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tidak ada data untuk diekspor"
        )
    
    # Prepare data
    data = []
    for vehicle in vehicles:
        data.append({
            'Nomor Polisi': vehicle.plat_nomor,
            'Nomor Lambung': vehicle.no_lambung or '',
            'Tipe Kendaraan': vehicle.vehicle_type,
            'Kategori': vehicle.kategori_unit.value if vehicle.kategori_unit else '',
            'Shift': vehicle.shift_type.value if vehicle.shift_type else '',
            'Merk': vehicle.merk or '',
            'Expired STNK': format_datetime(vehicle.stnk_expiry),
            'Expired KIR': format_datetime(vehicle.kir_expiry),
            'Status': 'Aktif' if vehicle.is_active else 'Tidak Aktif',
            'Tanggal Dibuat': format_datetime(vehicle.created_at)
        })
    
    df = pd.DataFrame(data)
    timestamp = get_current_datetime().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data Kendaraan', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Data Kendaraan']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#70AD47',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            cell_format = workbook.add_format({
                'border': 1,
                'align': 'left',
                'valign': 'vcenter'
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
        
        output.seek(0)
        filename = f"data_kendaraan_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format.lower() == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        filename = f"data_kendaraan_{timestamp}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format.lower() == "pdf":
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#70AD47'),
            spaceAfter=12,
            alignment=1
        )
        
        title = Paragraph("Data Kendaraan", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        table_data = [df.columns.tolist()] + df.values.tolist()
        col_widths = [1*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1.2*inch]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        filename = f"data_kendaraan_{timestamp}.pdf"
        
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format tidak valid. Gunakan: excel, pdf, atau csv"
        )


@router.get("/p2h-reports")
async def export_p2h_reports(
    format: str = Query(..., description="Format: excel, pdf, or csv"),
    kategori: Optional[str] = Query(None, description="Filter by kategori"),
    report_status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by vehicle plat or user name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export P2H reports to Excel, PDF, or CSV
    [ADMIN & SUPERADMIN ONLY]
    
    Filters:
    - kategori: IMM/TRAVEL
    - report_status: pending/approved/rejected
    - start_date: Filter from date
    - end_date: Filter to date
    - search: Search in vehicle plat or user name
    """
    
    # Authorization: Only admin and superadmin can export
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Superadmin yang dapat mengekspor data"
        )
    
    # Build query with joins
    query = db.query(P2HReport).join(Vehicle).join(User)
    
    # Apply filters
    filters = []
    
    if kategori:
        kategori_upper = kategori.upper()
        if kategori_upper == 'PT':
            kategori_upper = 'IMM'
        try:
            filters.append(Vehicle.kategori_unit == UnitKategori(kategori_upper))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid kategori: {kategori}"
            )
    
    if report_status:
        try:
            filters.append(P2HReport.overall_status == InspectionStatus(report_status.lower()))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {report_status}"
            )
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            filters.append(P2HReport.created_at >= start)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format start_date tidak valid. Gunakan YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            filters.append(P2HReport.created_at <= end)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format end_date tidak valid. Gunakan YYYY-MM-DD"
            )
    
    if search:
        search_filter = or_(
            Vehicle.plat_nomor.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get reports
    reports = query.order_by(P2HReport.created_at.desc()).all()
    
    if not reports:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tidak ada data untuk diekspor"
        )
    
    # Prepare data
    data = []
    for report in reports:
        # Determine shift name
        shift_name = {1: 'Shift 1', 2: 'Shift 2', 3: 'Shift 3'}.get(report.shift_number, f'Shift {report.shift_number}')
        
        data.append({
            'Tanggal Pemeriksaan': format_datetime(report.submission_date),
            'Waktu': format_datetime(report.submission_time),
            'Shift': shift_name,
            'Nomor Polisi': report.vehicle.plat_nomor if report.vehicle else '',
            'No Lambung': report.vehicle.no_lambung if report.vehicle else '',
            'Tipe Kendaraan': report.vehicle.vehicle_type if report.vehicle else '',
            'Kategori': report.vehicle.kategori_unit.value if report.vehicle and report.vehicle.kategori_unit else '',
            'Nama Pemeriksa': report.user.full_name if report.user else '',
            'Status Pemeriksaan': report.overall_status.value if report.overall_status else '',
        })
    
    df = pd.DataFrame(data)
    timestamp = get_current_datetime().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Laporan P2H', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Laporan P2H']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#ED7D31',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
        
        output.seek(0)
        filename = f"laporan_p2h_{timestamp}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format.lower() == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        filename = f"laporan_p2h_{timestamp}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format.lower() == "pdf":
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#ED7D31'),
            spaceAfter=12,
            alignment=1
        )
        
        title = Paragraph("Laporan P2H", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        table_data = [df.columns.tolist()] + df.values.tolist()
        # Adjust column widths based on new columns (11 columns now)
        col_widths = [0.9*inch, 0.6*inch, 0.6*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch, 1.2*inch, 1*inch, 0.7*inch, 1.2*inch]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ED7D31')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        filename = f"laporan_p2h_{timestamp}.pdf"
        
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format tidak valid. Gunakan: excel, pdf, atau csv"
        )
