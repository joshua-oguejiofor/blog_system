from models.media import Media
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


#Repository layer pattern
class MediaRepository(BaseRepository[Media]):
    def __init__(self, db: AsyncSession):
        super().__init__(Media, db)
        
        
    
    async def get_my_medias(self, user_id: int, offset: int, limit: int):
    
        return await self.get_all(
            offset=offset, #pagination
            limit=limit,
            filters= (Media.uploaded_by == user_id,),
            order_by= Media.created_at.desc())# sorting
    
    
    async def get_medias(self, offset: int, limit: int):
    
        return await self.get_all(
            offset= offset, #pagination
            limit=limit,
            order_by= Media.uploaded_by.desc()
            )# sorting
        
    
    
    async def delete_media_with_post(self, post_id: int) -> Media:
        
        return await self.db.scalar(
            select(Media)
            .where(Media.post_id == post_id)
        )
        
         
        
        
        
        
        