# Position Service Tests

This directory contains unit tests for the Form 4 position tracking functionality, implemented as part of Phase 3 of the schema redesign.

## Overview

The position tracking system provides historical tracking of security positions for Form 4 relationships. It supports both equity and derivative securities and maintains a complete audit trail of position changes over time.

## Test Files

### `test_mocked_service.py`

Contains comprehensive unit tests for the position service using mock implementations to avoid database dependencies.

#### Test Categories

1. **Position Creation Tests**
   - Basic position creation for equity securities
   - Derivative position creation with proper validation
   - Position data validation and error handling

2. **Position Retrieval Tests**
   - Get position by ID
   - Get latest position for relationship-security combinations
   - Get all positions for a relationship
   - Get all positions for a security
   - Position history retrieval with date filtering

3. **Position Update Tests**
   - Update positions from non-derivative transactions
   - Update positions from derivative transactions
   - Position calculation based on transaction impacts
   - Cumulative position tracking over time

4. **Position-Only Entry Tests**
   - Create position-only entries (holdings without transactions)
   - Handle duplicate position-only entries
   - Validate position-only flag handling

5. **Calculation Tests**
   - Calculate total shares owned per security
   - Handle multiple positions for the same security
   - Date-based position calculations

6. **Validation Tests**
   - Position type validation (equity vs. derivative)
   - Required field validation for derivative positions
   - Data type validation and conversion

### `conftest.py`

Provides shared test fixtures for position testing:

- **Mock Database Session**: Simulates database interactions
- **Sample Position Data**: Pre-configured position data for testing
- **Sample Transaction Data**: Transaction data for position update testing

## Key Test Scenarios

### Basic Position Management

```python
def test_position_creation(position_service, sample_position_data):
    """Test creating a basic equity position"""
    position_id = position_service.create_position(sample_position_data)
    retrieved = position_service.get_position(position_id)
    assert retrieved.shares_amount == sample_position_data.shares_amount
```

### Position Updates from Transactions

```python
def test_update_position_from_transaction(position_service, transaction):
    """Test position updates maintain cumulative totals"""
    # Creates new position based on transaction impact
    # Adds to existing position if one exists
    # Handles both acquisition and disposition
```

### Position History Tracking

```python
def test_get_position_history(position_service):
    """Test retrieving chronological position changes"""
    # Returns positions sorted by date
    # Supports date range filtering
    # Handles multiple positions over time
```

### Latest Position Retrieval

```python
def test_get_latest_position(position_service):
    """Test getting the most recent position"""
    # Returns the latest position for a relationship-security pair
    # Handles derivative security filtering
    # Supports as-of-date queries
```

## Mock Service Implementation

The `MockPositionService` class provides a database-free implementation for testing:

- **In-Memory Storage**: Uses dictionaries to simulate database storage
- **Business Logic**: Implements the same business logic as the real service
- **No Dependencies**: Avoids ORM and database dependencies
- **Fast Execution**: Tests run quickly without database overhead

## Position Data Validation

The tests verify proper validation of position data:

### Required Fields
- `relationship_id`: Must be a valid UUID string
- `security_id`: Must be a valid UUID string
- `position_date`: Must be a valid date
- `shares_amount`: Must be a Decimal value
- `filing_id`: Must be a valid UUID string
- `position_type`: Must be 'equity' or 'derivative'

### Derivative Position Requirements
- `derivative_security_id`: Required for derivative positions
- Validation ensures derivative positions have associated derivative security

### Data Type Conversion
- Automatically converts numeric values to Decimal
- Generates UUIDs if not provided
- Validates position type values

## Running Position Tests

### Run All Position Tests
```bash
python -m pytest tests/forms/position/ -v
```

### Run Specific Test Categories
```bash
# Position creation tests
python -m pytest tests/forms/position/test_mocked_service.py::TestPositionFunctionality::test_position_creation -v

# Position update tests
python -m pytest tests/forms/position/test_mocked_service.py::TestPositionFunctionality::test_update_position_from_non_derivative_transaction -v

# Position history tests
python -m pytest tests/forms/position/test_mocked_service.py::TestPositionFunctionality::test_get_position_history -v
```

### Run with Coverage
```bash
python -m pytest tests/forms/position/ --cov=services.forms.position_service --cov-report=html
```

## Integration with Other Components

The position service integrates with:

1. **Transaction Service**: Updates positions based on transaction impacts
2. **Security Service**: Links positions to normalized securities
3. **Form4 Parser**: Creates positions from parsed Form 4 data
4. **Relationship Service**: Associates positions with Form 4 relationships

## Future Test Enhancements

Potential areas for additional testing:

1. **Performance Tests**: Large dataset position calculations
2. **Concurrency Tests**: Multiple position updates for the same security
3. **Edge Case Tests**: Complex derivative security scenarios
4. **Integration Tests**: End-to-end position tracking through the pipeline

## Implementation Status

- ✅ **Basic Position CRUD**: Create, read, update position data
- ✅ **Position History**: Track position changes over time
- ✅ **Transaction Integration**: Update positions from transactions
- ✅ **Position Calculations**: Calculate total shares owned
- ✅ **Validation**: Comprehensive data validation
- ✅ **Mock Testing**: Database-independent unit tests
- 🔄 **Parser Integration**: Integration with Form 4 parser (Phase 4)
- 🔄 **Performance Optimization**: Large dataset optimizations (Future)