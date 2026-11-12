import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, UpdateTimeStamp


class Media(Base, UpdateTimeStamp):
    __tablename__ = "media"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    public_id = sa.Column(sa.String(300), nullable=True)  
    file_name = sa.Column(sa.String(255), nullable=False) 
    file_size = sa.Column(sa.Integer, nullable=True)  
    file_type = sa.Column(sa.String(100), nullable=True)  
    uploaded_by = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)  
    post_id= sa.Column(sa.Integer, sa.ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False)  
    
    # Relationships 
    post = relationship("Post", back_populates="media")
    user = relationship("User", back_populates="media")
 