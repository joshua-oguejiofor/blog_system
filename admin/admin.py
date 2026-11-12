"""
This module is responsible for registering an admin user in the database if it does not already exist. 
It checks for the existence of a user with the email specified in the settings and creates one with the provided password and role if not found.
"""


from core.config import settings
from core.database import AsyncSessionLocal
from core.security import hash_password
from models.user import User
from schemas import base
from sqlalchemy import select


async def register_admin_user():
    async with AsyncSessionLocal() as db:
    
        existing_user= await db.scalar(
            select(User)
            .where(User.email == settings.ADMIN_EMAIL)
            )
        
        if existing_user:
            return True
        
        admin_user= User(
            email=settings.ADMIN_EMAIL, 
            hashed_password= hash_password(settings.ADMIN_PASSWORD.get_secret_value()),
            acct_status=base.AccountStatus.ACTIVE, 
            is_verified=True, 
            role=base.UserRole.ADMIN,
            username=settings.ADMIN_USERNAME
            )
        
        db.add(admin_user) 
        await db.commit()
        await db.refresh(admin_user)
        return True
    
        
    