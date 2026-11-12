from datetime import datetime

from pydantic import Field, field_validator
from utility.field_utility import sanitize_input_data

from .base import BaseSchema


# CATEGORY
class CreateCategory(BaseSchema):

    name: str = Field(..., min_length=2, max_length=100)
    description: str | None= None

    @field_validator("*")
    @classmethod
    def clean_incoming_data(cls, value: str):
        return sanitize_input_data(value)


class CategoryResponse(BaseSchema):

    id: int
    name: str 
    description: str | None= None
    slug: str
    created_at: datetime

