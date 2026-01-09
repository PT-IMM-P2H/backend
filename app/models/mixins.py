# app/models/mixins.py
from sqlalchemy import Column, Boolean, DateTime
from datetime import datetime

class SoftDeleteMixin:
    """
    Mixin untuk implementasi Soft Delete.
    Menambahkan field is_active dan deleted_at ke model yang menggunakannya.
    """
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Method untuk melakukan soft delete"""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Method untuk restore data yang telah di-soft delete"""
        self.is_active = True
        self.deleted_at = None
