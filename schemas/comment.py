from datetime import datetime

from pydantic import Field, field_validator
from utility.field_utility import sanitize_input_data

from .base import BaseSchema

# COMMENT

    

class CreateComment(BaseSchema):

    post_id: int= Field(ge= 1)
    content: str= Field(..., min_length=5, max_length=5000)
    
    @field_validator("content")
    @classmethod
    def sanitize_content(cls, content):
        return sanitize_input_data(content)


class RplyComment(BaseSchema):
    parent_id: int= Field(ge= 1)
    content: str= Field(..., min_length=5, max_length=5000)
    
    
class UpdateComment(BaseSchema):
    comment_id: int= Field(ge= 1)
    content: str= Field(..., min_length=5, max_length=5000)
    
    
class CommentResponse(CreateComment):

    id: int
    parent_id: int | None= None
    user_id: int
    created_at: datetime
    updated_at: datetime | None= None


class CommentCachedPost(BaseSchema):
    id: int
    title: str
    author_id: int
