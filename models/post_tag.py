import sqlalchemy as sa
from schemas.base import PostStatus
from sqlalchemy.orm import relationship

from .base import Base, UpdateTimeStamp

post_tag_association = sa.Table(    
    "post_tags",
    Base.metadata,
    sa.Column("post_id", sa.Integer, sa.ForeignKey("post.id", ondelete="CASCADE"), primary_key=True), 
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True) 
)


class Tags(Base):
    __tablename__ = "tags"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    slug = sa.Column(sa.String(100), unique=True, nullable=False)  
    
    posts = relationship("Post", secondary=post_tag_association, back_populates="tags")


class Post(Base, UpdateTimeStamp):
    __tablename__ = "post"  

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(200), nullable=False, index=True)
    slug = sa.Column(sa.String(100), unique=True, nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    excerpt = sa.Column(sa.String(200), nullable=False)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True)  
    status = sa.Column(sa.Enum(PostStatus), default=PostStatus.PENDING)
    category_id= sa.Column(sa.Integer, sa.ForeignKey("category.id", ondelete="RESTRICT"))
    
    # Relationships 
    user = relationship("User", back_populates="post")
    comment = relationship("Comment", back_populates="post", cascade= "all, delete-orphan")
    book_mark = relationship("BookMark", back_populates="post", cascade= "all, delete-orphan")
    like = relationship("Likes", back_populates="post", cascade= "all, delete-orphan")
    tags = relationship("Tags", secondary=post_tag_association, back_populates="posts")
    media = relationship("Media", back_populates="post", cascade= "all, delete-orphan") 
    category= relationship("Category", back_populates="post")
