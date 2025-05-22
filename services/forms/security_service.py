# services/forms/security_service.py
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.orm_models.forms.security_orm import Security
from models.orm_models.forms.derivative_security_orm import DerivativeSecurity
from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.adapters.security_adapter import (
    convert_security_data_to_orm,
    convert_security_orm_to_data,
    convert_derivative_security_data_to_orm,
    convert_derivative_security_orm_to_data
)

class SecurityService:
    """Service for managing securities"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_or_create_security(self, security_data: SecurityData) -> str:
        """Get existing security or create a new one, return the ID"""
        # Check if security exists
        security = self.db_session.query(Security).filter(
            Security.title == security_data.title,
            Security.issuer_entity_id == security_data.issuer_entity_id
        ).first()
        
        if security:
            return str(security.id)
        
        # Create new security
        new_security = convert_security_data_to_orm(security_data)
        self.db_session.add(new_security)
        self.db_session.flush()  # Generate ID without committing
        
        return str(new_security.id)
    
    def get_securities_for_issuer(self, issuer_entity_id: str) -> List[SecurityData]:
        """Get all securities for an issuer"""
        securities = self.db_session.query(Security).filter(
            Security.issuer_entity_id == issuer_entity_id
        ).all()
        
        return [convert_security_orm_to_data(security) for security in securities]
    
    def get_or_create_derivative_security(self, derivative_data: DerivativeSecurityData) -> str:
        """Get existing derivative security or create a new one, return the ID"""
        # Check if derivative security exists
        derivative = self.db_session.query(DerivativeSecurity).filter(
            DerivativeSecurity.security_id == derivative_data.security_id,
            DerivativeSecurity.underlying_security_title == derivative_data.underlying_security_title,
            DerivativeSecurity.conversion_price == derivative_data.conversion_price
            # Not including exercise/expiration dates as they might not be unique identifiers
        ).first()
        
        if derivative:
            return str(derivative.id)
        
        # Create new derivative security
        new_derivative = convert_derivative_security_data_to_orm(derivative_data)
        self.db_session.add(new_derivative)
        self.db_session.flush()  # Generate ID without committing
        
        return str(new_derivative.id)
    
    def find_security_by_title_and_issuer(self, title: str, issuer_entity_id: str) -> Optional[SecurityData]:
        """Find a security by title and issuer"""
        security = self.db_session.query(Security).filter(
            Security.title == title,
            Security.issuer_entity_id == issuer_entity_id
        ).first()
        
        if not security:
            return None
            
        return convert_security_orm_to_data(security)
    
    def get_derivative_security(self, derivative_id: str) -> Optional[DerivativeSecurityData]:
        """Get a derivative security by ID"""
        derivative = self.db_session.query(DerivativeSecurity).filter(
            DerivativeSecurity.id == derivative_id
        ).first()
        
        if not derivative:
            return None
            
        return convert_derivative_security_orm_to_data(derivative)
        
    def get_security(self, security_id: str) -> Optional[SecurityData]:
        """Get a security by ID"""
        security = self.db_session.query(Security).filter(
            Security.id == security_id
        ).first()
        
        if not security:
            return None
            
        return convert_security_orm_to_data(security)
    
    def find_derivative_security_by_attributes(self, 
                                             security_id: str, 
                                             underlying_title: str, 
                                             conversion_price: Optional[float] = None) -> Optional[DerivativeSecurityData]:
        """Find a derivative security by its key attributes"""
        query = self.db_session.query(DerivativeSecurity).filter(
            DerivativeSecurity.security_id == security_id,
            DerivativeSecurity.underlying_security_title == underlying_title
        )
        
        if conversion_price is not None:
            query = query.filter(DerivativeSecurity.conversion_price == conversion_price)
            
        derivative = query.first()
        
        if not derivative:
            return None
            
        return convert_derivative_security_orm_to_data(derivative)