from datetime import datetime

from .base import BaseSchema


class BookMarkResponse(BaseSchema):
    id: int
    post_id: int
    title_name: str    
    created_at: datetime