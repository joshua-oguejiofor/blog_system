from datetime import datetime

from pydantic import Field

from .base import BaseSchema, PostStatus

# POST


class PostResponse(BaseSchema):

    id: int
    author_id: int | None
    featured_image_id: int | None = None
    slug: str
    tag_id: list[int] = Field(default_factory=list)
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    status: PostStatus = Field(PostStatus.PENDING)
    created_at: datetime
    updated_at: datetime | None= None


class ExcerptResponse(BaseSchema):
    id: int
    title: str
    excerpt: str
    slug: str
    created_at: datetime






