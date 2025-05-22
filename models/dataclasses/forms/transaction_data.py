# models/dataclasses/forms/transaction_data.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from decimal import Decimal
import uuid

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
    form4_filing_id: Optional[str] = None
    id: Optional[str] = None
    is_part_of_group_filing: bool = False
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
            
        # Validate acquisition_disposition_flag
        if self.acquisition_disposition_flag not in ['A', 'D']:
            raise ValueError(f"Invalid acquisition_disposition_flag: {self.acquisition_disposition_flag}. Must be 'A' or 'D'")
    
        # Ensure transaction_date is not None
        if self.transaction_date is None:
            raise ValueError("transaction_date is required for transactions")
            
        # Ensure ownership explanation is provided for indirect ownership
        if not self.direct_ownership and not self.ownership_nature_explanation:
            # Not setting as error, but flagging in log would be appropriate
            pass
            
        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.shares_amount, (float, int)):
            self.shares_amount = Decimal(str(self.shares_amount))
    
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
    
    def __post_init__(self):
        super().__post_init__()
        
        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.price_per_share, (float, int)):
            self.price_per_share = Decimal(str(self.price_per_share))
    
    @property
    def transaction_value(self) -> Optional[Decimal]:
        """Calculate the total value of the transaction if possible"""
        if self.shares_amount is not None and self.price_per_share is not None:
            return self.shares_amount * self.price_per_share
        return None


@dataclass
class DerivativeTransactionData(TransactionBase):
    """Data for derivative transactions"""
    derivative_security_id: str = field(default=None)  # Using field with metadata
    price_per_derivative: Optional[Decimal] = None
    underlying_shares_amount: Optional[Decimal] = None
    
    def __post_init__(self):
        super().__post_init__()
        
        # Validate derivative_security_id is present and not None
        if self.derivative_security_id is None:
            raise ValueError("derivative_security_id is required for derivative transactions")
            
        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.price_per_derivative, (float, int)):
            self.price_per_derivative = Decimal(str(self.price_per_derivative))
            
        if isinstance(self.underlying_shares_amount, (float, int)):
            self.underlying_shares_amount = Decimal(str(self.underlying_shares_amount))
    
    # Override shares_amount to rename to derivative_shares_amount for clarity
    @property
    def derivative_shares_amount(self) -> Decimal:
        return self.shares_amount
        
    @derivative_shares_amount.setter
    def derivative_shares_amount(self, value: Decimal):
        self.shares_amount = value
        
    @property
    def transaction_value(self) -> Optional[Decimal]:
        """Calculate the total value of the transaction if possible"""
        if self.shares_amount is not None and self.price_per_derivative is not None:
            return self.shares_amount * self.price_per_derivative
        return None