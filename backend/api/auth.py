# backend/api/auth.py
"""
Authentication and Authorization
JWT token-based authentication with bcrypt password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to encode
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# Simple in-memory user store for MVP (replace with database later)
class UserStore:
    """Simple in-memory user storage for MVP"""
    
    def __init__(self):
        self.users = {}
        self.user_id_counter = 1
        
        # Create a demo user
        self._create_demo_user()
    
    def _create_demo_user(self):
        """Create a demo user for testing"""
        demo_user = {
            'id': self.user_id_counter,
            'username': 'demo',
            'email': 'demo@kitforge.com',
            'hashed_password': get_password_hash('demo123'),
            'subscription_tier': 'free',
            'cards_generated_this_month': 0,
            'created_at': datetime.now()
        }
        self.users['demo'] = demo_user
        self.user_id_counter += 1
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username"""
        return self.users.get(username)
    
    def create_user(self, username: str, email: str, password: str) -> dict:
        """Create a new user"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        user = {
            'id': self.user_id_counter,
            'username': username,
            'email': email,
            'hashed_password': get_password_hash(password),
            'subscription_tier': 'free',
            'cards_generated_this_month': 0,
            'created_at': datetime.now()
        }
        
        self.users[username] = user
        self.user_id_counter += 1
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user"""
        user = self.get_user(username)
        if not user:
            return None
        
        if not verify_password(password, user['hashed_password']):
            return None
        
        return user
    
    def increment_card_count(self, username: str):
        """Increment the card generation count for a user"""
        if username in self.users:
            self.users[username]['cards_generated_this_month'] += 1
    
    def can_generate_card(self, username: str) -> tuple[bool, str]:
        """
        Check if user can generate a card based on their tier
        
        Returns:
            (can_generate, reason)
        """
        user = self.get_user(username)
        if not user:
            return False, "User not found"
        
        if user['subscription_tier'] == 'paid':
            return True, "Unlimited access"
        
        # Free tier limit
        free_limit = int(os.getenv('FREE_TIER_CARDS_PER_MONTH', 5))
        if user['cards_generated_this_month'] >= free_limit:
            return False, f"Free tier limit reached ({free_limit} cards/month)"
        
        return True, f"Free tier: {user['cards_generated_this_month']}/{free_limit} used"


# Singleton instance
user_store = UserStore()
