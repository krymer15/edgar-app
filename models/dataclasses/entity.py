# models/dataclasses/entity.py

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class EntityData:
    """
    Entity dataclass representing a company, person, trust, or other entity in SEC filings.
    - Used for in-memory representation before database storage
    - Represents both issuers and reporting owners
    """
    # Core fields
    cik: str
    name: str
    entity_type: str  # 'company', 'person', 'trust', 'group'

    # Optional fields
    id: UUID = field(default_factory=uuid4)  # Use default_factory for new instances
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Metadata - not stored in database but useful for tracking
    source_accession: Optional[str] = None

    def __post_init__(self):
        # Normalize CIK (remove leading zeros, special characters)
        self.cik = self.cik.lstrip('0').strip()

        # Validate entity_type
        valid_types = ('company', 'person', 'trust', 'group')
        if self.entity_type not in valid_types:
            raise ValueError(f"Entity type must be one of {valid_types}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': str(self.id) if self.id else None,
            'cik': self.cik,
            'name': self.name,
            'entity_type': self.entity_type
        }