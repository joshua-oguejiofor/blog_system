from models.post_tag import Tags
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class TagRepository(BaseRepository[Tags]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tags, db)
        
        
    async def get_tag_name(self, tag_name: str):
        
        return await self.db.scalar(
            select(Tags)
            .where(Tags.name == tag_name)
            )
        
        
    async def check_tags(self, tags_names: str):
        result =  await self.db.execute(
            select(Tags)
            .where(Tags.name.in_(tags_names))
            )
        return result.scalars().all()
        
    
    async def get_all_tags(self, offset: int, limit: int):
        return await self.get_all(order_by= Tags.name, offset= offset, limit= limit)
    
    