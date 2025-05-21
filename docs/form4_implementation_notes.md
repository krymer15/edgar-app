# Form 4 Implementation Notes

This document covers important details and nuances of Form 4 data processing, especially regarding position-only rows and derivative securities.

## Form 4 Structure and Columns

Form 4 is divided into two main tables:
1. **Non-Derivative Securities** (Table I)
2. **Derivative Securities** (Table II)

### Non-Derivative Securities Columns

Column structure for Table I:
- **Column 1**: Title of Security
- **Column 2**: Transaction Date
- **Column 3**: Transaction Code
- **Column 4**: Amount of Securities Acquired (A) or Disposed of (D)
- **Column 5**: Amount of Securities Beneficially Owned Following Reported Transaction(s)
- **Column 6**: Ownership Form: Direct (D) or Indirect (I)
- **Column 7**: Nature of Indirect Beneficial Ownership

### Derivative Securities Columns

Column structure for Table II:
- **Column 1**: Title of Derivative Security
- **Column 2**: Conversion or Exercise Price of Derivative Security
- **Column 3**: Transaction Date
- **Column 4**: Transaction Code
- **Column 5**: Number of Derivative Securities Acquired (A) or Disposed of (D)
- **Column 6**: Date Exercisable and Expiration Date
- **Column 7**: Title and Amount of Underlying Securities
- **Column 8**: Price of Derivative Security
- **Column 9**: Number of Derivative Securities Beneficially Owned Following Reported Transaction(s)
- **Column 10**: Ownership Form of Derivative Security: Direct (D) or Indirect (I)
- **Column 11**: Nature of Indirect Beneficial Ownership

## Position-Only Rows

Position-only rows are represented as:
- `<nonDerivativeHolding>` elements for Table I
- `<derivativeHolding>` elements for Table II

These elements do not contain transaction information but report only the current ownership position.

### Key Characteristics of Position-Only Rows:

1. No transaction date
2. No transaction code
3. No acquisition/disposition flag
4. No price information
5. Only contain position amounts (Column 5 for non-derivatives, Column 9 for derivatives)

## Database Implementation Challenges

### 1. Shared fields for different semantics

Our current implementation uses the same field (`shares_amount`) for two different purposes:
- For regular transactions: stores transaction amount (Column 4 for non-derivatives or Column 5 for derivatives)
- For position-only rows: stores total position (Column 5 for non-derivatives or Column 9 for derivatives)

This dual usage creates ambiguity and makes querying difficult.

### 2. Missing dedicated position columns

We need dedicated columns for:
- Regular transaction amount (Column 4 for non-derivatives or Column 5 for derivatives)
- Ending position amount (Column 5 for non-derivatives or Column 9 for derivatives)

### 3. Derivative vs. Non-Derivative Total Calculations

The `total_shares_owned` field in `form4_relationships` only represents non-derivative securities. We need an additional field for derivative securities, perhaps called `total_derivative_shares_owned`.

### 4. Underlying Securities Reporting

Derivative securities represent potential ownership of underlying securities. Column 7 (of Table II - Derivative Securities) indicates:
- The title of the underlying security (usually Common Stock)
- The amount of underlying securities received upon conversion

This needs to be clearly tracked in our model.

## Transaction Codes

Transaction codes have specific meanings:

| Code | Description | Notes |
|------|-------------|-------|
| P | Open market or private purchase | Often has non-zero price |
| S | Open market or private sale | Often has non-zero price |
| A | Grant, award, or other acquisition | Often has $0 price |
| D | Disposition to the issuer | Often has $0 price |
| M | Exercise or conversion of derivative security | | 
| C | Conversion of derivative security | |
| F | Payment of exercise price or tax liability | |
| I | Discretionary transaction | |
| J | Other acquisition or disposition | |
| K | Transaction in equity swap or similar instrument | |
| G | Gift | |
| V | Transaction voluntarily reported earlier than required | |
| X | Exercise of in-the-money derivative security | |

## Acquisition/Disposition Flag Differences

- **Non-Derivative Securities**: Single column with A/D flag
- **Derivative Securities**: Two subcolumns for Acquired (A) and Disposed (D)

## Proposed Database Enhancements

1. **Separate Tables for Non-Derivative and Derivative Transactions:**
   - `form4_non_derivative_transactions` - For Table I (non-derivative) transactions
   - `form4_derivative_transactions` - For Table II (derivative) transactions
   - Each table has fields specific to its transaction type
   - Clear separation of concerns and data models
   
   **Non-Derivative Fields:**
   - `transaction_shares` - Column 4 (transaction amount)
   - `shares_owned_following_transaction` - Column 5 (ending position)
   - Direct ownership fields specific to Table I
   
   **Derivative Fields:**
   - `derivative_units` - Column 5 (derivative transaction amount)
   - `derivative_units_owned_following_transaction` - Column 9 (ending derivative position)
   - `underlying_security_title` - Part of Column 7
   - `underlying_shares` - Part of Column 7
   - Fields for exercise/expiration dates specific to Table II

2. **New Column for Form4Relationship:**
   - `derivative_total_shares_owned` - Total derivative holdings
   - `non_derivative_total_shares_owned` - Total non-derivative holdings (rename from total_shares_owned)

3. **Position-Only Flag:**
   - `is_holding` boolean field to identify position-only rows

4. **Standardize Transaction Codes:**
   - Implement enum-based validation and interpretation
   - Add business logic for expected behavior by code

## Processing Logic Changes

1. **Position Calculation:**
   - Separate derivative from non-derivative calculation
   - Track history of positions for time-series analysis
   - Consider consequences of null transaction_code

2. **Transaction vs Position Distinction:**
   - Clear separation in parsing and storage
   - Consistent handling across derivative and non-derivative sections

3. **A/D Flag Handling:**
   - Standardize handling despite reporting differences
   - Apply consistent total calculation logic

## Migration Strategy

1. **Database Schema Restructuring:**
   - Create new separate transaction tables while maintaining the existing form4_transactions table
   - Add migration scripts to create the new tables and necessary indexes
   - Create views if needed for backward compatibility

2. **Model and Code Changes:**
   - Create new ORM models for each transaction type
   - Update parsers to populate both old tables and new separate tables
   - Create separate writer classes or methods for each transaction type
   - Update calculation logic to use the new structure

3. **Data Migration:**
   - Implement a script to migrate existing data to the new tables
   - Verify data integrity after migration 

4. **Testing and Documentation:**
   - Create comprehensive tests for the new structure
   - Update documentation to reflect the new model
   - Test with existing fixtures to ensure consistent behavior

5. **Transition:**
   - Support dual writing during transition period
   - Eventually deprecate the original form4_transactions table 
   - Provide transition documentation for users of the API

## XML files to reference

- File with non-derivative transactions: `tests\fixtures\000032012123000040_form4.xml`
- File with derivative transaction: `tests\fixtures\000106299323011116_form4.xml`