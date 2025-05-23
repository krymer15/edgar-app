# models/dataclasses/forms/form4_relationship.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID, uuid4
from decimal import Decimal

@dataclass
class Form4RelationshipData:
    """
    Form4Relationship dataclass representing the relationship between
    an issuer entity and a reporting owner in Form 4 filings.
    
    This includes the total_shares_owned field (Bug 11 fix) which aggregates 
    all related transaction amounts to provide the total shares owned by the reporting owner.
    """
    # Required core fields
    issuer_entity_id: UUID  # References Entity
    owner_entity_id: UUID   # References Entity
    filing_date: date

    # Relationship metadata
    is_director: bool = False
    is_officer: bool = False
    is_ten_percent_owner: bool = False
    is_other: bool = False
    officer_title: Optional[str] = None
    other_text: Optional[str] = None
    is_group_filing: bool = False

    # Internal fields
    form4_filing_id: Optional[UUID] = None
    relationship_type: str = "unknown"  # 'director', 'officer', '10_percent_owner', 'other'
    relationship_details: Optional[Dict[str, Any]] = None
    
    # Bug 11 Fix: Add total shares owned field
    total_shares_owned: Optional[Decimal] = None  # Calculated from all related transactions

    # Database tracking fields
    id: UUID = field(default_factory=uuid4)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Determine relationship_type based on boolean flags
        if self.is_director:
            self.relationship_type = "director"
        elif self.is_officer:
            self.relationship_type = "officer"
        elif self.is_ten_percent_owner:
            self.relationship_type = "10_percent_owner"
        elif self.is_other:
            self.relationship_type = "other"

        # Validate relationship_type
        valid_types = ('director', 'officer', '10_percent_owner', 'other', 'unknown')
        if self.relationship_type not in valid_types:
            raise ValueError(f"Relationship type must be one of {valid_types}")

        # If no relationship type is specified, default to "other" instead of raising an error
        if not any([self.is_director, self.is_officer, self.is_ten_percent_owner, self.is_other]):
            self.is_other = True
            self.other_text = "Form 4 Filer"
            self.relationship_type = "other"

        # Ensure officer_title is present for officers
        if self.is_officer and not self.officer_title:
            self.officer_title = "Officer"  # Default value if not specified

        # Ensure other_text is present for 'other' type
        if self.is_other and not self.other_text:
            raise ValueError("other_text must be provided when is_other is True")
            
        # Convert total_shares_owned to Decimal if provided as float/int
        if isinstance(self.total_shares_owned, (float, int)):
            self.total_shares_owned = Decimal(str(self.total_shares_owned))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': str(self.id),
            'issuer_entity_id': str(self.issuer_entity_id),
            'owner_entity_id': str(self.owner_entity_id),
            'filing_date': self.filing_date.isoformat() if self.filing_date else None,
            'form4_filing_id': str(self.form4_filing_id) if self.form4_filing_id else None,
            'relationship_type': self.relationship_type,
            'is_director': self.is_director,
            'is_officer': self.is_officer,
            'is_ten_percent_owner': self.is_ten_percent_owner,
            'is_other': self.is_other,
            'officer_title': self.officer_title,
            'other_text': self.other_text,
            'is_group_filing': self.is_group_filing,
            'relationship_details': self.relationship_details,
            'total_shares_owned': str(self.total_shares_owned) if self.total_shares_owned is not None else None
        }