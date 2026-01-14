"""
Base Repository - Common database operations for all repositories
"""

from sqlalchemy.orm import Session, Query
from typing import TypeVar, Generic, Type, Optional, List
from uuid import UUID

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    
    Principles:
    - Accept clean, typed parameters
    - No conditional checking of parameters
    - Return raw data or Query objects
    - Let caller handle business logic
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get_by_id(self, db: Session, id: UUID) -> Optional[ModelType]:
        """Get single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj: ModelType) -> ModelType:
        """Create new record"""
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(self, db: Session, obj: ModelType) -> ModelType:
        """Update existing record"""
        db.commit()
        db.refresh(obj)
        return obj
    
    def delete(self, db: Session, obj: ModelType) -> None:
        """Delete record"""
        db.delete(obj)
        db.commit()
    
    def get_query(self, db: Session) -> Query:
        """Get base query for the model"""
        return db.query(self.model)
