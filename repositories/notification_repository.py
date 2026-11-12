from models.notification import Notification
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)
        
    
    async def get_all_my_notiffication(self, user_id: int, limit: int, offset: int):
        return await self.get_all(
            offset= offset, 
            limit= limit,
            filters=(Notification.recipient_id == user_id, ), 
            order_by= Notification.created_at.desc()
            )
    
    
