# Archive for notebook or testing use

import os
import json
from typing import List
from utils.get_project_root import get_project_root

def save_html_to_file(content: str, filepath: str) -> None:
    """
    Saves raw HTML content to a file.

    Args:
        content (str): The HTML content to save.
        filepath (str): The path where the file will be saved.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        if not os.path.isabs(filepath):
            filepath = os.path.join(get_project_root(), filepath)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Failed to save HTML to {filepath}: {e}")

def save_text_blocks_to_file(blocks: List[str], filepath: str) -> None:
    """
    Saves a list of cleaned text blocks to a file.

    Each block is separated by two newlines for readability.

    Args:
        blocks (List[str]): List of text blocks.
        filepath (str): The path where the file will be saved.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        if not os.path.isabs(filepath):
            filepath = os.path.join(get_project_root(), filepath)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            for block in blocks:
                f.write(block.strip())
                f.write("\n\n")  # Separate blocks with two newlines
    except Exception as e:
        raise IOError(f"Failed to save text blocks to {filepath}: {e}")

def save_metadata_to_json(metadata: dict, filepath: str) -> None:
    """
    Saves metadata dictionary to a JSON file.

    Args:
        metadata (dict): Metadata to save.
        filepath (str): The path where the file will be saved.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        if not os.path.isabs(filepath):
            filepath = os.path.join(get_project_root(), filepath)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
    except Exception as e:
        raise IOError(f"Failed to save metadata to {filepath}: {e}")
