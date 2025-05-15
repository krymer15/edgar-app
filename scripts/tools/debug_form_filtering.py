# scripts/tools/debug_form_filtering.py

"""
Debug script for troubleshooting SEC form type filtering.
This script:
1. Connects to the database
2. Runs a query showing form type distribution
3. Simulates the same SQL filter that would be applied with --include_forms

Usage:
    python scripts/tools/debug_form_filtering.py --date 2025-05-12
    python scripts/tools/debug_form_filtering.py --date 2025-05-12 --include_forms 10-K 8-K
"""

import argparse
import sys, os
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import text

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from models.database import get_db_session
from models.orm_models.filing_metadata import FilingMetadata
from utils.form_type_validator import FormTypeValidator
from utils.report_logger import log_info, log_warn, log_error

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD.")

def show_form_distribution(session, date_str):
    """Show the distribution of form types for a given date"""
    query = text("""
        SELECT form_type, COUNT(*) as count
        FROM filing_metadata
        WHERE filing_date = :date
        GROUP BY form_type
        ORDER BY count DESC, form_type
    """)
    
    results = session.execute(query, {"date": date_str}).fetchall()
    
    if not results:
        log_warn(f"No records found for date: {date_str}")
        return []
    
    log_info(f"Form type distribution for {date_str}:")
    log_info("---------------------------------------")
    for form_type, count in results:
        log_info(f"{form_type:10} | {count:5}")
    
    return [r[0] for r in results]  # Return list of form types

def simulate_form_filtering(session, date_str, include_forms):
    """Simulate the SQL filtering that would be applied with --include_forms"""
    # Initial query that would typically filter for the date
    query = session.query(
        FilingMetadata.form_type,
        sa.func.count().label('count')
    ).filter(
        FilingMetadata.filing_date == date_str
    )
    
    # Add form type filter if specified
    if include_forms:
        query = query.filter(FilingMetadata.form_type.in_(include_forms))
    
    # Group by form type and order by count
    query = query.group_by(FilingMetadata.form_type).order_by(
        sa.desc('count'),
        FilingMetadata.form_type
    )
    
    # Get results
    results = query.all()
    
    # Display results
    log_info(f"Results with form filtering - include_forms={include_forms}:")
    log_info("---------------------------------------")
    for row in results:
        log_info(f"{row.form_type:10} | {row.count:5}")
    
    return results

def verify_filtering(all_forms, filtered_results, include_forms):
    """Verify the filtering is working as expected"""
    filtered_forms = [r[0] for r in filtered_results]
    
    log_info("\nFiltering Verification:")
    log_info("---------------------------------------")
    
    # Check if all forms in results are in the include_forms list
    all_included = all(form in include_forms for form in filtered_forms)
    log_info(f"All results are in include_forms list: {'✅' if all_included else '❌'}")
    
    # Check if any forms might be missing from the results
    missing_forms = [form for form in include_forms if form in all_forms and form not in filtered_forms]
    if missing_forms:
        log_warn(f"Forms in include_forms but not in results: {missing_forms}")
    else:
        log_info(f"All applicable forms from include_forms are in results: ✅")
    
    # Check for form normalization issues
    normalized_forms = FormTypeValidator.normalize_form_types(include_forms)
    if normalized_forms != include_forms:
        log_warn(f"Form normalization changed the forms:")
        for original, normalized in zip(include_forms, normalized_forms):
            if original != normalized:
                log_warn(f"  {original} -> {normalized}")
    
    return all_included

def main():
    parser = argparse.ArgumentParser(description="Debug SEC form type filtering")
    parser.add_argument("--date", type=validate_date, required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--include_forms", nargs="*", help="Form types to include (e.g. 10-K 8-K)")

    args = parser.parse_args()
    
    # Validate and normalize form types if provided
    validated_forms = None
    if args.include_forms:
        validated_forms = FormTypeValidator.get_validated_form_types(args.include_forms)
        log_info(f"Validated form types: {validated_forms}")
        
        # Show the original vs. normalized forms
        if args.include_forms != validated_forms:
            log_info("Forms were normalized:")
            for i, (orig, norm) in enumerate(zip(args.include_forms, validated_forms)):
                if orig != norm:
                    log_info(f"  {orig} -> {norm}")

    try:
        with get_db_session() as session:
            # Get all form types for the date
            all_forms = show_form_distribution(session, args.date)
            
            if not all_forms:
                log_warn(f"No filing metadata records found for {args.date}")
                return
            
            # If include_forms is provided, simulate the filtering
            if validated_forms:
                log_info("")  # Empty line for readability
                filtered_results = simulate_form_filtering(session, args.date, validated_forms)
                
                # Verify the filtering
                if filtered_results:
                    log_info("")  # Empty line for readability
                    verify_filtering(all_forms, filtered_results, validated_forms)
                else:
                    log_warn(f"No results found with the specified form filters: {validated_forms}")
    
    except Exception as e:
        log_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()