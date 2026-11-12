from models.bookmark import BookMark
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .base import BaseRepository


class BookMarkRepositroy(BaseRepository[BookMark]):
    def __init__(self, db: AsyncSession):
        super().__init__(BookMark, db)
        
    async def get_user_bookmark(self, user_id: int, offset: int= 0, limit: int= 20):
        
        bookmarks = await self.db.execute(
        select(BookMark)
        .options(selectinload(BookMark.post))#eager loading
        .where(BookMark.user_id == user_id)# filtering
        .offset(offset).limit(limit)# pagination
        .order_by(BookMark.title_name)# sorting
        )

        return bookmarks.scalars().all()
        
    async def check_bookmark(self, user_id: int, post_id: int) -> int:
        count_result = await self.db.execute(
            select(func.count())
            .select_from(BookMark)
            .where(BookMark.user_id == user_id)
            )
        bookmark_count = count_result.scalar_one()
        
        bookmark_result = await self.db.execute(
        select(BookMark.id)
        .where(
            BookMark.user_id == user_id,
            BookMark.post_id == post_id)
        )
        
        bookmark_id = bookmark_result.scalar_one_or_none()

        return bookmark_count, bookmark_id

           
    