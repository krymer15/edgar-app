# services/forms/position_service.py
from typing import Optional, List, Tuple, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import date, timedelta
from decimal import Decimal
import uuid

from models.orm_models.forms.relationship_position_orm import RelationshipPosition
from models.orm_models.forms.derivative_security_orm import DerivativeSecurity
from models.dataclasses.forms.position_data import RelationshipPositionData
from models.adapters.position_adapter import (
    convert_position_data_to_orm,
    convert_position_orm_to_data
)
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from services.forms.transaction_service import TransactionService

class PositionService:
    """Service for managing Form 4 relationship positions"""
    
    def __init__(self, db_session: Session, transaction_service: Optional[TransactionService] = None):
        self.db_session = db_session
        self.transaction_service = transaction_service or TransactionService(db_session)
    
    def create_position(self, position_data: RelationshipPositionData) -> str:
        """Create a new relationship position"""
        position = convert_position_data_to_orm(position_data)
        self.db_session.add(position)
        self.db_session.flush()  # Generate ID without committing
        
        return str(position.id)
    
    def get_position(self, position_id: str) -> Optional[RelationshipPositionData]:
        """Get a position by ID"""
        position = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.id == position_id
        ).first()
        
        if not position:
            return None
        
        return convert_position_orm_to_data(position)
    
    def get_latest_position(self, relationship_id: str, security_id: str, 
                            derivative_security_id: Optional[str] = None, 
                            as_of_date: Optional[date] = None) -> Optional[RelationshipPositionData]:
        """Get the latest position for a relationship-security combination as of a specific date"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id,
            RelationshipPosition.security_id == security_id
        )
        
        if derivative_security_id:
            query = query.filter(RelationshipPosition.derivative_security_id == derivative_security_id)
        else:
            query = query.filter(RelationshipPosition.derivative_security_id.is_(None))
        
        if as_of_date:
            query = query.filter(RelationshipPosition.position_date <= as_of_date)
        
        position = query.order_by(desc(RelationshipPosition.position_date)).first()
        
        if not position:
            return None
        
        return convert_position_orm_to_data(position)
    
    def get_positions_for_relationship(self, relationship_id: str, 
                                     as_of_date: Optional[date] = None) -> List[RelationshipPositionData]:
        """Get all positions for a specific relationship"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id
        )
        
        if as_of_date:
            # Subquery to get the latest position for each security as of the date
            subquery = self.db_session.query(
                RelationshipPosition.security_id,
                RelationshipPosition.derivative_security_id,
                RelationshipPosition.direct_ownership,
                func.max(RelationshipPosition.position_date).label("max_date")
            ).filter(
                RelationshipPosition.relationship_id == relationship_id,
                RelationshipPosition.position_date <= as_of_date
            ).group_by(
                RelationshipPosition.security_id,
                RelationshipPosition.derivative_security_id,
                RelationshipPosition.direct_ownership
            ).subquery()
            
            # Join with the subquery to get the latest positions
            query = self.db_session.query(RelationshipPosition).join(
                subquery,
                and_(
                    RelationshipPosition.security_id == subquery.c.security_id,
                    RelationshipPosition.position_date == subquery.c.max_date,
                    RelationshipPosition.derivative_security_id == subquery.c.derivative_security_id,
                    RelationshipPosition.direct_ownership == subquery.c.direct_ownership
                )
            )
        
        positions = query.order_by(
            RelationshipPosition.position_date.desc(),
            RelationshipPosition.security_id,
            RelationshipPosition.derivative_security_id
        ).all()
        
        return [convert_position_orm_to_data(p) for p in positions]
    
    def get_positions_for_security(self, security_id: str, 
                                 as_of_date: Optional[date] = None) -> List[RelationshipPositionData]:
        """Get all positions for a specific security"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.security_id == security_id
        )
        
        if as_of_date:
            # Similar subquery approach for latest positions
            subquery = self.db_session.query(
                RelationshipPosition.relationship_id,
                RelationshipPosition.direct_ownership,
                func.max(RelationshipPosition.position_date).label("max_date")
            ).filter(
                RelationshipPosition.security_id == security_id,
                RelationshipPosition.position_date <= as_of_date
            ).group_by(
                RelationshipPosition.relationship_id,
                RelationshipPosition.direct_ownership
            ).subquery()
            
            query = self.db_session.query(RelationshipPosition).join(
                subquery,
                and_(
                    RelationshipPosition.relationship_id == subquery.c.relationship_id,
                    RelationshipPosition.position_date == subquery.c.max_date,
                    RelationshipPosition.direct_ownership == subquery.c.direct_ownership
                )
            )
        
        positions = query.order_by(
            RelationshipPosition.position_date.desc(),
            RelationshipPosition.relationship_id
        ).all()
        
        return [convert_position_orm_to_data(p) for p in positions]
    
    def update_position_from_transaction(self, transaction: Union[NonDerivativeTransactionData, DerivativeTransactionData]) -> str:
        """Create or update a position based on a transaction"""
        # Determine transaction type
        is_derivative = isinstance(transaction, DerivativeTransactionData)
        position_type = 'derivative' if is_derivative else 'equity'
        derivative_security_id = getattr(transaction, 'derivative_security_id', None) if is_derivative else None
        
        # Try to find the latest position
        latest_position = self.get_latest_position(
            relationship_id=transaction.relationship_id,
            security_id=transaction.security_id,
            derivative_security_id=derivative_security_id,
            as_of_date=transaction.transaction_date - timedelta(days=1)  # Latest position before transaction
        )
        
        # Calculate new position amount
        new_amount = transaction.position_impact
        if latest_position:
            new_amount += latest_position.shares_amount
        
        # Create new position
        position_data = RelationshipPositionData(
            relationship_id=transaction.relationship_id,
            security_id=transaction.security_id,
            position_date=transaction.transaction_date,
            shares_amount=new_amount,
            direct_ownership=transaction.direct_ownership,
            ownership_nature_explanation=transaction.ownership_nature_explanation,
            filing_id=transaction.form4_filing_id,
            transaction_id=transaction.id,
            is_position_only=False,
            position_type=position_type,
            derivative_security_id=derivative_security_id
        )
        
        return self.create_position(position_data)
    
    def create_position_only_entry(self, position_data: RelationshipPositionData) -> str:
        """Create a position-only entry (from a holding without transaction)"""
        # Set position-only flag
        position_data.is_position_only = True
        
        # Check for duplicate position-only entries
        existing = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == position_data.relationship_id,
            RelationshipPosition.security_id == position_data.security_id,
            RelationshipPosition.position_date == position_data.position_date,
            RelationshipPosition.derivative_security_id == (
                uuid.UUID(position_data.derivative_security_id) 
                if position_data.derivative_security_id else None
            ),
            RelationshipPosition.direct_ownership == position_data.direct_ownership,
            RelationshipPosition.is_position_only == True
        ).first()
        
        if existing:
            # Update existing entry
            existing.shares_amount = position_data.shares_amount
            existing.ownership_nature_explanation = position_data.ownership_nature_explanation
            existing.filing_id = uuid.UUID(position_data.filing_id)
            self.db_session.flush()
            return str(existing.id)
        
        # Create new position
        return self.create_position(position_data)
    
    def get_position_history(self, relationship_id: str, security_id: str,
                           derivative_security_id: Optional[str] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[RelationshipPositionData]:
        """Get position history for a relationship-security combination"""
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id,
            RelationshipPosition.security_id == security_id
        )
        
        if derivative_security_id:
            query = query.filter(RelationshipPosition.derivative_security_id == derivative_security_id)
        else:
            query = query.filter(RelationshipPosition.derivative_security_id.is_(None))
        
        if start_date:
            query = query.filter(RelationshipPosition.position_date >= start_date)
        
        if end_date:
            query = query.filter(RelationshipPosition.position_date <= end_date)
        
        positions = query.order_by(RelationshipPosition.position_date).all()
        
        return [convert_position_orm_to_data(p) for p in positions]
    
    def calculate_total_shares_owned(self, relationship_id: str, 
                                   as_of_date: Optional[date] = None) -> Dict[str, Decimal]:
        """Calculate total shares owned per security for a relationship"""
        positions = self.get_positions_for_relationship(relationship_id, as_of_date)
        
        # Group by security_id and sum shares
        totals = {}
        for position in positions:
            security_id = position.security_id
            if security_id not in totals:
                totals[security_id] = Decimal('0')
            
            totals[security_id] += position.shares_amount
        
        return totals
    
    def recalculate_positions(self, relationship_id: str, security_id: str,
                            start_date: Optional[date] = None) -> None:
        """Recalculate positions for a relationship-security combination"""
        # Get transactions in chronological order
        if start_date:
            non_derivative = self.transaction_service.get_transactions_for_security(
                security_id, start_date=start_date
            )
            
            # Also get derivative transactions if applicable
            derivative = []
            derivative_securities = self.db_session.query(DerivativeSecurity).filter(
                DerivativeSecurity.underlying_security_id == security_id
            ).all()
            
            for deriv_sec in derivative_securities:
                deriv_txs = self.transaction_service.get_transactions_for_derivative_security(
                    str(deriv_sec.id), start_date=start_date
                )
                derivative.extend(deriv_txs)
        else:
            # Get all transactions for the relationship
            non_derivative, derivative = self.transaction_service.get_transactions_for_relationship(relationship_id)
            
            # Filter by security_id
            non_derivative = [tx for tx in non_derivative if tx.security_id == security_id]
            derivative = [tx for tx in derivative if tx.security_id == security_id]
        
        # Combine and sort by date
        all_transactions = []
        all_transactions.extend(non_derivative)
        all_transactions.extend(derivative)
        all_transactions.sort(key=lambda tx: tx.transaction_date)
        
        # Delete existing positions that will be recalculated
        query = self.db_session.query(RelationshipPosition).filter(
            RelationshipPosition.relationship_id == relationship_id,
            RelationshipPosition.security_id == security_id,
            RelationshipPosition.is_position_only == False
        )
        
        if start_date:
            query = query.filter(RelationshipPosition.position_date >= start_date)
            
        query.delete(synchronize_session=False)
        
        # Process transactions in order
        for transaction in all_transactions:
            if transaction.relationship_id == relationship_id:
                self.update_position_from_transaction(transaction)
        
        self.db_session.flush()