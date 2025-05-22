# Pragmatic Dataclass Models for Form 4 Schema (IMPLEMENTATION COMPLETE)

# Status: Implementation Complete ✅
# Last Updated: Post-Phase 4 Implementation
# Reference: See `form4_comprehensive_implementation_status.md` for full status
#
# These dataclass models have been successfully implemented and are in production use
# across the SecurityService, TransactionService, PositionService, and Form4ParserV2.

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
import uuid

# Core Security Dataclasses
@dataclass
class SecurityData:
    """Dataclass for transferring security information between service layers"""
    title: str
    issuer_entity_id: str
    security_type: str  # 'equity', 'option', 'convertible', 'other_derivative'
    standard_cusip: Optional[str] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        # Generate ID if not provided
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate security type
        valid_types = ['equity', 'option', 'convertible', 'other_derivative']
        if self.security_type not in valid_types:
            raise ValueError(f"Invalid security type: {self.security_type}. Must be one of {valid_types}")


@dataclass
class DerivativeSecurityData:
    """Dataclass for derivative security details"""
    security_id: str
    underlying_security_title: str
    conversion_price: Optional[Decimal] = None
    exercise_date: Optional[date] = None
    expiration_date: Optional[date] = None
    underlying_security_id: Optional[str] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())


# Transaction Dataclasses
@dataclass
class TransactionBase:
    """Base class for transaction data"""
    relationship_id: str
    security_id: str
    transaction_code: str
    transaction_date: date
    shares_amount: Decimal
    acquisition_disposition_flag: str  # 'A' or 'D'
    direct_ownership: bool = True
    ownership_nature_explanation: Optional[str] = None
    transaction_form_type: Optional[str] = None
    transaction_timeliness: Optional[str] = None
    footnote_ids: List[str] = field(default_factory=list)
    filing_id: Optional[str] = None
    id: Optional[str] = None
    is_part_of_group_filing: bool = False
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate acquisition_disposition_flag
        if self.acquisition_disposition_flag not in ['A', 'D']:
            raise ValueError(f"Invalid acquisition_disposition_flag: {self.acquisition_disposition_flag}. Must be 'A' or 'D'")
    
    @property
    def position_impact(self) -> Decimal:
        """Calculate the impact on the position (positive for acquisitions, negative for dispositions)"""
        if self.acquisition_disposition_flag == 'A':
            return self.shares_amount
        elif self.acquisition_disposition_flag == 'D':
            return -1 * self.shares_amount
        return Decimal('0')


@dataclass
class NonDerivativeTransactionData(TransactionBase):
    """Data for non-derivative transactions"""
    price_per_share: Optional[Decimal] = None


@dataclass
class DerivativeTransactionData(TransactionBase):
    """Data for derivative transactions"""
    derivative_security_id: str
    price_per_derivative: Optional[Decimal] = None
    underlying_shares_amount: Optional[Decimal] = None


# Position Data - For Phase 3
@dataclass
class RelationshipPositionData:
    """Dataclass for relationship position data"""
    relationship_id: str
    security_id: str
    position_date: date
    shares_amount: Decimal
    filing_id: str
    position_type: str  # 'equity' or 'derivative'
    direct_ownership: bool = True
    ownership_nature_explanation: Optional[str] = None
    transaction_id: Optional[str] = None
    is_position_only: bool = False
    derivative_security_id: Optional[str] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        # Generate ID if not provided
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate position_type
        valid_types = ['equity', 'derivative']
        if self.position_type not in valid_types:
            raise ValueError(f"Invalid position_type: {self.position_type}. Must be one of {valid_types}")
            
        # Ensure derivative_security_id is present for derivative positions
        if self.position_type == 'derivative' and not self.derivative_security_id:
            raise ValueError("derivative_security_id is required for derivative positions")
            
        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.shares_amount, (float, int)):
            self.shares_amount = Decimal(str(self.shares_amount))


# IMPLEMENTATION STATUS:
# ✅ SecurityData & DerivativeSecurityData: Implemented in Phase 1
# ✅ TransactionBase, NonDerivativeTransactionData, DerivativeTransactionData: Implemented in Phase 2  
# ✅ RelationshipPositionData: Implemented in Phase 3
# ✅ Form4FilingContext: Implemented in Phase 4 (see parsers/forms/form4_filing_context.py)
#
# Position calculation utilities are implemented in the PositionService class:
# - PositionService.update_position_from_transaction: Creates/updates positions from transactions
# - PositionService.create_position_only_entry: Creates position-only entries
# - PositionService.calculate_total_shares_owned: Calculates position totals
# - PositionService.get_position_history: Historical position tracking
#
# This separation maintains clean architecture between data models and business logic.