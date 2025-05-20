# Leveraging Reporting CIKs for Query and Analysis

## Overview

While the Bug 8 fix standardizes on the issuer CIK for storage paths and URLs, the reporting owner CIKs still contain valuable relationship information that should be indexed and queryable. This document outlines a strategy for making reporting CIK data easily accessible through the application's UI for end users.

## Database-Level Indexing Strategy

### 1. Add PostgreSQL Indexes on CIK Columns

```sql
-- Add index on entity CIK for fast lookups by either issuer or owner CIK
CREATE INDEX idx_entities_cik ON entities(cik);

-- Add index on owner_entity_id in form4_relationships table for finding all relationships 
-- where a specific entity is the owner
CREATE INDEX idx_form4_relationships_owner_entity_id ON form4_relationships(owner_entity_id);

-- Add composite index for common queries joining issuer and owner
CREATE INDEX idx_form4_relationships_issuer_owner 
ON form4_relationships(issuer_entity_id, owner_entity_id);

-- Add index on transaction dates for time-based filtering
CREATE INDEX idx_form4_transactions_transaction_date 
ON form4_transactions(transaction_date);
```

### 2. Create View Tables for Common Query Patterns

Create materialized views that precompute common query results for UI display:

```sql
-- Insider trading activity summary
CREATE MATERIALIZED VIEW insider_trading_summary AS
SELECT 
    e_issuer.cik AS issuer_cik,
    e_issuer.name AS issuer_name,
    e_owner.cik AS owner_cik,
    e_owner.name AS owner_name,
    e_owner.entity_type AS owner_type,
    r.is_director, 
    r.is_officer,
    r.is_ten_percent_owner,
    r.officer_title,
    COUNT(t.id) AS transaction_count,
    SUM(CASE WHEN t.transaction_code IN ('P', 'A') THEN t.shares_amount ELSE 0 END) AS total_acquired,
    SUM(CASE WHEN t.transaction_code IN ('S', 'D') THEN t.shares_amount ELSE 0 END) AS total_disposed,
    MAX(t.transaction_date) AS latest_transaction_date
FROM 
    form4_relationships r
JOIN
    entities e_issuer ON r.issuer_entity_id = e_issuer.id
JOIN
    entities e_owner ON r.owner_entity_id = e_owner.id
LEFT JOIN
    form4_transactions t ON t.relationship_id = r.id
GROUP BY
    e_issuer.cik, e_issuer.name, e_owner.cik, e_owner.name, 
    e_owner.entity_type, r.is_director, r.is_officer, 
    r.is_ten_percent_owner, r.officer_title;

-- Index the view for fast queries
CREATE INDEX idx_insider_trading_owner_cik ON insider_trading_summary(owner_cik);
CREATE INDEX idx_insider_trading_issuer_cik ON insider_trading_summary(issuer_cik);
CREATE INDEX idx_insider_trading_latest_date ON insider_trading_summary(latest_transaction_date);

-- Create a view for recent significant transactions
CREATE MATERIALIZED VIEW significant_transactions AS
SELECT 
    e_issuer.cik AS issuer_cik,
    e_issuer.name AS issuer_name,
    e_owner.cik AS owner_cik,
    e_owner.name AS owner_name,
    r.officer_title,
    t.transaction_date,
    t.transaction_code,
    t.shares_amount,
    t.price_per_share,
    (t.shares_amount * t.price_per_share) AS transaction_value,
    t.security_title,
    t.ownership_nature
FROM 
    form4_transactions t
JOIN
    form4_relationships r ON t.relationship_id = r.id
JOIN
    entities e_issuer ON r.issuer_entity_id = e_issuer.id
JOIN
    entities e_owner ON r.owner_entity_id = e_owner.id
WHERE 
    (t.shares_amount * t.price_per_share) > 100000 -- Transactions over $100,000
ORDER BY
    t.transaction_date DESC;

-- Refresh strategy for materialized views
-- Create a function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW insider_trading_summary;
    REFRESH MATERIALIZED VIEW significant_transactions;
    -- Add additional views as they are created
END;
$$ LANGUAGE plpgsql;
```

### 3. Enhance ORM Models for UI-Friendly Queries

Update the ORM models to include methods that support UI query patterns:

