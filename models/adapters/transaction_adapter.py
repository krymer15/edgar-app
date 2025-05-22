# models/adapters/transaction_adapter.py
import uuid
from typing import List, Optional, Dict

from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from models.orm_models.forms.non_derivative_transaction_orm import NonDerivativeTransaction
from models.orm_models.forms.derivative_transaction_orm import DerivativeTransaction

def convert_non_derivative_transaction_data_to_orm(transaction_data: NonDerivativeTransactionData) -> NonDerivativeTransaction:
    """Convert NonDerivativeTransactionData dataclass to NonDerivativeTransaction ORM model"""
    return NonDerivativeTransaction(
        id=uuid.UUID(transaction_data.id) if transaction_data.id else None,
        form4_filing_id=uuid.UUID(transaction_data.form4_filing_id) if transaction_data.form4_filing_id else None,
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
        form4_filing_id=str(transaction_orm.form4_filing_id) if transaction_orm.form4_filing_id else None,
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
        footnote_ids=transaction_orm.footnote_ids if transaction_orm.footnote_ids else [],
        acquisition_disposition_flag=transaction_orm.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_orm.is_part_of_group_filing
    )

def convert_derivative_transaction_data_to_orm(transaction_data: DerivativeTransactionData) -> DerivativeTransaction:
    """Convert DerivativeTransactionData dataclass to DerivativeTransaction ORM model"""
    return DerivativeTransaction(
        id=uuid.UUID(transaction_data.id) if transaction_data.id else None,
        form4_filing_id=uuid.UUID(transaction_data.form4_filing_id) if transaction_data.form4_filing_id else None,
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
        form4_filing_id=str(transaction_orm.form4_filing_id) if transaction_orm.form4_filing_id else None,
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
        footnote_ids=transaction_orm.footnote_ids if transaction_orm.footnote_ids else [],
        acquisition_disposition_flag=transaction_orm.acquisition_disposition_flag,
        is_part_of_group_filing=transaction_orm.is_part_of_group_filing
    )