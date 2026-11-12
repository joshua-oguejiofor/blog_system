"""Creating user repsitory"""

from models.user import Profile, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repositories.base import BaseRepository


class UserRepository(BaseRepository[Profile]):
    def __init__(self, db: AsyncSession):
        super().__init__(Profile, db)# database_table and db connection are passed to the base repository
        
    async def get_profile_by_id(self, profile_id: int) -> Profile | None:
        db_profile= await self.db.execute(
            select(Profile)
            .options(selectinload(Profile.user))# eager loading
            .where(Profile.id == profile_id))# filtering
        
        return db_profile.scalar_one_or_none()
    
    
    async def get_profile_by_user_id(self, user_id: int) -> Profile | None:
        result = await self.db.execute(
            select(Profile)
            .options(selectinload(Profile.user))
            .where(Profile.user_id == user_id)
        )

        return result.scalar_one_or_none()
      
      
    async def get_all_profile(self, offset: int, limit: int) -> Profile:
        return await self.get_all(
            offset= offset, 
            limit= limit, 
            related_table=Profile.user, 
            order_by= Profile.created_at)
        
        
    async def search_user(self, username: str, offset: int, limit: int):
        user= await self.db.execute(
            select(Profile)
            .options(selectinload(Profile.user))
            .join(Profile.user)
            .where(User.username.ilike(f"%{username}%"))
            #for cases of multiple username
            .offset(offset)
            .limit(limit)
        )
        
        return user.scalars().all()
        
    