# models/dataclasses/forms/form4_filing.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID, uuid4

from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.form4_transaction import Form4TransactionData

@dataclass
class Form4FilingData:
    """
    Form4FilingData represents the top-level form 4 filing information.
    It serves as the container for relationships and transactions.
    """
    # Required core fields
    accession_number: str

    # Optional fields
    period_of_report: Optional[date] = None
    has_multiple_owners: bool = False

    # Collection fields - populated during processing
    relationships: List[Form4RelationshipData] = field(default_factory=list)
    transactions: List[Form4TransactionData] = field(default_factory=list)

    # Raw content fields - optional for storage/debugging
    raw_header: Optional[str] = None
    raw_xml: Optional[str] = None

    # Database tracking fields
    id: UUID = field(default_factory=uuid4)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Normalize accession number
        self.accession_number = self.accession_number.strip().replace('-', '')

        # Determine if this has multiple owners based on relationships
        if len(self.relationships) > 1:
            self.has_multiple_owners = True

    def add_relationship(self, relationship: Form4RelationshipData) -> None:
        """Add a relationship to this filing"""
        relationship.form4_filing_id = self.id
        self.relationships.append(relationship)

        # Update multiple owners flag
        if len(self.relationships) > 1:
            self.has_multiple_owners = True

    def add_transaction(self, transaction: Form4TransactionData, relationship_id: Optional[UUID] = None) -> None:
        """
        Add a transaction to this filing and associate it with a relationship
        if relationship_id is None and only one relationship exists, it will be associated with that
        """
        transaction.form4_filing_id = self.id

        if relationship_id:
            transaction.relationship_id = relationship_id
        elif len(self.relationships) == 1:
            transaction.relationship_id = self.relationships[0].id

        self.transactions.append(transaction)

    def get_transactions_by_relationship(self, relationship_id: UUID) -> List[Form4TransactionData]:
        """Get all transactions for a specific relationship"""
        return [t for t in self.transactions if t.relationship_id == relationship_id]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': str(self.id),
            'accession_number': self.accession_number,
            'period_of_report': self.period_of_report.isoformat() if self.period_of_report else None,
            'has_multiple_owners': self.has_multiple_owners,
            'relationships_count': len(self.relationships),
            'transactions_count': len(self.transactions),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_full_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including all relationships and transactions"""
        result = self.to_dict()
        result['relationships'] = [r.to_dict() for r in self.relationships]
        result['transactions'] = [t.to_dict() for t in self.transactions]
        return result