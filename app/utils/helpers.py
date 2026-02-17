import secrets
import string
from typing import Optional


def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Length of the token (default: 32)
        
    Returns:
        Random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_verification_token() -> str:
    """Generate a verification token for email verification."""
    return generate_token(64)


def generate_reset_token() -> str:
    """Generate a password reset token."""
    return generate_token(64)


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (without dot)
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing potentially dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()
