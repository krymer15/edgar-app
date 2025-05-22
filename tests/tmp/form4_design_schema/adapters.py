# Adapters for Form 4 Schema (FOR IMPLEMENTATION)

import uuid
from typing import List, Optional

# Import dataclasses
from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.dataclasses.forms.transaction_data import (
    NonDerivativeTransactionData,
    DerivativeTransactionData,
    TransactionBase
)
from models.dataclasses.forms.position_data import PositionData

# Import ORM models
from models.orm_models.forms.security_orm import Security
from models.orm_models.forms.derivative_security_orm import DerivativeSecurity
from models.orm_models.forms.non_derivative_transaction_orm import NonDerivativeTransaction
from models.orm_models.forms.derivative_transaction_orm import DerivativeTransaction
from models.orm_models.forms.relationship_position_orm import RelationshipPosition

# Security adapters
def convert_security_data_to_orm(security_data: SecurityData) -> Security:
    """Convert SecurityData dataclass to Security ORM model"""
    return Security(
        id=uuid.UUID(security_data.id) if security_data.id else None,
        title=security_data.title,
        issuer_entity_id=uuid.UUID(security_data.issuer_entity_id),
        security_type=security_data.security_type,
        standard_cusip=security_data.standard_cusip
    )

def convert_security_orm_to_data(security_orm: Security) -> SecurityData:
    """Convert Security ORM model to SecurityData dataclass"""
    return SecurityData(
        id=str(security_orm.id),
        title=security_orm.title,
        issuer_entity_id=str(security_orm.issuer_entity_id),
        security_type=security_orm.security_type,
        standard_cusip=security_orm.standard_cusip
    )

# Derivative security adapters
def convert_derivative_security_data_to_orm(derivative_data: DerivativeSecurityData) -> DerivativeSecurity:
    """Convert DerivativeSecurityData dataclass to DerivativeSecurity ORM model"""
    return DerivativeSecurity(
        id=uuid.UUID(derivative_data.id) if derivative_data.id else None,
        security_id=uuid.UUID(derivative_data.security_id),
        underlying_security_id=uuid.UUID(derivative_data.underlying_security_id) if derivative_data.underlying_security_id else None,
        underlying_security_title=derivative_data.underlying_security_title,
        conversion_price=derivative_data.conversion_price,
        exercise_date=derivative_data.exercise_date,
        expiration_date=derivative_data.expiration_date
    )

def convert_derivative_security_orm_to_data(derivative_orm: DerivativeSecurity) -> DerivativeSecurityData:
    """Convert DerivativeSecurity ORM model to DerivativeSecurityData dataclass"""
    return DerivativeSecurityData(
        id=str(derivative_orm.id),
        security_id=str(derivative_orm.security_id),
        underlying_security_id=str(derivative_orm.underlying_security_id) if derivative_orm.underlying_security_id else None,
        underlying_security_title=derivative_orm.underlying_security_title,
        conversion_price=derivative_orm.conversion_price,
        exercise_date=derivative_orm.exercise_date,
        expiration_date=derivative_orm.expiration_date
    )

# Transaction adapters - For Phase 2
def convert_non_derivative_transaction_data_to_orm(transaction_data: NonDerivativeTransactionData) -> NonDerivativeTransaction:
    """Convert NonDerivativeTransactionData dataclass to NonDerivativeTransaction ORM model"""
    return NonDerivativeTransaction(
        id=uuid.UUID(transaction_data.id) if transaction_data.id else None,
        form4_filing_id=uuid.UUID(transaction_data.filing_id) if transaction_data.filing_id else None,
        relationship_id=uuid.UUID(transaction_data.relationship_id),
        security_id=uuid.UUID(transaction_data.security_id),
        transaction_code=transaction_data.transaction_code,
        transaction_date=transaction_data.transaction_date,
        transaction_form_type=transaction_data.transaction_form_type,
        shares_amount=transaction_data.shares_amount,
        price_per_share=transaction_data.price_per_share,
        direct_ownership=transaction_data.direct_ownership,
        ownership_nature_explanation=transaction_data.ownership_nature_explanation,
        transaction_timeliness=transaction_data.transaction_timeliness,
        footnote_ids=transaction_data.footnote_ids,
        acquisition_disposition_flag=transaction_data.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_data.is_part_of_group_filing
    )

