from passlib.context import CryptContext
from datetime import date

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_username(first_name: str, birth_date: date) -> str:
    """
    Generate username from first name and birth date.
    Format: [FirstName][DDMMYYYY]
    
    Example:
        first_name = "Budi"
        birth_date = 1990-05-15
        result = "Budi15051990"
    
    Args:
        first_name: User's first name
        birth_date: User's birth date
        
    Returns:
        Generated username
    """
    # Format date as DDMMYYYY
    date_str = birth_date.strftime("%d%m%Y")
    
    # Combine first name with date
    username = f"{first_name}{date_str}"
    
    return username
