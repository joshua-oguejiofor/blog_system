from datetime import datetime

from .base import BaseSchema


class AduitResponse(BaseSchema):
    id: int
    user_id: int
    action: str
    entity: str
    entity_id: int
    created_at: datetime
