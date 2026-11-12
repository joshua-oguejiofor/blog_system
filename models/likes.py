import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TimeStamp


class Likes(Base, TimeStamp):
    __tablename__ = "likes"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)  
    post_id = sa.Column(sa.Integer, sa.ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False) 
    

    __table_args__ = (sa.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    # Relationships
    user = relationship("User", back_populates="like")
    post = relationship("Post", back_populates="like")
