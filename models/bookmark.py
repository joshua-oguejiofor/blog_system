import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TimeStamp


class BookMark(Base, TimeStamp):
    __tablename__ = "book_mark"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False) 
    post_id = sa.Column(sa.Integer, sa.ForeignKey("post.id", ondelete="CASCADE"), nullable=False) 
    title_name= sa.Column(sa.String(200), nullable=False)
    
    __table_args__ = (sa.UniqueConstraint('user_id', 'post_id', name='unique_user_post_bookmark'),)
    
    # Relationships
    user = relationship("User", back_populates="book_mark")
    post = relationship("Post", back_populates="book_mark")
