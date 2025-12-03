# backend/models/user.py
"""
User model for authentication and subscription management
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    FREE = "free"
    PAID = "paid"


class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    username: str
    hashed_password: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    cards_generated_this_month: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
