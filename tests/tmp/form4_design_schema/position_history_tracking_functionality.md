# Position History Tracking: Core Concepts (REFERENCE)

This document contains core concepts for position tracking that complement the implementation details in `phase3_implementation.md`. It is meant as a reference for understanding the position tracking model.

## Position Tracking Principles

The position tracking system relies on the following components:

1. **Relationship Positions Table**: Stores point-in-time position data linked to relationships, securities, and optionally transactions
2. **Position Calculation Logic**: Determines the impact of transactions on positions
3. **Position Service**: Provides methods for querying and managing positions
4. **Auditable History**: Maintains a complete history of position changes

## Position Query Types

The service will provide methods for querying positions in various ways:

1. **Current Position**: Get the latest position for a relationship and security
2. **Position History**: Get a time series of positions for analysis
3. **Position Snapshot**: Get all positions as of a specific date
4. **Insider Ownership**: Get all insider positions for an issuer

These methods support both application logic and GUI displays.

## Transaction-Position Integration

Position history is automatically updated when transactions are processed:

1. When a new transaction is created, the position service should be called
2. The position service calculates the new position amount based on:
   - The previous position (if any)
   - The transaction's impact (acquisition or disposition)
3. A new position record is created with the updated amount

This keeps the position history in sync with transactions and provides an accurate audit trail.