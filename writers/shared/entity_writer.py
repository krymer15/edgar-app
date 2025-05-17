# writers/shared/entity_writer.py

from models.dataclasses.entity import EntityData
from models.orm_models.entity_orm import Entity
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Dict, Optional
from utils.report_logger import log_info, log_warn, log_error
from utils.url_builder import normalize_cik
from utils.cache_manager import get_cache_root  # Just for reference

class EntityWriter:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        # Entity cache to avoid repeated DB queries
        self._entity_cache: Dict[str, Entity] = {}

    def get_or_create_entity(self, entity_data: EntityData) -> Entity:
        """
        Get an existing entity or create a new one if it doesn't exist.
        Uses an in-memory cache to reduce database queries.

        Args:
            entity_data: EntityData object

        Returns:
            Entity ORM instance
        """
        # Use the project's normalize_cik function for consistency
        normalized_cik = entity_data.cik.lstrip("0")  # We still use this for DB lookups

        # Check cache first
        if normalized_cik in self._entity_cache:
            return self._entity_cache[normalized_cik]

        try:
            # Try to find existing entity by CIK
            existing = self.db_session.query(Entity).filter(
                Entity.cik == normalized_cik  # Exact match since we normalize
            ).first()

            if existing:
                # Update details if needed
                updated = False

                if existing.name != entity_data.name:
                    existing.name = entity_data.name
                    updated = True

                if existing.entity_type != entity_data.entity_type:
                    existing.entity_type = entity_data.entity_type
                    updated = True

                if updated:
                    log_info(f"Updated entity details for CIK {entity_data.cik}")

                # Add to cache
                self._entity_cache[normalized_cik] = existing
                return existing

            # Create new entity
            new_entity = Entity(
                cik=normalized_cik,
                name=entity_data.name,
                entity_type=entity_data.entity_type
            )

            self.db_session.add(new_entity)
            self.db_session.flush()  # Get ID without committing

            log_info(f"Created new entity: {entity_data.name} (CIK: {entity_data.cik})")

            # Add to cache
            self._entity_cache[normalized_cik] = new_entity
            return new_entity

        except SQLAlchemyError as e:
            log_error(f"Error in get_or_create_entity: {e}")
            self.db_session.rollback()
            raise

    def get_entity_by_cik(self, cik: str) -> Optional[Entity]:
        """
        Get entity by CIK, using cache if available.

        Args:
            cik: Entity CIK

        Returns:
            Entity ORM instance or None if not found
        """
        # Normalize CIK
        normalized_cik = cik.lstrip("0")

        # Check cache first
        if normalized_cik in self._entity_cache:
            return self._entity_cache[normalized_cik]

        try:
            entity = self.db_session.query(Entity).filter(
                Entity.cik == normalized_cik
            ).first()

            if entity:
                # Add to cache
                self._entity_cache[normalized_cik] = entity

            return entity

        except SQLAlchemyError as e:
            log_error(f"Error in get_entity_by_cik: {e}")
            return None

    def clear_cache(self) -> None:
        """Clear the entity cache"""
        self._entity_cache = {}