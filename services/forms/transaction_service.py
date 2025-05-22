# services/forms/transaction_service.py
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from decimal import Decimal

from models.orm_models.forms.non_derivative_transaction_orm import NonDerivativeTransaction
from models.orm_models.forms.derivative_transaction_orm import DerivativeTransaction
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from models.adapters.transaction_adapter import (
    convert_non_derivative_transaction_data_to_orm,
    convert_non_derivative_transaction_orm_to_data,
    convert_derivative_transaction_data_to_orm,
    convert_derivative_transaction_orm_to_data
)
from services.forms.security_service import SecurityService

class TransactionService:
    """Service for managing Form 4 transactions"""
    
    def __init__(self, db_session: Session, security_service: Optional[SecurityService] = None):
        self.db_session = db_session
        self.security_service = security_service or SecurityService(db_session)
    
    def create_non_derivative_transaction(self, transaction_data: NonDerivativeTransactionData) -> str:
        """Create a new non-derivative transaction"""
        transaction = convert_non_derivative_transaction_data_to_orm(transaction_data)
        self.db_session.add(transaction)
        self.db_session.flush()  # Generate ID without committing
        
        return str(transaction.id)
    
    def create_derivative_transaction(self, transaction_data: DerivativeTransactionData) -> str:
        """Create a new derivative transaction"""
        transaction = convert_derivative_transaction_data_to_orm(transaction_data)
        self.db_session.add(transaction)
        self.db_session.flush()  # Generate ID without committing
        
        return str(transaction.id)
    
    def get_non_derivative_transaction(self, transaction_id: str) -> Optional[NonDerivativeTransactionData]:
        """Get a non-derivative transaction by ID"""
        transaction = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return None
        
        return convert_non_derivative_transaction_orm_to_data(transaction)
    
    def get_derivative_transaction(self, transaction_id: str) -> Optional[DerivativeTransactionData]:
        """Get a derivative transaction by ID"""
        transaction = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return None
        
        return convert_derivative_transaction_orm_to_data(transaction)
    
    def get_transactions_for_filing(self, filing_id: str) -> Tuple[List[NonDerivativeTransactionData], List[DerivativeTransactionData]]:
        """Get all transactions for a specific filing"""
        non_derivative = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.form4_filing_id == filing_id
        ).all()
        
        derivative = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.form4_filing_id == filing_id
        ).all()
        
        return (
            [convert_non_derivative_transaction_orm_to_data(t) for t in non_derivative],
            [convert_derivative_transaction_orm_to_data(t) for t in derivative]
        )
    
    def get_transactions_for_relationship(self, relationship_id: str) -> Tuple[List[NonDerivativeTransactionData], List[DerivativeTransactionData]]:
        """Get all transactions for a specific relationship"""
        non_derivative = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.relationship_id == relationship_id
        ).all()
        
        derivative = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.relationship_id == relationship_id
        ).all()
        
        return (
            [convert_non_derivative_transaction_orm_to_data(t) for t in non_derivative],
            [convert_derivative_transaction_orm_to_data(t) for t in derivative]
        )
    
    def get_transactions_for_security(self, security_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[NonDerivativeTransactionData]:
        """Get all non-derivative transactions for a specific security"""
        query = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.security_id == security_id
        )
        
        if start_date:
            query = query.filter(NonDerivativeTransaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(NonDerivativeTransaction.transaction_date <= end_date)
        
        transactions = query.order_by(NonDerivativeTransaction.transaction_date).all()
        
        return [convert_non_derivative_transaction_orm_to_data(t) for t in transactions]
    
    def get_transactions_for_derivative_security(self, derivative_security_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[DerivativeTransactionData]:
        """Get all derivative transactions for a specific derivative security"""
        query = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.derivative_security_id == derivative_security_id
        )
        
        if start_date:
            query = query.filter(DerivativeTransaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(DerivativeTransaction.transaction_date <= end_date)
        
        transactions = query.order_by(DerivativeTransaction.transaction_date).all()
        
        return [convert_derivative_transaction_orm_to_data(t) for t in transactions]
    
    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> Tuple[List[NonDerivativeTransactionData], List[DerivativeTransactionData]]:
        """Get all transactions within a date range"""
        non_derivative = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.transaction_date >= start_date,
            NonDerivativeTransaction.transaction_date <= end_date
        ).order_by(NonDerivativeTransaction.transaction_date).all()
        
        derivative = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.transaction_date >= start_date,
            DerivativeTransaction.transaction_date <= end_date
        ).order_by(DerivativeTransaction.transaction_date).all()
        
        return (
            [convert_non_derivative_transaction_orm_to_data(t) for t in non_derivative],
            [convert_derivative_transaction_orm_to_data(t) for t in derivative]
        )
    
    def update_non_derivative_transaction(self, transaction_id: str, transaction_data: NonDerivativeTransactionData) -> bool:
        """Update an existing non-derivative transaction"""
        transaction = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return False
        
        # Update fields
        transaction.relationship_id = transaction_data.relationship_id
        transaction.security_id = transaction_data.security_id
        transaction.transaction_code = transaction_data.transaction_code
        transaction.transaction_date = transaction_data.transaction_date
        transaction.transaction_form_type = transaction_data.transaction_form_type
        transaction.shares_amount = transaction_data.shares_amount
        transaction.price_per_share = transaction_data.price_per_share
        transaction.direct_ownership = transaction_data.direct_ownership
        transaction.ownership_nature_explanation = transaction_data.ownership_nature_explanation
        transaction.transaction_timeliness = transaction_data.transaction_timeliness
        transaction.footnote_ids = transaction_data.footnote_ids
        transaction.acquisition_disposition_flag = transaction_data.acquisition_disposition_flag
        transaction.is_part_of_group_filing = transaction_data.is_part_of_group_filing
        
        self.db_session.flush()
        return True
    
    def update_derivative_transaction(self, transaction_id: str, transaction_data: DerivativeTransactionData) -> bool:
        """Update an existing derivative transaction"""
        transaction = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return False
        
        # Update fields
        transaction.relationship_id = transaction_data.relationship_id
        transaction.security_id = transaction_data.security_id
        transaction.derivative_security_id = transaction_data.derivative_security_id
        transaction.transaction_code = transaction_data.transaction_code
        transaction.transaction_date = transaction_data.transaction_date
        transaction.transaction_form_type = transaction_data.transaction_form_type
        transaction.derivative_shares_amount = transaction_data.shares_amount
        transaction.price_per_derivative = transaction_data.price_per_derivative
        transaction.underlying_shares_amount = transaction_data.underlying_shares_amount
        transaction.direct_ownership = transaction_data.direct_ownership
        transaction.ownership_nature_explanation = transaction_data.ownership_nature_explanation
        transaction.transaction_timeliness = transaction_data.transaction_timeliness
        transaction.footnote_ids = transaction_data.footnote_ids
        transaction.acquisition_disposition_flag = transaction_data.acquisition_disposition_flag
        transaction.is_part_of_group_filing = transaction_data.is_part_of_group_filing
        
        self.db_session.flush()
        return True
    
    def delete_non_derivative_transaction(self, transaction_id: str) -> bool:
        """Delete a non-derivative transaction"""
        transaction = self.db_session.query(NonDerivativeTransaction).filter(
            NonDerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return False
        
        self.db_session.delete(transaction)
        self.db_session.flush()
        return True
    
    def delete_derivative_transaction(self, transaction_id: str) -> bool:
        """Delete a derivative transaction"""
        transaction = self.db_session.query(DerivativeTransaction).filter(
            DerivativeTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            return False
        
        self.db_session.delete(transaction)
        self.db_session.flush()
        return True