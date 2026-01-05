from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.user import UserCreate, UserUpdate
from app.utils.password import hash_password, verify_password, generate_username


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If username already exists
        """
        # Generate username
        username = generate_username(user_data.first_name, user_data.birth_date)
        
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValueError(
                f"Username {username} sudah digunakan. "
                f"User dengan nama depan dan tanggal lahir yang sama sudah ada."
            )
        
        # Generate password (default: same as username)
        password = user_data.password if user_data.password else username
        password_hash = hash_password(password)
        
        # Create user
        user = User(
            username=username,
            password_hash=password_hash,
            full_name=user_data.full_name,
            first_name=user_data.first_name,
            birth_date=user_data.birth_date,
            role=user_data.role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            db: Database session
            username: Username
            password: Password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user
            
        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User tidak ditemukan")
        
        # Update fields if provided
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.first_name is not None:
            # If first_name or birth_date changed, regenerate username
            if user_data.first_name != user.first_name or (user_data.birth_date and user_data.birth_date != user.birth_date):
                new_first_name = user_data.first_name
                new_birth_date = user_data.birth_date if user_data.birth_date else user.birth_date
                new_username = generate_username(new_first_name, new_birth_date)
                
                # Check if new username already exists
                existing = db.query(User).filter(
                    User.username == new_username,
                    User.id != user_id
                ).first()
                
                if existing:
                    raise ValueError(f"Username {new_username} sudah digunakan")
                
                user.username = new_username
            
            user.first_name = user_data.first_name
        
        if user_data.birth_date is not None:
            user.birth_date = user_data.birth_date
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        if user_data.password is not None:
            user.password_hash = hash_password(user_data.password)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """
        Delete a user (soft delete by setting is_active to False).
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if deleted, False otherwise
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Soft delete
        user.is_active = False
        db.commit()
        
        return True


# Global instance
auth_service = AuthService()
