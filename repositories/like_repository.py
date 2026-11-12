from models.likes import Likes
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import BaseRepository


class LikeRepository(BaseRepository[Likes]):
    def __init__(self, db: AsyncSession):
        super().__init__(Likes, db)
        
    

    async def count_post_likes(self, post_id: int) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Likes)
            .where(Likes.post_id == post_id)
        )
        return result.scalar_one()    
    
    
    async def like_exists(self, user_id: int, post_id: int):
        return await self.db.scalar(
            select(Likes)
            .where(Likes.post_id == post_id, 
                   Likes.user_id == user_id))
    
        
    async def get_post_likes(self, post_id: int):
        result=  await self.db.execute(
            select(Likes)
            .options(selectinload(Likes.user))
            .where(Likes.post_id == post_id))
        
        return result.scalars().all()
        
 
 
    async def check_user_likes(self, post_id: int, user_id: int):
        result=  await self.db.execute(
            select(Likes)
            .options(selectinload(Likes.post))
            .where(Likes.post_id == post_id, Likes.user_id == user_id))
        
        return result.scalars().all()
        
