from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class AccountStatus(str, Enum):
    ACTIVE = "active"          
    SUSPENDED = "suspended"    
    BANNED = "banned"          
    PENDING = "pending" 
    DELETED = "deleted"       


class UserRole(str, Enum):
    ADMIN = "admin"      
    AUTHOR = "author"    
    READER = "reader"    


class PostStatus(str, Enum):
    PENDING= "pending"
    REJECTED= "rejected"
    PUBLISHED = "published"  





class BaseSchema(BaseModel): 
    """ 
    Base class for all schemas.
    Allows reading from ORM (e.g., SQLAlchemy objects by .model_validate()).
    """
    
    
    @field_validator("*")
    @classmethod
    def format_field(cls, value):
        if isinstance(value, str): #for all strings, avoide crash for integer
            return value.strip().lower()
        return value
    
    model_config= ConfigDict(from_attributes=True)

