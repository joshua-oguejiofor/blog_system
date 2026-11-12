import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, UpdateTimeStamp


class Comment(Base, UpdateTimeStamp):
    __tablename__ = "comment"  

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey("post.id", ondelete="CASCADE"), nullable=False)  
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("comment.id", ondelete="CASCADE"), nullable=True) 
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False) 
    content = sa.Column(sa.Text, nullable=False)  


    # Relationships 
    
    post = relationship("Post", back_populates="comment")
    user = relationship("User", back_populates="comment")
    replies = relationship("Comment", backref="parent", remote_side=[id])  