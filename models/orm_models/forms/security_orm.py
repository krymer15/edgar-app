# models/orm_models/forms/security_orm.py
from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, Numeric, ARRAY, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Security(Base):
    __tablename__ = "securities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    issuer_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    security_type = Column(String, nullable=False)
    standard_cusip = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Table arguments
    __table_args__ = (
        Index('idx_securities_issuer', 'issuer_entity_id'),
        Index('idx_securities_title', 'title'),
        CheckConstraint("security_type IN ('equity', 'option', 'convertible', 'other_derivative')",
                      name="security_type_check"),
    )

    # Relationships
    issuer_entity = relationship("Entity", foreign_keys=[issuer_entity_id])
    derivative_security = relationship("DerivativeSecurity", back_populates="security", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Security(id='{self.id}', title='{self.title}', type='{self.security_type}')>"