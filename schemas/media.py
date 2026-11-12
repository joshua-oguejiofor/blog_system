from datetime import datetime

from schemas.base import BaseSchema


class MediaResponse(BaseSchema):
    id: int
    public_id: str
    file_name: str
    file_size: float
    file_type: str
    uploaded_by: int
    post_id: int
    created_at: datetime
    updated_at: datetime | None

    