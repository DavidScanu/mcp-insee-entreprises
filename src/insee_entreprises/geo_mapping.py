"""
Geographic Code Mapping Service.

Provides mapping between geographic entity names and their official INSEE codes.
Supports regions (2-digit codes), départements (2-3 digit codes), and communes (5-char codes).
Data source: INSEE Code Officiel Géographique (COG) 2025.
"""

import csv
from pathlib import Path
from typing import Dict, Optional, Tuple, List

# Module-level caches
_REGION_CACHE: Optional[Dict[str, str]] = None
_REGION_REVERSE_CACHE: Optional[Dict[str, str]] = None
_DEPARTEMENT_CACHE: Optional[Dict[str, str]] = None
_DEPARTEMENT_REVERSE_CACHE: Optional[Dict[str, str]] = None
_COMMUNE_CACHE: Optional[Dict[str, Tuple[str, str]]] = None  # name -> (code, dept_code)
_COMMUNE_REVERSE_CACHE: Optional[Dict[str, str]] = None


def _load_regions() -> tuple[Dict[str, str], Dict[str, str]]:
    """Load region mappings from CSV file."""
    global _REGION_CACHE, _REGION_REVERSE_CACHE

    if _REGION_CACHE is not None and _REGION_REVERSE_CACHE is not None:
        return _REGION_CACHE, _REGION_REVERSE_CACHE

    # Get path to data file
    data_dir = Path(__file__).parent / "data"
    csv_path = data_dir / "v_region_2025.csv"

    name_to_code: Dict[str, str] = {}
    code_to_name: Dict[str, str] = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["REG"].strip()
            name = row["NCCENR"].strip()  # Nom en clair enrichi

            # Store both mappings
            code_to_name[code] = name
            name_to_code[name.lower()] = code

    _REGION_CACHE = name_to_code
    _REGION_REVERSE_CACHE = code_to_name

    return _REGION_CACHE, _REGION_REVERSE_CACHE


def _load_departements() -> tuple[Dict[str, str], Dict[str, str]]:
    """Load département mappings from CSV file."""
    global _DEPARTEMENT_CACHE, _DEPARTEMENT_REVERSE_CACHE

    if _DEPARTEMENT_CACHE is not None and _DEPARTEMENT_REVERSE_CACHE is not None:
        return _DEPARTEMENT_CACHE, _DEPARTEMENT_REVERSE_CACHE

    # Get path to data file
    data_dir = Path(__file__).parent / "data"
    csv_path = data_dir / "v_departement_2025.csv"

    name_to_code: Dict[str, str] = {}
    code_to_name: Dict[str, str] = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["DEP"].strip()
            name = row["NCCENR"].strip()  # Nom en clair enrichi

            # Store both mappings
            code_to_name[code] = name
            name_to_code[name.lower()] = code

    _DEPARTEMENT_CACHE = name_to_code
    _DEPARTEMENT_REVERSE_CACHE = code_to_name

    return _DEPARTEMENT_CACHE, _DEPARTEMENT_REVERSE_CACHE


def _load_communes() -> tuple[Dict[str, List[Tuple[str, str]]], Dict[str, str]]:
    """
    Load commune mappings from CSV file.

    Returns:
        Tuple of (name_to_codes, code_to_name) where:
        - name_to_codes: Maps lowercase commune name to list of (code, dept_code) tuples
        - code_to_name: Maps commune code to name
    """
    global _COMMUNE_CACHE, _COMMUNE_REVERSE_CACHE

    if _COMMUNE_CACHE is not None and _COMMUNE_REVERSE_CACHE is not None:
        return _COMMUNE_CACHE, _COMMUNE_REVERSE_CACHE

    # Get path to data file
    data_dir = Path(__file__).parent / "data"
    csv_path = data_dir / "v_commune_2025.csv"

    name_to_codes: Dict[str, List[Tuple[str, str]]] = {}
    code_to_name: Dict[str, str] = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only process actual communes (type "COM")
            if row["TYPECOM"] != "COM":
                continue

            code = row["COM"].strip()
            name = row["NCCENR"].strip()  # Nom en clair enrichi
            dept_code = row["DEP"].strip()

            # Store reverse mapping (code to name)
            code_to_name[code] = name

            # Store forward mapping (name to codes)
            # Multiple communes can have same name
            name_lower = name.lower()
            if name_lower not in name_to_codes:
                name_to_codes[name_lower] = []
            name_to_codes[name_lower].append((code, dept_code))

    _COMMUNE_CACHE = name_to_codes
    _COMMUNE_REVERSE_CACHE = code_to_name

    return _COMMUNE_CACHE, _COMMUNE_REVERSE_CACHE


