import sqlalchemy as sa
from schemas.base import AccountStatus, UserRole
from sqlalchemy.orm import relationship

from .base import Base, UpdateTimeStamp


class User(Base, UpdateTimeStamp):
    __tablename__ = "user"  # Fixed spacing
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String(120), unique=True, index=True, nullable=False)
    username = sa.Column(sa.String(30), nullable=True, unique=True)
    hashed_password = sa.Column(sa.String(150), nullable=False)
    role = sa.Column(sa.Enum(UserRole), default=UserRole.READER)
    acct_status = sa.Column(sa.Enum(AccountStatus), default=AccountStatus.PENDING)
    is_verified = sa.Column(sa.Boolean, default=False)

    
    # Relationships 
    profile = relationship("Profile", back_populates="user", uselist=False)  
    media = relationship("Media", back_populates="user")
    book_mark = relationship("BookMark", back_populates="user", cascade= "all, delete-orphan")
    post = relationship("Post", back_populates="user")
    like = relationship("Likes", back_populates="user", cascade= "all, delete-orphan")
    audit_log = relationship("AuditLog", back_populates="user") 
    comment = relationship("Comment", back_populates="user", cascade= "all, delete-orphan")
    received_notification= relationship("Notification",foreign_keys="Notification.recipient_id", back_populates="recipient", cascade="all, delete-orphan")
    sent_notification= relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender")



class Profile(Base, UpdateTimeStamp):
    __tablename__ = "profile"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), unique=True, index=True)  
    bio = sa.Column(sa.Text, nullable=True)
    profile_image_public_id = sa.Column(sa.String(200), nullable=True)
    profile_mime = sa.Column(sa.String(15), nullable=True) 
    website_url = sa.Column(sa.String(100), nullable=True)  
    country = sa.Column(sa.String(50), nullable=True) 
    social_links = sa.Column(sa.JSON, nullable=True) 
    
    # Relationship 
    user = relationship("User", back_populates="profile", uselist=False)

