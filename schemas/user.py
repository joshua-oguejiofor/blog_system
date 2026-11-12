from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from utility.field_utility import format_field

from .base import BaseSchema

# # USER

    

class UserSchema(BaseModel):
    
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=20)
    
    @field_validator("email")
    @classmethod
    def format_email(cls, email: str):
        return format_field(email)


class UserResponse(BaseSchema):
    """Returned user data."""

    id: int    
    email: str 
    username: str | None= None
    role: str                
    created_at: datetime       
    updated_at: datetime | None= None
    

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("email")
    @classmethod
    def format_email(cls, email: str):
        return format_field(email)




class PasswordReset(BaseModel):
    reset_token: str
    new_password: str= Field(..., min_length=8, max_length=20)
    

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


    
class ViewProfile(BaseSchema):
    id: int
    user_id: int | None
    country: str
    user: UserResponse
    created_at: datetime
    updated_at: datetime | None = None
    bio: str | None = None
    profile_image_public_id: str | None = None
    profile_mime: str | None = None
    website_url: HttpUrl | None = None
    social_links: dict[str, Any] | None = None
    
  


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=20)
    new_password: str = Field(..., min_length=8, max_length=20)


class EmailVerification(BaseSchema):
    email: EmailStr 

    @field_validator("email")
    @classmethod
    def format_email(cls, email: str):
        return format_field(email)


