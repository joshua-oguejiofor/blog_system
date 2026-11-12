import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TimeStamp


class AuditLog(Base, TimeStamp):
    __tablename__ = "audit_log"  
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)  
    action = sa.Column(sa.String(200), nullable=False)
    entity = sa.Column(sa.String(100), nullable=False)
    entity_id = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    
    __table_args__ = (sa.Index('ix_audit_log_entity_entity_id', 'entity', 'entity_id'),)
    
    # Relationship
    user = relationship("User", back_populates="audit_log")