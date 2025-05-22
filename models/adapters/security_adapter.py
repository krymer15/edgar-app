# models/adapters/security_adapter.py
import uuid
from typing import List, Optional, Dict

from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.orm_models.forms.security_orm import Security
from models.orm_models.forms.derivative_security_orm import DerivativeSecurity

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