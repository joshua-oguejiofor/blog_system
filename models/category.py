import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TimeStamp


class Category(Base, TimeStamp):
    __tablename__ = "category"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(50), nullable=False, index=True)
    slug = sa.Column(sa.String(100), unique=True, nullable=False) 
    description = sa.Column(sa.Text, nullable=True)  

    post= relationship("Post", back_populates= "category")

