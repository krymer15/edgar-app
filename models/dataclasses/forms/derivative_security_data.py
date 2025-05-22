# models/dataclasses/forms/derivative_security_data.py
from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal
import uuid

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
            
        # Convert numeric values to Decimal if provided as float/int
        if isinstance(self.conversion_price, (float, int)):
            self.conversion_price = Decimal(str(self.conversion_price))