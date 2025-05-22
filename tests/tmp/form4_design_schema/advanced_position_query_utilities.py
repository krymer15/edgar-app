# Advanced Position Query Utilities
#
# This file contains advanced position query implementations and GUI integration
# examples that supplement the core position service in phase3_implementation.md.
# These components can be optionally implemented for enhanced functionality.

from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

# Import ORM models
from models.orm_models.forms.relationship_position_orm import RelationshipPosition
from models.orm_models.forms.security_orm import Security
from models.orm_models.forms.form4_relationship_orm import Form4Relationship
from models.orm_models.forms.non_derivative_transaction_orm import NonDerivativeTransaction
from models.orm_models.forms.derivative_transaction_orm import DerivativeTransaction
from models.orm_models.entity_orm import Entity

# Optional request/response dataclasses for formal API design
class PositionResult:
    """Standard response format for position queries"""
    def __init__(self, success: bool, data: Dict[str, Any], error_message: str = None):
        self.success = success
        self.data = data
        self.error_message = error_message

# Advanced query methods that can be added to PositionService

def get_entity_positions_snapshot(db_session: Session, entity_id: str, 
                                as_of_date: Optional[date] = None) -> Dict[str, Dict[str, Decimal]]:
    """Get positions snapshot for an entity (either as issuer or owner)
    
    Returns a hierarchical structure of positions:
    {
        "relationship_name": {
            "security_title": shares_amount,
            ...
        },
        ...
    }
    """
    as_of_date = as_of_date or date.today()
    
    # For each relationship involving this entity (either as issuer or owner)
    relationships = db_session.query(Form4Relationship).filter(
        or_(
            Form4Relationship.issuer_entity_id == entity_id,
            Form4Relationship.owner_entity_id == entity_id
        )
    ).all()
    
    result = {}
    for relationship in relationships:
        # For each security, get the most recent position before or on as_of_date
        securities = db_session.query(
            Security.id,
            Security.title,
            RelationshipPosition.shares_amount
        ).join(
            RelationshipPosition, Security.id == RelationshipPosition.security_id
        ).filter(
            RelationshipPosition.relationship_id == relationship.id,
            RelationshipPosition.position_date <= as_of_date
        ).distinct(
            Security.id  # Get distinct securities
        ).order_by(
            Security.id,
            desc(RelationshipPosition.position_date)  # Get most recent position
        ).all()
        
        relationship_key = f"{relationship.issuer_entity.name} - {relationship.owner_entity.name}"
        result[relationship_key] = {
            security_title: shares_amount
            for security_id, security_title, shares_amount in securities
        }
        
    return result