```python
# In models/orm_models/forms/form4_relationship_orm.py

class Form4Relationship(Base):
    # ... existing columns ...
    
    # Add query methods for UI
    @classmethod
    def get_insider_activity(cls, session, filters=None, order_by=None, limit=None):
        """
        Get insider trading activity for UI display with flexible filtering.
        
        Args:
            session: Database session
            filters: Dict of filter parameters:
                - issuer_cik: Filter by issuer CIK
                - owner_cik: Filter by owner CIK
                - start_date: Minimum transaction date
                - end_date: Maximum transaction date
                - relationship_types: List of relationship types to include
                - transaction_codes: List of transaction codes to include
            order_by: Column to order by (default: transaction_date desc)
            limit: Maximum number of results
            
        Returns:
            Query object that can be further refined or executed
        """
        from models.orm_models.entity_orm import Entity
        from models.orm_models.forms.form4_transaction_orm import Form4Transaction
        
        # Start with a base query joining all relevant tables
        query = (session.query(
                cls, 
                Entity.name.label('issuer_name'),
                Form4Transaction
            )
            .join(Entity, cls.issuer_entity_id == Entity.id)
            .join(Form4Transaction, Form4Transaction.relationship_id == cls.id)
        )
        
        # Apply filters
        if filters:
            if 'issuer_cik' in filters and filters['issuer_cik']:
                issuer_subq = (session.query(Entity.id)
                              .filter(Entity.cik == filters['issuer_cik'])
                              .subquery())
                query = query.filter(cls.issuer_entity_id.in_(issuer_subq))
                
            if 'owner_cik' in filters and filters['owner_cik']:
                owner_subq = (session.query(Entity.id)
                             .filter(Entity.cik == filters['owner_cik'])
                             .subquery())
                query = query.filter(cls.owner_entity_id.in_(owner_subq))
                
            if 'start_date' in filters and filters['start_date']:
                query = query.filter(Form4Transaction.transaction_date >= filters['start_date'])
                
            if 'end_date' in filters and filters['end_date']:
                query = query.filter(Form4Transaction.transaction_date <= filters['end_date'])
                
            if 'relationship_types' in filters and filters['relationship_types']:
                conditions = []
                for r_type in filters['relationship_types']:
                    if r_type == 'director':
                        conditions.append(cls.is_director == True)
                    elif r_type == 'officer':
                        conditions.append(cls.is_officer == True)
                    elif r_type == 'ten_percent_owner':
                        conditions.append(cls.is_ten_percent_owner == True)
                if conditions:
                    query = query.filter(or_(*conditions))
                    
            if 'transaction_codes' in filters and filters['transaction_codes']:
                query = query.filter(Form4Transaction.transaction_code.in_(filters['transaction_codes']))
        
        # Apply ordering
        if order_by:
            query = query.order_by(order_by)
        else:
            query = query.order_by(Form4Transaction.transaction_date.desc())
            
        # Apply limit
        if limit:
            query = query.limit(limit)
            
        return query
```

## UI Component Design for CIK-Based Queries

The UI should provide intuitive ways to query the data by either issuer CIK, reporting owner CIK, or both. Here are recommended UI components and their associated query patterns:

### 1. Entity Search Component

A flexible search component that allows users to find either issuers or reporting owners:

```python
def search_entities(session, search_term, entity_type=None, limit=10):
    """
    Search for entities by name or CIK for autocomplete in UI.
    
    Args:
        session: Database session
        search_term: Text to search for (name or CIK)
        entity_type: Optional filter ('person', 'company', or None for all)
        limit: Maximum results to return
        
    Returns:
        List of matching entities with id, name, cik, and entity_type
    """
    from models.orm_models.entity_orm import Entity
    from sqlalchemy import or_
    
    query = (session.query(
            Entity.id, 
            Entity.name, 
            Entity.cik, 
            Entity.entity_type
        )
        .filter(
            or_(
                Entity.name.ilike(f'%{search_term}%'),
                Entity.cik.ilike(f'%{search_term}%')
            )
        )
    )
    
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
        
    return query.limit(limit).all()
```

### 2. Relationship Explorer Dashboard

A dashboard that shows the relationships between issuers and reporting owners:

