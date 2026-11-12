from datetime import datetime

from .base import BaseSchema


class _UserSchem(BaseSchema):
    role: str
    username: str
        

class LikeResponse(BaseSchema):
    post_id: int
    user_id: int
    id: int
    created_at: datetime
    user: _UserSchem
      