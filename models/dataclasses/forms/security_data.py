# models/dataclasses/forms/security_data.py
from dataclasses import dataclass
from typing import Optional
import uuid

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