from models.category import Category
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)
        
        
    async def get_category(self, limit: int, offset: int):
        return await self.get_all(order_by= Category.name, limit= limit, offset= offset)
    
    async def get_name(self, name):
        return await self.db.scalar(
            select(Category.name)
            .where(Category.name == name))# filtering
    
    async def get_slug(self, slug):
        return await self.db.scalar(
            select(Category.slug)
            .where(Category.slug == slug))# filtering

