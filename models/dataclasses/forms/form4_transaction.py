# models/dataclasses/forms/form4_transaction.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID, uuid4
from decimal import Decimal

@dataclass
class Form4TransactionData:
    """
    Form4TransactionData represents a transaction reported in a Form 4 filing.
    Each transaction belongs to a specific relationship between an issuer and owner.
    """
    # Required core fields
    security_title: str
    transaction_date: date
    transaction_code: str

    # Transaction details
    shares_amount: Optional[Decimal] = None
    price_per_share: Optional[Decimal] = None
    ownership_nature: Optional[str] = None  # 'D' for Direct or 'I' for Indirect
    indirect_ownership_explanation: Optional[str] = None
    transaction_form_type: Optional[str] = None
    is_derivative: bool = False
    equity_swap_involved: bool = False
    transaction_timeliness: Optional[str] = None
    footnote_ids: List[str] = field(default_factory=list)

    # Derivative-specific fields
    conversion_price: Optional[Decimal] = None
    exercise_date: Optional[date] = None
    expiration_date: Optional[date] = None

    # Relationship fields
    form4_filing_id: Optional[UUID] = None
    relationship_id: Optional[UUID] = None

    # Database tracking fields
    id: UUID = field(default_factory=uuid4)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Validate ownership_nature
        if self.ownership_nature and self.ownership_nature not in ('D', 'I'):
            raise ValueError("ownership_nature must be 'D' for Direct or 'I' for Indirect")

        # Ensure indirect ownership explanation is provided when needed
        if self.ownership_nature == 'I' and not self.indirect_ownership_explanation:
            # Not setting as error, but flagging in log would be appropriate
            pass

        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.shares_amount, (float, int)):
            self.shares_amount = Decimal(str(self.shares_amount))

        if isinstance(self.price_per_share, (float, int)):
            self.price_per_share = Decimal(str(self.price_per_share))

        if isinstance(self.conversion_price, (float, int)):
            self.conversion_price = Decimal(str(self.conversion_price))

    @property
    def is_purchase(self) -> bool:
        """Helper method to determine if this is a purchase transaction"""
        return self.transaction_code in ('P', 'A')

    @property
    def is_sale(self) -> bool:
        """Helper method to determine if this is a sale transaction"""
        return self.transaction_code in ('S', 'D')

    @property
    def transaction_value(self) -> Optional[Decimal]:
        """Calculate the total value of the transaction if possible"""
        if self.shares_amount is not None and self.price_per_share is not None:
            return self.shares_amount * self.price_per_share
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': str(self.id),
            'security_title': self.security_title,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'transaction_code': self.transaction_code,
            'shares_amount': str(self.shares_amount) if self.shares_amount else None,
            'price_per_share': str(self.price_per_share) if self.price_per_share else None,
            'ownership_nature': self.ownership_nature,
            'indirect_ownership_explanation': self.indirect_ownership_explanation,
            'transaction_form_type': self.transaction_form_type,
            'is_derivative': self.is_derivative,
            'equity_swap_involved': self.equity_swap_involved,
            'transaction_timeliness': self.transaction_timeliness,
            'footnote_ids': self.footnote_ids,
            'conversion_price': str(self.conversion_price) if self.conversion_price else None,
            'exercise_date': self.exercise_date.isoformat() if self.exercise_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'form4_filing_id': str(self.form4_filing_id) if self.form4_filing_id else None,
            'relationship_id': str(self.relationship_id) if self.relationship_id else None,
            'transaction_value': str(self.transaction_value) if self.transaction_value is not None else None
        }