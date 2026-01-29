"""
Schemas for bulk upload operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class BulkUploadError(BaseModel):
    """Error detail for single row"""
    row: int = Field(..., description="Row number in Excel (1-indexed)")
    field: Optional[str] = Field(None, description="Field name that caused error")
    message: str = Field(..., description="Error message")
    data: Optional[dict] = Field(None, description="Row data that failed")


class BulkUploadResponse(BaseModel):
    """Response for bulk upload operations"""
    success_count: int = Field(..., description="Number of successfully imported rows")
    error_count: int = Field(..., description="Number of failed rows")
    errors: List[BulkUploadError] = Field(default_factory=list, description="List of errors")
    total_rows: int = Field(..., description="Total rows processed")
