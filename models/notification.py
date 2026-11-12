import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TimeStamp


class Notification(Base, TimeStamp):
    __tablename__ = "notification"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    recipient_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    sender_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    notification_type = sa.Column(sa.String(50), nullable=False)  
    entity_id= sa.Column(sa.Integer, nullable=False)
    entity_type= sa.Column(sa.String(30), nullable=False)
    message = sa.Column(sa.Text, nullable=False)  
    is_read = sa.Column(sa.Boolean, default=False)

    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_notification")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_notification")
