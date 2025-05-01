# utils/path_utils.py

'''
For building paths to save to /Data/
We support both accession_number and accessionNumber keys because Submissions and DailyIndex have slightly different casing.
'''

def build_path_args(metadata: dict, filename: str):
    """
    Build (year, cik, form_type, accession_or_subtype, filename) tuple for storage paths such as: build_raw_filepath().
    """
    return (
        metadata["filing_date"][:4],
        metadata["cik"],
        metadata["form_type"],
        metadata.get("accession_number") or metadata.get("accessionNumber"),
        filename
    )