```python
def get_relationship_network(session, entity_cik, as_role=None, max_depth=1):
    """
    Get relationship network centered on an entity (either issuer or owner).
    
    Args:
        session: Database session
        entity_cik: CIK of the central entity
        as_role: 'issuer', 'owner', or None (both)
        max_depth: How many degrees of separation to include (1-3)
        
    Returns:
        Network data structure for visualization
    """
    from models.orm_models.entity_orm import Entity
    from models.orm_models.forms.form4_relationship_orm import Form4Relationship
    
    # First find the entity
    entity = session.query(Entity).filter(Entity.cik == entity_cik).first()
    if not entity:
        return {"nodes": [], "links": []}
    
    # Initialize results
    nodes = {entity.id: {"id": entity.id, "name": entity.name, "cik": entity.cik, 
                         "type": entity.entity_type, "central": True}}
    links = {}
    entities_to_process = [(entity.id, 0)]  # (entity_id, current_depth)
    processed_entities = set()
    
    # Process entities up to max_depth
    while entities_to_process:
        current_id, current_depth = entities_to_process.pop(0)
        
        if current_id in processed_entities or current_depth >= max_depth:
            continue
            
        processed_entities.add(current_id)
        
        # Find relationships where this entity is the issuer
        if as_role in (None, 'issuer'):
            issuer_relationships = (session.query(Form4Relationship, Entity)
                                   .join(Entity, Form4Relationship.owner_entity_id == Entity.id)
                                   .filter(Form4Relationship.issuer_entity_id == current_id)
                                   .all())
            
            for rel, owner in issuer_relationships:
                # Add owner node if not already present
                if owner.id not in nodes:
                    nodes[owner.id] = {"id": owner.id, "name": owner.name, "cik": owner.cik, 
                                      "type": owner.entity_type}
                    if current_depth + 1 < max_depth:
                        entities_to_process.append((owner.id, current_depth + 1))
                
                # Add relationship link
                link_id = f"{current_id}-{owner.id}"
                if link_id not in links:
                    links[link_id] = {
                        "source": current_id,
                        "target": owner.id,
                        "type": "has_insider",
                        "details": {
                            "is_director": rel.is_director,
                            "is_officer": rel.is_officer,
                            "is_ten_percent_owner": rel.is_ten_percent_owner,
                            "officer_title": rel.officer_title
                        }
                    }
        
        # Find relationships where this entity is the owner
        if as_role in (None, 'owner'):
            owner_relationships = (session.query(Form4Relationship, Entity)
                                  .join(Entity, Form4Relationship.issuer_entity_id == Entity.id)
                                  .filter(Form4Relationship.owner_entity_id == current_id)
                                  .all())
            
            for rel, issuer in owner_relationships:
                # Add issuer node if not already present
                if issuer.id not in nodes:
                    nodes[issuer.id] = {"id": issuer.id, "name": issuer.name, "cik": issuer.cik, 
                                       "type": issuer.entity_type}
                    if current_depth + 1 < max_depth:
                        entities_to_process.append((issuer.id, current_depth + 1))
                
                # Add relationship link
                link_id = f"{issuer.id}-{current_id}"
                if link_id not in links:
                    links[link_id] = {
                        "source": issuer.id,
                        "target": current_id,
                        "type": "has_insider",
                        "details": {
                            "is_director": rel.is_director,
                            "is_officer": rel.is_officer,
                            "is_ten_percent_owner": rel.is_ten_percent_owner,
                            "officer_title": rel.officer_title
                        }
                    }
    
    return {
        "nodes": list(nodes.values()),
        "links": list(links.values())
    }
```

### 3. Transaction Timeline

A timeline view of transactions for a specific issuer, owner, or relationship:

