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
        # Start with a clean transaction state
        self.db_session.rollback()
        
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
                # Use flush to get the ID and make sure it's available in the session
                self.db_session.flush()  
                log_info(f"Created new Form 4 filing record for {db_accession_number}")
            
            # Check if we have entity objects attached directly
            # This would be the case when using the enhanced XML parser
            if hasattr(form4_data, 'issuer_entity') and form4_data.issuer_entity:
                log_info(f"Using entity objects attached directly to Form4FilingData for {db_accession_number}")
                # Create or get the issuer entity
                issuer_entity_orm = self.entity_writer.get_or_create_entity(form4_data.issuer_entity)
                
                # Create or get the owner entities
                if hasattr(form4_data, 'owner_entities') and form4_data.owner_entities:
                    for owner_entity in form4_data.owner_entities:
                        self.entity_writer.get_or_create_entity(owner_entity)
                    
                    # Commit entities to ensure they exist before proceeding
                    self.db_session.commit()
                    log_info(f"Committed issuer and {len(form4_data.owner_entities)} owner entities")
            else:
                # Fallback to the old approach of extracting entity info from relationship IDs
                # Collect all entity IDs from this Form 4 data to pre-create them
                entity_ids = set()
                for rel in form4_data.relationships:
                    entity_ids.add(rel.issuer_entity_id)
                    entity_ids.add(rel.owner_entity_id)
                
                # Pre-create all entities in a single transaction to ensure they exist
                log_info(f"Pre-creating {len(entity_ids)} entities for {db_accession_number}")
                for entity_id in entity_ids:
                    # Create a basic entity
                    is_issuer = any(rel.issuer_entity_id == entity_id for rel in form4_data.relationships)
                    
                    if is_issuer:
                        # For issuers, try to extract a reasonable CIK
                        cik = self._extract_cik_from_accession(form4_data.accession_number)
                        name = f"Issuer CIK {cik}"
                        entity_type = "company"
                    else:
                        # For owners, use a derived identifier
                        cik = f"owner_{str(entity_id)[-6:]}"
                        name = f"Owner ID {str(entity_id)[-6:]}"
                        entity_type = "person"
                    
                    entity_data = EntityData(
                        cik=cik,
                        name=name,
                        entity_type=entity_type,
                        id=entity_id
                    )
                    
                    self.entity_writer.get_or_create_entity(entity_data)
                
                # Commit entities first to ensure they exist
                self.db_session.commit()
                log_info(f"Committed all entities before creating relationships for {db_accession_number}")
            
            # Now process relationships and transactions
            self._write_relationships_and_transactions(form4_data, form4_filing)

            # Commit all remaining changes
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
            if hasattr(form4_data, 'issuer_entity') and form4_data.issuer_entity:
                # Use the issuer entity from form4_data directly
                issuer_entity = self.entity_writer.get_entity_by_id(form4_data.issuer_entity.id)
                if not issuer_entity:
                    # If not found by ID, try by CIK
                    issuer_entity = self.entity_writer.get_entity_by_cik(form4_data.issuer_entity.cik)
                    if not issuer_entity:
                        # Last resort: create it
                        issuer_entity = self.entity_writer.get_or_create_entity(form4_data.issuer_entity)
                    
                # Get owner entity - match by relationship index if owner_entities is available
                owner_entity = None
                if hasattr(form4_data, 'owner_entities') and form4_data.owner_entities and idx < len(form4_data.owner_entities):
                    owner_data = form4_data.owner_entities[idx]
                    owner_entity = self.entity_writer.get_entity_by_id(owner_data.id)
                    if not owner_entity:
                        # If not found by ID, try by CIK
                        owner_entity = self.entity_writer.get_entity_by_cik(owner_data.cik)
                        if not owner_entity:
                            # Last resort: create it
                            owner_entity = self.entity_writer.get_or_create_entity(owner_data)
                
                # If we still don't have an owner, fallback to getting by ID from the relationship
                if not owner_entity:
                    owner_entity = self.entity_writer.get_entity_by_id(rel_data.owner_entity_id)
            else:
                # Need to get entity records by ID from the database
                issuer_id = rel_data.issuer_entity_id
                owner_id = rel_data.owner_entity_id
                
                log_info(f"Retrieving entity information by ID for relationship")
                log_info(f"Using issuer_entity_id: {issuer_id}, owner_entity_id: {owner_id}")
                
                # Get entities from the database - they should already exist
                # from our pre-creation step in write_form4_data
                issuer_entity = self.entity_writer.get_entity_by_id(issuer_id)
                owner_entity = self.entity_writer.get_entity_by_id(owner_id)
                
                if not issuer_entity or not owner_entity:
                    log_warn(f"Entity not found despite pre-creation: issuer={issuer_id}, owner={owner_id}")
                    # Fall back to creating them if they don't exist for some reason
                    if not issuer_entity:
                        # Create dummy EntityData object for issuer
                        issuer_cik = self._extract_cik_from_accession(form4_data.accession_number)
                        issuer_entity_data = EntityData(
                            cik=issuer_cik,
                            name=f"Issuer CIK {issuer_cik}",
                            entity_type="company",
                            id=issuer_id  # Use the same ID from the relationship
                        )
                        issuer_entity = self.entity_writer.get_or_create_entity(issuer_entity_data)
                        
                    if not owner_entity:
                        # Create dummy EntityData object for owner
                        owner_entity_data = EntityData(
                            cik=f"owner_{str(owner_id)[-6:]}",  # Use last 6 chars of ID as a unique identifier
                            name=f"Owner ID {str(owner_id)[-6:]}",
                            entity_type="person",
                            id=owner_id  # Use the same ID from the relationship
                        )
                        owner_entity = self.entity_writer.get_or_create_entity(owner_entity_data)
                
            # Important: Use the actual database entity IDs, not the IDs from rel_data
            # This ensures we use the correct entity IDs that exist in the database
            if not issuer_entity or not owner_entity:
                log_error(f"Cannot create relationship - missing entities")
                log_error(f"  Missing: {'issuer' if not issuer_entity else ''} {'owner' if not owner_entity else ''}")
                log_error(f"  Issuer ID in relationship: {rel_data.issuer_entity_id}")
                log_error(f"  Owner ID in relationship: {rel_data.owner_entity_id}")
                continue
                
            # Debug info to track ID differences that may cause foreign key issues
            if str(issuer_entity.id) != str(rel_data.issuer_entity_id) or str(owner_entity.id) != str(rel_data.owner_entity_id):
                log_info(f"Entity ID difference detected:")
                log_info(f"  Issuer: DB ID {issuer_entity.id} vs relationship ID {rel_data.issuer_entity_id}")
                log_info(f"  Owner: DB ID {owner_entity.id} vs relationship ID {rel_data.owner_entity_id}")
                
            # Force a commit here to ensure entities are actually in the database before creating relationships
            # This resolves the foreign key constraint violation we've been seeing
            try:
                self.db_session.commit()
                log_info(f"Committed entities to database before creating relationships")
            except Exception as e:
                log_error(f"Error committing entities before relationships: {e}")
                raise
                
            # Create relationship with the actual database entity IDs
            relationship = Form4Relationship(
                form4_filing_id=form4_filing.id,
                issuer_entity_id=issuer_entity.id,  # Use the actual entity ID from the database
                owner_entity_id=owner_entity.id,    # Use the actual entity ID from the database
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

            # Log the relationship creation with detailed information
            log_info(f"Created relationship between:")
            log_info(f"  Issuer: {issuer_entity.name} (ID: {issuer_entity.id}, CIK: {issuer_entity.cik})")
            log_info(f"  Owner: {owner_entity.name} (ID: {owner_entity.id}, CIK: {owner_entity.cik})")
            
            # Debug information - compare with original relationship data
            if str(issuer_entity.id) != str(rel_data.issuer_entity_id):
                log_info(f"  Note: Issuer ID from relationship data ({rel_data.issuer_entity_id}) differs from database entity ID ({issuer_entity.id})")
            if str(owner_entity.id) != str(rel_data.owner_entity_id):
                log_info(f"  Note: Owner ID from relationship data ({rel_data.owner_entity_id}) differs from database entity ID ({owner_entity.id})")

        # Commit relationships to ensure they're in the database before adding transactions
        try:
            self.db_session.commit()
            log_info(f"Committed relationships to database before creating transactions")
        except Exception as e:
            log_error(f"Error committing relationships before transactions: {e}")
            raise
            
        # Process transactions
        log_info(f"Processing {len(form4_data.transactions)} transactions")
        for txn_data in form4_data.transactions:
            # Determine which relationship to associate with
            relationship = None

            # First try to match by relationship_id if provided
            if txn_data.relationship_id and str(txn_data.relationship_id) in relationship_map:
                relationship = relationship_map[str(txn_data.relationship_id)]
                log_info(f"Found relationship by ID {txn_data.relationship_id}")
            else:
                # Fallback to first relationship
                if relationship_map:
                    relationship = relationship_map[0]
                    log_info(f"Using first relationship (ID: {relationship.id}) for transaction")

            if relationship:
                try:
                    log_info(f"Creating transaction: {txn_data.security_title} on {txn_data.transaction_date}")
                    log_info(f"  Transaction code: {txn_data.transaction_code}")
                    log_info(f"  Shares: {txn_data.shares_amount}, Price: {txn_data.price_per_share}")
                    log_info(f"  Using relationship ID: {relationship.id}")
                    log_info(f"  Using form4_filing_id: {form4_filing.id}")
                    
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
                    # Flush to detect any immediate database issues
                    self.db_session.flush()
                    log_info(f"Added transaction: {txn_data.security_title} on {txn_data.transaction_date} (ID: {transaction.id})")
                except Exception as e:
                    log_error(f"Error creating transaction: {e}")
                    # Continue processing other transactions
                    continue
            else:
                log_warn(f"No relationship found for transaction: {txn_data.security_title}. Transaction will be skipped.")
                
        # After all transactions are processed, do an explicit commit to ensure they're saved
        try:
            self.db_session.commit()
            log_info(f"Committed all transactions to database")
        except Exception as e:
            log_error(f"Error committing transactions: {e}")
            raise