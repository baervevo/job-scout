"""Password hashing utilities using bcrypt"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with a random salt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password as a string
    """
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches the hash, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Return False if verification fails for any reason
        return False