```python
def get_transaction_timeline(session, filters, interval='month'):
    """
    Get aggregated transaction data for timeline visualization.
    
    Args:
        session: Database session
        filters: Dict with query filters (same as get_insider_activity)
        interval: 'day', 'week', 'month', 'quarter', or 'year'
        
    Returns:
        Time series data for visualization
    """
    from models.orm_models.forms.form4_transaction_orm import Form4Transaction
    from models.orm_models.forms.form4_relationship_orm import Form4Relationship
    from models.orm_models.entity_orm import Entity
    from sqlalchemy import func
    
    # Define the date truncation expression based on interval
    if interval == 'day':
        date_trunc = func.date_trunc('day', Form4Transaction.transaction_date)
    elif interval == 'week':
        date_trunc = func.date_trunc('week', Form4Transaction.transaction_date)
    elif interval == 'month':
        date_trunc = func.date_trunc('month', Form4Transaction.transaction_date)
    elif interval == 'quarter':
        date_trunc = func.date_trunc('quarter', Form4Transaction.transaction_date)
    else:  # year
        date_trunc = func.date_trunc('year', Form4Transaction.transaction_date)
    
    # Base query with time grouping
    query = (session.query(
            date_trunc.label('period'),
            func.sum(
                func.case(
                    [(Form4Transaction.transaction_code.in_(['P', 'A']), Form4Transaction.shares_amount)],
                    else_=0
                )
            ).label('acquired'),
            func.sum(
                func.case(
                    [(Form4Transaction.transaction_code.in_(['S', 'D']), Form4Transaction.shares_amount)],
                    else_=0
                )
            ).label('disposed'),
            func.count(Form4Transaction.id).label('count')
        )
        .join(Form4Relationship, Form4Transaction.relationship_id == Form4Relationship.id)
    )
    
    # Apply the same filters as get_insider_activity
    if 'issuer_cik' in filters and filters['issuer_cik']:
        issuer_subq = (session.query(Entity.id)
                      .filter(Entity.cik == filters['issuer_cik'])
                      .subquery())
        query = query.join(Entity, Form4Relationship.issuer_entity_id == Entity.id)
        query = query.filter(Form4Relationship.issuer_entity_id.in_(issuer_subq))
    
    if 'owner_cik' in filters and filters['owner_cik']:
        owner_subq = (session.query(Entity.id)
                     .filter(Entity.cik == filters['owner_cik'])
                     .subquery())
        query = query.filter(Form4Relationship.owner_entity_id.in_(owner_subq))
    
    # Apply date filters
    if 'start_date' in filters and filters['start_date']:
        query = query.filter(Form4Transaction.transaction_date >= filters['start_date'])
    if 'end_date' in filters and filters['end_date']:
        query = query.filter(Form4Transaction.transaction_date <= filters['end_date'])
    
    # Group by the period
    query = query.group_by(date_trunc).order_by(date_trunc)
    
    # Transform results into visualization-friendly format
    results = query.all()
    
    return [{
        'period': result.period.isoformat(),
        'acquired': float(result.acquired) if result.acquired else 0,
        'disposed': float(result.disposed) if result.disposed else 0,
        'count': result.count
    } for result in results]
```

## Implementation Roadmap

### Phase 1: Database Optimization

1. **Create a SQL migration script** to add the necessary indexes on CIK columns
2. **Implement materialized views** for common query patterns
3. **Create a view refresh mechanism** (scheduled task or trigger-based)

### Phase 2: Query Model Enhancement

1. **Enhance ORM models** with UI-friendly query methods
2. **Create unit tests** to ensure query performance and correctness
3. **Document query patterns** for frontend developers

### Phase 3: UI Component Implementation

1. **Design entity search and selection UI** (autocomplete, dropdown, etc.)
2. **Implement transaction dashboard components**:
   - Entity relationship visualization
   - Transaction timeline charts
   - Transaction tables with filtering
3. **Create filter UI** for relationship types, date ranges, transaction codes, etc.

### Phase 4: Integration and Optimization 

1. **Implement client-side caching** for frequently accessed data
2. **Optimize query performance** for large datasets
3. **Add pagination and lazy loading** for large result sets
4. **Create export functionality** for data table results

## Conclusion

By implementing proper database indexing and UI-friendly query patterns, we can fully leverage the relationship data in Form 4 filings while maintaining the benefits of our Bug 8 fix. This approach ensures:

1. **Standardized storage organization** (by issuer CIK) for consistency
2. **Rich query capabilities** (by any CIK) for analysis
3. **UI-friendly data access patterns** for interactive exploration
4. **High performance** through optimized database design and materialized views

The approach outlined in this document enables end users to easily explore and analyze Form 4 data through an intuitive UI without requiring direct API access or SQL knowledge.