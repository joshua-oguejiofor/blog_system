from models.comment import Comment
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Comment, db)
        
    
    async def get_all_comment(self, post_id, limit: int, offset: int):
        return await self.get_all(filters= (Comment.post_id == post_id,), offset= offset, limit= limit, order_by= Comment.created_at.asc())






