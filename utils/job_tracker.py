# utils/job_tracker.py

import uuid
from datetime import datetime
from typing import Dict, Optional, List
from sqlalchemy import func
from models.database import get_db_session
from models.orm_models.filing_metadata import FilingMetadata
from utils.report_logger import log_info, log_error

def create_job(target_date: str, description: Optional[str] = None) -> str:
    """
    Create a new processing job for tracking.
    
    Args:
        target_date: The date being processed
        description: Optional description of the job
        
    Returns:
        str: The job ID
    """
    job_id = str(uuid.uuid4())
    
    with get_db_session() as session:
        # Count total records available for the date
        total_records = session.query(func.count(FilingMetadata.accession_number))\
            .filter(FilingMetadata.filing_date == target_date)\
            .scalar() or 0
        
        # Create job metadata in the database (if using a job_metadata table)
        # For simplicity, we'll just log the job creation for now
        log_info(f"Created job {job_id} for date {target_date} with {total_records} records")
        
    return job_id

def get_job_progress(job_id: str) -> Dict:
    """
    Get progress information for a job.
    
    Args:
        job_id: The job ID
        
    Returns:
        Dict: Job progress information
    """
    with get_db_session() as session:
        # Count records by status
        results = session.query(
                FilingMetadata.processing_status, 
                func.count(FilingMetadata.accession_number)
            )\
            .filter(FilingMetadata.job_id == job_id)\
            .group_by(FilingMetadata.processing_status)\
            .all()
        
        # Convert to dictionary
        status_counts = {status: count for status, count in results}
        
        # Calculate total
        total = sum(status_counts.values())
        completed = status_counts.get('completed', 0)
        failed = status_counts.get('failed', 0)
        processing = status_counts.get('processing', 0)
        pending = status_counts.get('pending', 0) + status_counts.get(None, 0)
        
        return {
            'job_id': job_id,
            'total': total,
            'completed': completed,
            'failed': failed,
            'processing': processing,
            'pending': pending,
            'progress_pct': (completed / total * 100) if total else 0
        }

def update_record_status(accession_number: str, status: str, error: Optional[str] = None) -> bool:
    """
    Update the processing status of a record.
    
    Args:
        accession_number: The accession number
        status: The new status ('pending', 'processing', 'completed', 'failed', 'skipped')
        error: Optional error message for failed records
        
    Returns:
        bool: True if successful, False otherwise
    """
    valid_statuses = ['pending', 'processing', 'completed', 'failed', 'skipped']
    
    if status not in valid_statuses:
        log_error(f"Invalid status: {status}. Valid statuses are: {valid_statuses}")
        return False
        
    try:
        with get_db_session() as session:
            record = session.query(FilingMetadata)\
                .filter(FilingMetadata.accession_number == accession_number)\
                .first()
            
            if not record:
                log_error(f"Record not found: {accession_number}")
                return False
            
            record.processing_status = status
            
            if status == 'processing':
                record.processing_started_at = datetime.now()
            elif status == 'completed':
                record.processing_completed_at = datetime.now()
            elif status == 'failed':
                record.processing_error = error
            
            session.commit()
            return True
    except Exception as e:
        log_error(f"Failed to update record status: {e}")
        return False

def update_batch_status(accession_numbers: List[str], status: str) -> bool:
    """
    Update the processing status of multiple records.
    
    Args:
        accession_numbers: List of accession numbers
        status: The new status
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_session() as session:
            timestamp = datetime.now()
            
            if status == 'processing':
                session.query(FilingMetadata)\
                    .filter(FilingMetadata.accession_number.in_(accession_numbers))\
                    .update({
                        "processing_status": status,
                        "processing_started_at": timestamp
                    }, synchronize_session=False)
            elif status == 'completed':
                session.query(FilingMetadata)\
                    .filter(FilingMetadata.accession_number.in_(accession_numbers))\
                    .update({
                        "processing_status": status,
                        "processing_completed_at": timestamp
                    }, synchronize_session=False)
            else:
                session.query(FilingMetadata)\
                    .filter(FilingMetadata.accession_number.in_(accession_numbers))\
                    .update({
                        "processing_status": status
                    }, synchronize_session=False)
            
            session.commit()
            return True
    except Exception as e:
        log_error(f"Failed to update batch status: {e}")
        return False