def convert_non_derivative_transaction_orm_to_data(transaction_orm: NonDerivativeTransaction) -> NonDerivativeTransactionData:
    """Convert NonDerivativeTransaction ORM model to NonDerivativeTransactionData dataclass"""
    return NonDerivativeTransactionData(
        id=str(transaction_orm.id),
        filing_id=str(transaction_orm.form4_filing_id),
        relationship_id=str(transaction_orm.relationship_id),
        security_id=str(transaction_orm.security_id),
        transaction_code=transaction_orm.transaction_code,
        transaction_date=transaction_orm.transaction_date,
        transaction_form_type=transaction_orm.transaction_form_type,
        shares_amount=transaction_orm.shares_amount,
        price_per_share=transaction_orm.price_per_share,
        direct_ownership=transaction_orm.direct_ownership,
        ownership_nature_explanation=transaction_orm.ownership_nature_explanation,
        transaction_timeliness=transaction_orm.transaction_timeliness,
        footnote_ids=transaction_orm.footnote_ids or [],
        acquisition_disposition_flag=transaction_orm.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_orm.is_part_of_group_filing
    )

def convert_derivative_transaction_data_to_orm(transaction_data: DerivativeTransactionData) -> DerivativeTransaction:
    """Convert DerivativeTransactionData dataclass to DerivativeTransaction ORM model"""
    return DerivativeTransaction(
        id=uuid.UUID(transaction_data.id) if transaction_data.id else None,
        form4_filing_id=uuid.UUID(transaction_data.filing_id) if transaction_data.filing_id else None,
        relationship_id=uuid.UUID(transaction_data.relationship_id),
        security_id=uuid.UUID(transaction_data.security_id),
        derivative_security_id=uuid.UUID(transaction_data.derivative_security_id),
        transaction_code=transaction_data.transaction_code,
        transaction_date=transaction_data.transaction_date,
        transaction_form_type=transaction_data.transaction_form_type,
        derivative_shares_amount=transaction_data.shares_amount,
        price_per_derivative=transaction_data.price_per_derivative,
        underlying_shares_amount=transaction_data.underlying_shares_amount,
        direct_ownership=transaction_data.direct_ownership,
        ownership_nature_explanation=transaction_data.ownership_nature_explanation,
        transaction_timeliness=transaction_data.transaction_timeliness,
        footnote_ids=transaction_data.footnote_ids,
        acquisition_disposition_flag=transaction_data.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_data.is_part_of_group_filing
    )

def convert_derivative_transaction_orm_to_data(transaction_orm: DerivativeTransaction) -> DerivativeTransactionData:
    """Convert DerivativeTransaction ORM model to DerivativeTransactionData dataclass"""
    return DerivativeTransactionData(
        id=str(transaction_orm.id),
        filing_id=str(transaction_orm.form4_filing_id),
        relationship_id=str(transaction_orm.relationship_id),
        security_id=str(transaction_orm.security_id),
        derivative_security_id=str(transaction_orm.derivative_security_id),
        transaction_code=transaction_orm.transaction_code,
        transaction_date=transaction_orm.transaction_date,
        transaction_form_type=transaction_orm.transaction_form_type,
        shares_amount=transaction_orm.derivative_shares_amount,
        price_per_derivative=transaction_orm.price_per_derivative,
        underlying_shares_amount=transaction_orm.underlying_shares_amount,
        direct_ownership=transaction_orm.direct_ownership,
        ownership_nature_explanation=transaction_orm.ownership_nature_explanation,
        transaction_timeliness=transaction_orm.transaction_timeliness,
        footnote_ids=transaction_orm.footnote_ids or [],
        acquisition_disposition_flag=transaction_orm.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_orm.is_part_of_group_filing
    )

# Position adapters - For Phase 3
def convert_position_data_to_orm(position_data: PositionData) -> RelationshipPosition:
    """Convert PositionData dataclass to RelationshipPosition ORM model"""
    return RelationshipPosition(
        id=uuid.UUID(position_data.id) if position_data.id else None,
        relationship_id=uuid.UUID(position_data.relationship_id),
        security_id=uuid.UUID(position_data.security_id),
        position_date=position_data.position_date,
        shares_amount=position_data.shares_amount,
        direct_ownership=position_data.direct_ownership,
        ownership_nature_explanation=position_data.ownership_nature_explanation,
        filing_id=uuid.UUID(position_data.filing_id) if position_data.filing_id else None,
        transaction_id=uuid.UUID(position_data.transaction_id) if position_data.transaction_id else None,
        is_position_only=position_data.is_position_only,
        position_type=position_data.position_type
    )

def convert_position_orm_to_data(position_orm: RelationshipPosition) -> PositionData:
    """Convert RelationshipPosition ORM model to PositionData dataclass"""
    return PositionData(
        id=str(position_orm.id),
        relationship_id=str(position_orm.relationship_id),
        security_id=str(position_orm.security_id),
        position_date=position_orm.position_date,
        shares_amount=position_orm.shares_amount,
        direct_ownership=position_orm.direct_ownership,
        ownership_nature_explanation=position_orm.ownership_nature_explanation,
        filing_id=str(position_orm.filing_id) if position_orm.filing_id else None,
        transaction_id=str(position_orm.transaction_id) if position_orm.transaction_id else None,
        is_position_only=position_orm.is_position_only,
        position_type=position_orm.position_type
    )