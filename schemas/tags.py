from pydantic import Field, field_validator
from utility.field_utility import sanitize_input_data

from .base import BaseSchema


class CreateTag(BaseSchema):
    name: str= Field(..., min_length=3)
    
    @field_validator("name")
    @classmethod
    def clean(cls, name):
        return sanitize_input_data(name)



class TagResponse(BaseSchema):
    id: int
    name: str
    slug: str
    