from datetime import datetime

from .base import BaseSchema


class NotificationResponse(BaseSchema):
    recipient_id: int
    message: str
    notification_type: str
    id: int
    is_read: bool
    created_at: datetime
    sender_id: int 
    entity_id: int
    entity_type: str