def get_region_code(region_name: str) -> Optional[str]:
    """
    Get region code from name.

    Args:
        region_name: Region name (e.g., "Auvergne-Rhône-Alpes")

    Returns:
        Region code (2 digits) or None if not found
    """
    name_to_code, _ = _load_regions()

    # Try exact match first (case insensitive)
    name_lower = region_name.lower().strip()
    if name_lower in name_to_code:
        return name_to_code[name_lower]

    # Try partial match
    for name, code in name_to_code.items():
        if name_lower in name or name in name_lower:
            return code

    return None


def get_region_name(region_code: str) -> Optional[str]:
    """
    Get region name from code.

    Args:
        region_code: Region code (2 digits)

    Returns:
        Region name or None if not found
    """
    _, code_to_name = _load_regions()
    return code_to_name.get(region_code.strip())


def get_departement_code(dept_name: str) -> Optional[str]:
    """
    Get département code from name.

    Args:
        dept_name: Département name (e.g., "Isère", "Rhône")

    Returns:
        Département code (2-3 digits) or None if not found
    """
    name_to_code, _ = _load_departements()

    # Try exact match first (case insensitive)
    name_lower = dept_name.lower().strip()
    if name_lower in name_to_code:
        return name_to_code[name_lower]

    # Try partial match
    for name, code in name_to_code.items():
        if name_lower in name or name in name_lower:
            return code

    return None


def get_departement_name(dept_code: str) -> Optional[str]:
    """
    Get département name from code.

    Args:
        dept_code: Département code (2-3 digits or 2A/2B for Corsica)

    Returns:
        Département name or None if not found
    """
    _, code_to_name = _load_departements()
    return code_to_name.get(dept_code.strip())


def get_commune_code(commune_name: str, departement: Optional[str] = None) -> Optional[str]:
    """
    Get commune code from name.

    Args:
        commune_name: Commune name (e.g., "Grenoble", "Lyon")
        departement: Optional département code or name to disambiguate (e.g., "38" or "Isère")

    Returns:
        Commune code (5 characters) or None if not found or ambiguous
    """
    name_to_codes, _ = _load_communes()

    # Try exact match first (case insensitive)
    name_lower = commune_name.lower().strip()

    if name_lower not in name_to_codes:
        # Try partial match
        matches = []
        for name, codes in name_to_codes.items():
            if name_lower in name or name in name_lower:
                matches.extend(codes)

        if not matches:
            return None

        codes_list = matches
    else:
        codes_list = name_to_codes[name_lower]

    # If no département specified and multiple matches, return None (ambiguous)
    if not departement and len(codes_list) > 1:
        return None

    # If département specified, filter by département
    if departement:
        dept_code = departement.strip()

        # If département is a name, convert to code
        if not dept_code.isdigit() and dept_code not in ["2A", "2B"]:
            dept_code = get_departement_code(departement)
            if not dept_code:
                return None

        # Find commune in specified département
        for code, dept in codes_list:
            if dept == dept_code:
                return code

        return None

    # Single match found
    if len(codes_list) == 1:
        return codes_list[0][0]

    return None


def get_commune_name(commune_code: str) -> Optional[str]:
    """
    Get commune name from code.

    Args:
        commune_code: Commune code (5 characters)

    Returns:
        Commune name or None if not found
    """
    _, code_to_name = _load_communes()
    return code_to_name.get(commune_code.strip())


def list_all_regions() -> Dict[str, str]:
    """
    Get all available regions.

    Returns:
        Dictionary mapping codes to names
    """
    _, code_to_name = _load_regions()
    return code_to_name.copy()


def list_all_departements() -> Dict[str, str]:
    """
    Get all available départements.

    Returns:
        Dictionary mapping codes to names
    """
    _, code_to_name = _load_departements()
    return code_to_name.copy()


def search_communes(name_pattern: str, departement: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Search communes by name pattern.

    Args:
        name_pattern: Partial or full commune name to search for
        departement: Optional département code or name to filter results

    Returns:
        List of dictionaries with 'code', 'name', and 'departement' keys
    """
    name_to_codes, code_to_name = _load_communes()
    pattern_lower = name_pattern.lower().strip()

    results = []
    dept_code_filter = None

    # If département specified, convert to code if needed
    if departement:
        dept_code_filter = departement.strip()
        if not dept_code_filter.isdigit() and dept_code_filter not in ["2A", "2B"]:
            dept_code_filter = get_departement_code(departement)
            if not dept_code_filter:
                return []

    # Search in all communes
    for name, codes_list in name_to_codes.items():
        if pattern_lower in name:
            for code, dept in codes_list:
                # Filter by département if specified
                if dept_code_filter and dept != dept_code_filter:
                    continue

                results.append({
                    "code": code,
                    "name": code_to_name[code],
                    "departement": dept
                })

    return results
