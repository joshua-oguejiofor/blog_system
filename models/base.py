import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase


# Base model for other models
class Base(DeclarativeBase):
    pass


class TimeStamp:
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    

class UpdateTimeStamp:
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())  
    