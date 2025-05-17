# models/orm_models/entity_orm.py

from sqlalchemy import Column, String, TIMESTAMP, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.base import Base

class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cik = Column(String, nullable=False, unique=True, index=True)  # Add index for performance
    name = Column(String, nullable=False)
    entity_type = Column(
        String,
        nullable=False
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Add check constraint to match DB constraint
    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('company', 'person', 'trust', 'group')",
            name="entity_type_check"
        ),
    )

    # Relationships
    issuer_relationships = relationship(
        "Form4Relationship",
        foreign_keys="Form4Relationship.issuer_entity_id",
        back_populates="issuer_entity",
        cascade="all, delete-orphan"  # Consider if this cascade is appropriate
    )
    owner_relationships = relationship(
        "Form4Relationship",
        foreign_keys="Form4Relationship.owner_entity_id",
        back_populates="owner_entity",
        cascade="all, delete-orphan"  # Consider if this cascade is appropriate
    )

    def __repr__(self):
        return f"<Entity(id='{self.id}', cik='{self.cik}', name='{self.name}', type='{self.entity_type}')>"

    @classmethod
    def get_or_create(cls, session, cik, name, entity_type):
        """Get an existing entity or create a new one if it doesn't exist"""
        entity = session.query(cls).filter(cls.cik == cik).first()
        if not entity:
            entity = cls(cik=cik, name=name, entity_type=entity_type)
            session.add(entity)
            # Don't commit here - let the caller handle transaction
        return entity