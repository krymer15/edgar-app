# models/orm_models/forms/derivative_security_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class DerivativeSecurity(Base):
    __tablename__ = "derivative_securities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    underlying_security_id = Column(UUID(as_uuid=True), ForeignKey("securities.id", ondelete="SET NULL", onupdate="CASCADE"))
    underlying_security_title = Column(String, nullable=False)
    conversion_price = Column(Numeric)
    exercise_date = Column(Date)
    expiration_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_derivative_underlying', 'underlying_security_id'),
    )

    # Relationships
    security = relationship("Security", foreign_keys=[security_id], back_populates="derivative_security")
    underlying_security = relationship("Security", foreign_keys=[underlying_security_id])

    def __repr__(self):
        return f"<DerivativeSecurity(id='{self.id}', security_id='{self.security_id}')>"