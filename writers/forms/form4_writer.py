# writers/forms/form4_writer.py
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.form4_transaction import Form4TransactionData
from models.orm_models.forms.form4_filing_orm import Form4Filing
from models.orm_models.forms.form4_relationship_orm import Form4Relationship
from models.orm_models.forms.form4_transaction_orm import Form4Transaction
from writers.shared.entity_writer import EntityWriter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from utils.report_logger import log_info, log_warn, log_error
from utils.accession_formatter import format_for_db
from models.dataclasses.entity import EntityData
from typing import Dict, Optional, List, Any
import uuid

class Form4Writer:
    """
    Writer for Form 4 data to the database.
    Handles saving entities, relationships, and transactions.
    """
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.entity_writer = EntityWriter(db_session)
        
    def _extract_cik_from_accession(self, accession_number: str) -> str:
        """Extract CIK from accession number - first 10 digits"""
        # Remove any dashes
        clean_acc = accession_number.replace('-', '')
        # The first 10 digits are the CIK
        if len(clean_acc) >= 10:
            return clean_acc[:10]
        return "0000000000"  # Fallback

    def write_form4_data(self, form4_data: Form4FilingData) -> Optional[Form4Filing]:
        """
        Write Form 4 data to the database.

        Args:
            form4_data: Form4FilingData object

        Returns:
            Form4Filing ORM instance if successful, None otherwise
        """
        try:
            # Format the accession number for database (with dashes)
            db_accession_number = format_for_db(form4_data.accession_number)
            
            # Check if form4 filing already exists
            existing_filing = self.db_session.query(Form4Filing).filter_by(
                accession_number=db_accession_number
            ).first()

            if existing_filing:
                log_info(f"Form 4 filing already exists for {db_accession_number}, updating")
                # Delete existing relationships and transactions for clean update
                self._delete_existing_data(existing_filing.id)
                form4_filing = existing_filing

                # Update filing details
                form4_filing.period_of_report = form4_data.period_of_report
                form4_filing.has_multiple_owners = form4_data.has_multiple_owners
            else:
                # Create new Form 4 filing
                form4_filing = Form4Filing(
                    accession_number=db_accession_number,
                    period_of_report=form4_data.period_of_report,
                    has_multiple_owners=form4_data.has_multiple_owners
                )

                self.db_session.add(form4_filing)
                self.db_session.flush()  # Get ID without committing
                log_info(f"Created new Form 4 filing record for {db_accession_number}")

            # Process relationships and transactions
            self._write_relationships_and_transactions(form4_data, form4_filing)

            # Commit all changes
            self.db_session.commit()
            log_info(f"Successfully wrote Form 4 data for {db_accession_number}")

            return form4_filing

        except SQLAlchemyError as e:
            log_error(f"Error writing Form 4 data: {e}")
            self.db_session.rollback()
            return None

    def _delete_existing_data(self, form4_filing_id: uuid.UUID) -> None:
        """Delete existing relationships and transactions for a Form 4 filing"""
        try:
            # First delete transactions (due to foreign key constraints)
            self.db_session.query(Form4Transaction).filter_by(
                form4_filing_id=form4_filing_id
            ).delete()

            # Then delete relationships
            self.db_session.query(Form4Relationship).filter_by(
                form4_filing_id=form4_filing_id
            ).delete()

            log_info(f"Deleted existing relationships and transactions for Form 4 filing {form4_filing_id}")
        except SQLAlchemyError as e:
            log_error(f"Error deleting existing Form 4 data: {e}")
            raise

    def _write_relationships_and_transactions(self, form4_data: Form4FilingData, form4_filing: Form4Filing) -> None:
        """Write relationships and transactions for a Form 4 filing"""
        # Track relationship mappings (from dataclass ID to ORM object)
        relationship_map = {}

        # Process relationships
        for idx, rel_data in enumerate(form4_data.relationships):
            # Get entity objects from form4_data if available, or fetch from DB
            if hasattr(form4_data, 'issuer_entity') and hasattr(form4_data, 'owner_entity'):
                # Use the entity objects from form4_data if available (mainly for tests)
                issuer_entity = self.entity_writer.get_or_create_entity(form4_data.issuer_entity)
                owner_entity = self.entity_writer.get_or_create_entity(form4_data.owner_entity)
            else:
                # Need to get or create entity records first from Form4SgmlIndexer data
                # Parse CIK out of the accession number (first 10 digits)
                issuer_id = rel_data.issuer_entity_id
                owner_id = rel_data.owner_entity_id
                
                log_info(f"Retrieving entity information by ID for relationship")
                log_info(f"Using issuer_entity_id: {issuer_id}, owner_entity_id: {owner_id}")
                
                # Create dummy EntityData objects since we need to save them to the DB
                issuer_cik = self._extract_cik_from_accession(form4_data.accession_number)
                issuer_entity_data = EntityData(
                    cik=issuer_cik,
                    name=f"Issuer CIK {issuer_cik}",
                    entity_type="company",
                    id=issuer_id  # Use the same ID from the relationship
                )
                
                # Reporting owner CIK will just be a generated ID for now
                owner_entity_data = EntityData(
                    cik=f"owner_{str(owner_id)[-6:]}",  # Use last 6 chars of ID as a unique identifier
                    name=f"Owner ID {str(owner_id)[-6:]}",
                    entity_type="person",
                    id=owner_id  # Use the same ID from the relationship
                )
                
                # Create entities in the database
                issuer_entity = self.entity_writer.get_or_create_entity(issuer_entity_data)
                owner_entity = self.entity_writer.get_or_create_entity(owner_entity_data)
                
                # Commit the entities explicitly to ensure they're in the database
                # before creating relationships that reference them
                self.db_session.commit()
                log_info(f"Committed entities to database before creating relationships")
                
            # Create relationship
            relationship = Form4Relationship(
                form4_filing_id=form4_filing.id,
                issuer_entity_id=rel_data.issuer_entity_id,
                owner_entity_id=rel_data.owner_entity_id,
                relationship_type=rel_data.relationship_type,
                is_director=rel_data.is_director,
                is_officer=rel_data.is_officer,
                is_ten_percent_owner=rel_data.is_ten_percent_owner,
                is_other=rel_data.is_other,
                officer_title=rel_data.officer_title,
                other_text=rel_data.other_text,
                relationship_details=rel_data.relationship_details,
                is_group_filing=rel_data.is_group_filing,
                filing_date=rel_data.filing_date
            )

            self.db_session.add(relationship)
            self.db_session.flush()  # Get ID without committing

            # Store both by index and by ID for flexible lookup
            relationship_map[idx] = relationship
            if rel_data.id:
                relationship_map[str(rel_data.id)] = relationship

            # Log the relationship creation
            if 'issuer_entity' in locals() and 'owner_entity' in locals():
                log_info(f"Created relationship between {issuer_entity.name} and {owner_entity.name}")
            else:
                log_info(f"Created relationship with issuer ID {rel_data.issuer_entity_id} and owner ID {rel_data.owner_entity_id}")

        # Process transactions
        for txn_data in form4_data.transactions:
            # Determine which relationship to associate with
            relationship = None

            # First try to match by relationship_id if provided
            if txn_data.relationship_id and str(txn_data.relationship_id) in relationship_map:
                relationship = relationship_map[str(txn_data.relationship_id)]
            else:
                # Fallback to first relationship
                if relationship_map:
                    relationship = relationship_map[0]

            if relationship:
                transaction = Form4Transaction(
                    form4_filing_id=form4_filing.id,
                    relationship_id=relationship.id,
                    transaction_code=txn_data.transaction_code,
                    transaction_date=txn_data.transaction_date,
                    security_title=txn_data.security_title,
                    transaction_form_type=txn_data.transaction_form_type,
                    shares_amount=txn_data.shares_amount,
                    price_per_share=txn_data.price_per_share,
                    ownership_nature=txn_data.ownership_nature,
                    indirect_ownership_explanation=txn_data.indirect_ownership_explanation,
                    is_derivative=txn_data.is_derivative,
                    equity_swap_involved=txn_data.equity_swap_involved,
                    transaction_timeliness=txn_data.transaction_timeliness,
                    footnote_ids=txn_data.footnote_ids,
                    conversion_price=txn_data.conversion_price,
                    exercise_date=txn_data.exercise_date,
                    expiration_date=txn_data.expiration_date
                )

                self.db_session.add(transaction)
                log_info(f"Added transaction: {txn_data.security_title} on {txn_data.transaction_date}")
            else:
                log_warn(f"No relationship found for transaction: {txn_data.security_title}")