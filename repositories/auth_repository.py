from models.user import User
from schemas.base import UserRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import BaseRepository


class AuthRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    
    async def get_by_email(self, email: str):
        return await self.db.scalar(select(User).where(User.email == email))
        
        
    
    async def get_admin(self):
        result=  await self.db.scalar(
            select(User)
            .where(User.role == UserRole.ADMIN))
        
        return result    
    
    async def check_username(self, username: str):
        return await self.db.scalar(
            select(User)
            .where(User.username == username)
        )