def get_insider_ownership(db_session: Session, issuer_id: str, 
                        as_of_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """Get all insider ownership positions for an issuer
    
    Returns a list of ownership positions with owner details:
    [
        {
            "owner_name": "John Smith",
            "owner_id": "123",
            "relationship_type": "director",
            "security_title": "Common Stock",
            "shares_amount": 1000,
            ...
        },
        ...
    ]
    """
    as_of_date = as_of_date or date.today()
    
    # Find the most recent position for each owner-security combination
    subquery = db_session.query(
        RelationshipPosition.relationship_id,
        RelationshipPosition.security_id,
        func.max(RelationshipPosition.position_date).label('latest_date')
    ).join(
        Form4Relationship, RelationshipPosition.relationship_id == Form4Relationship.id
    ).filter(
        Form4Relationship.issuer_entity_id == issuer_id,
        RelationshipPosition.position_date <= as_of_date
    ).group_by(
        RelationshipPosition.relationship_id,
        RelationshipPosition.security_id
    ).subquery()
    
    # Join with the positions to get the actual amounts
    results = db_session.query(
        Entity.name.label('owner_name'),
        Entity.id.label('owner_id'),
        Form4Relationship.relationship_type,
        Form4Relationship.id.label('relationship_id'),
        Security.title.label('security_title'),
        Security.id.label('security_id'),
        RelationshipPosition.shares_amount,
        RelationshipPosition.direct_ownership,
        RelationshipPosition.position_date
    ).select_from(
        RelationshipPosition
    ).join(
        subquery, and_(
            RelationshipPosition.relationship_id == subquery.c.relationship_id,
            RelationshipPosition.security_id == subquery.c.security_id,
            RelationshipPosition.position_date == subquery.c.latest_date
        )
    ).join(
        Form4Relationship, RelationshipPosition.relationship_id == Form4Relationship.id
    ).join(
        Entity, Form4Relationship.owner_entity_id == Entity.id
    ).join(
        Security, RelationshipPosition.security_id == Security.id
    ).filter(
        Form4Relationship.issuer_entity_id == issuer_id,
        RelationshipPosition.shares_amount > 0  # Only include positive positions
    ).order_by(
        Entity.name,
        Security.title
    ).all()
    
    # Convert SQLAlchemy result to dict for easier consumption
    return [
        {
            'owner_name': r.owner_name,
            'owner_id': str(r.owner_id),
            'relationship_type': r.relationship_type,
            'relationship_id': str(r.relationship_id),
            'security_title': r.security_title,
            'security_id': str(r.security_id),
            'shares_amount': float(r.shares_amount),
            'direct_ownership': r.direct_ownership,
            'position_date': r.position_date
        }
        for r in results
    ]

def format_position_history_for_chart(position_history: List[Dict[str, Any]], 
                                    security_title: str) -> Dict[str, Any]:
    """Format position history data for chart display
    
    Converts a position history list into a format suitable for chart libraries:
    {
        "labels": ["2023-01-01", "2023-01-15", ...],
        "datasets": [{
            "label": "Common Stock Position",
            "data": [1000, 1500, ...],
            "borderColor": "rgb(53, 162, 235)",
            "backgroundColor": "rgba(53, 162, 235, 0.5)"
        }]
    }
    """
    return {
        "labels": [p['position_date'].strftime('%Y-%m-%d') for p in position_history],
        "datasets": [{
            "label": f"{security_title} Position",
            "data": [float(p['shares_amount']) for p in position_history],
            "borderColor": "rgb(53, 162, 235)",
            "backgroundColor": "rgba(53, 162, 235, 0.5)"
        }]
    }

# Simple error handling wrapper example
def with_error_handling(func):
    """Decorator for wrapping service methods with error handling"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return PositionResult(success=True, data=result)
        except Exception as e:
            return PositionResult(
                success=False,
                data={},
                error_message=f"Error in {func.__name__}: {str(e)}"
            )
    return wrapper

# Example controller integration with GUI elements
class PositionController:
    """Controller class that interfaces with GUI elements for position data"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    def get_entity_position_snapshot(self, entity_id: str, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """Get position snapshot data for GUI display"""
        try:
            entity = self.db_session.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                return {"error": f"Entity with ID {entity_id} not found"}
                
            positions = get_entity_positions_snapshot(self.db_session, entity_id, as_of_date)
            
            # Format for GUI display
            return {
                "entity_name": entity.name,
                "entity_cik": entity.cik,
                "entity_type": entity.entity_type,
                "as_of_date": as_of_date or date.today(),
                "position_count": sum(len(secs) for secs in positions.values()),
                "relationship_count": len(positions),
                "positions": positions
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_position_history_chart_data(self, relationship_id: str, security_id: str, 
                                     start_date: Optional[date] = None,
                                     end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get position history data formatted for chart display in GUI"""
        try:
            # Get relationship info
            relationship = self.db_session.query(Form4Relationship).filter(
                Form4Relationship.id == relationship_id
            ).first()
            
            if not relationship:
                return {"error": f"Relationship with ID {relationship_id} not found"}
            
            # Get security info
            security = self.db_session.query(Security).filter(Security.id == security_id).first()
            if not security:
                return {"error": f"Security with ID {security_id} not found"}
            
            # Query positions
            query = self.db_session.query(
                RelationshipPosition.position_date,
                RelationshipPosition.shares_amount,
                RelationshipPosition.direct_ownership,
                RelationshipPosition.transaction_id,
                RelationshipPosition.filing_id
            ).filter(
                RelationshipPosition.relationship_id == relationship_id,
                RelationshipPosition.security_id == security_id
            )
            
            if start_date:
                query = query.filter(RelationshipPosition.position_date >= start_date)
            
            if end_date:
                query = query.filter(RelationshipPosition.position_date <= end_date)
                
            results = query.order_by(RelationshipPosition.position_date).all()
            
            position_history = [
                {
                    'position_date': r.position_date,
                    'shares_amount': float(r.shares_amount),
                    'direct_ownership': r.direct_ownership,
                    'transaction_id': str(r.transaction_id) if r.transaction_id else None,
                    'filing_id': str(r.filing_id)
                }
                for r in results
            ]
            
            # Format for charts
            chart_data = format_position_history_for_chart(position_history, security.title)
            
            return {
                "relationship_issuer": relationship.issuer_entity.name,
                "relationship_owner": relationship.owner_entity.name,
                "security_title": security.title,
                "position_count": len(position_history),
                "chart_data": chart_data,
                "position_history": position_history
            }
        except Exception as e:
            return {"error": str(e)}