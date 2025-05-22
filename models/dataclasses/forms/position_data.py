# models/dataclasses/forms/position_data.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from decimal import Decimal
import uuid

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