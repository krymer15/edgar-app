# models/adapters/position_adapter.py
import uuid
from typing import List, Optional, Dict

from models.dataclasses.forms.position_data import RelationshipPositionData
from models.orm_models.forms.relationship_position_orm import RelationshipPosition

def convert_position_data_to_orm(position_data: RelationshipPositionData) -> RelationshipPosition:
    """Convert RelationshipPositionData dataclass to RelationshipPosition ORM model"""
    return RelationshipPosition(
        id=uuid.UUID(position_data.id) if position_data.id else None,
        relationship_id=uuid.UUID(position_data.relationship_id),
        security_id=uuid.UUID(position_data.security_id),
        position_date=position_data.position_date,
        shares_amount=position_data.shares_amount,
        direct_ownership=position_data.direct_ownership,
        ownership_nature_explanation=position_data.ownership_nature_explanation,
        filing_id=uuid.UUID(position_data.filing_id),
        transaction_id=uuid.UUID(position_data.transaction_id) if position_data.transaction_id else None,
        is_position_only=position_data.is_position_only,
        position_type=position_data.position_type,
        derivative_security_id=uuid.UUID(position_data.derivative_security_id) if position_data.derivative_security_id else None
    )

def convert_position_orm_to_data(position_orm: RelationshipPosition) -> RelationshipPositionData:
    """Convert RelationshipPosition ORM model to RelationshipPositionData dataclass"""
    return RelationshipPositionData(
        id=str(position_orm.id),
        relationship_id=str(position_orm.relationship_id),
        security_id=str(position_orm.security_id),
        position_date=position_orm.position_date,
        shares_amount=position_orm.shares_amount,
        direct_ownership=position_orm.direct_ownership,
        ownership_nature_explanation=position_orm.ownership_nature_explanation,
        filing_id=str(position_orm.filing_id),
        transaction_id=str(position_orm.transaction_id) if position_orm.transaction_id else None,
        is_position_only=position_orm.is_position_only,
        position_type=position_orm.position_type,
        derivative_security_id=str(position_orm.derivative_security_id) if position_orm.derivative_security_id else None
    )