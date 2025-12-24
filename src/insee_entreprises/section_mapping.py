"""
NAF Section Mapping Service.

Provides mapping between section labels (e.g., "Agriculture") and their codes (A-U).
"""

import csv
from pathlib import Path
from typing import Dict, Optional

# Cache for section mappings
_SECTION_CACHE: Optional[Dict[str, str]] = None
_REVERSE_CACHE: Optional[Dict[str, str]] = None


def _load_sections() -> tuple[Dict[str, str], Dict[str, str]]:
    """Load section mappings from CSV file."""
    global _SECTION_CACHE, _REVERSE_CACHE

    if _SECTION_CACHE is not None and _REVERSE_CACHE is not None:
        return _SECTION_CACHE, _REVERSE_CACHE

    # Get path to data file
    data_dir = Path(__file__).parent / "data"
    csv_path = data_dir / "naf_niveau_1.csv"

    label_to_code: Dict[str, str] = {}
    code_to_label: Dict[str, str] = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["Code"].strip()
            label = row["Libellé"].strip()

            # Store both mappings
            code_to_label[code] = label
            label_to_code[label.lower()] = code

    _SECTION_CACHE = label_to_code
    _REVERSE_CACHE = code_to_label

    return _SECTION_CACHE, _REVERSE_CACHE


def get_section_code(section_label: str) -> Optional[str]:
    """
    Get section code from label.

    Args:
        section_label: Section label (e.g., "Agriculture" or "agriculture, sylviculture et pêche")

    Returns:
        Section code (A-U) or None if not found
    """
    label_to_code, _ = _load_sections()

    # Try exact match first (case insensitive)
    label_lower = section_label.lower().strip()
    if label_lower in label_to_code:
        return label_to_code[label_lower]

    # Try partial match
    for label, code in label_to_code.items():
        if label_lower in label or label in label_lower:
            return code

    return None


def get_section_label(section_code: str) -> Optional[str]:
    """
    Get section label from code.

    Args:
        section_code: Section code (A-U)

    Returns:
        Section label or None if not found
    """
    _, code_to_label = _load_sections()
    return code_to_label.get(section_code.upper().strip())


def list_all_sections() -> Dict[str, str]:
    """
    Get all available sections.

    Returns:
        Dictionary mapping codes to labels
    """
    _, code_to_label = _load_sections()
    return code_to_label.copy()


def is_valid_section_code(section_code: str) -> bool:
    """
    Check if a section code is valid.

    Args:
        section_code: Section code to validate

    Returns:
        True if valid, False otherwise
    """
    _, code_to_label = _load_sections()
    return section_code.upper().strip() in code_to_label