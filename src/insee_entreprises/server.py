#!/usr/bin/env python3
"""
MCP Server for INSEE SIRENE API.

Provides tools to search French enterprises using:
- SIREN (enterprise identifier) via official INSEE API
- SIRET (establishment identifier) via official INSEE API
- Advanced search with geographic and activity filters via Recherche Entreprises API
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent

from .section_mapping import get_section_code, list_all_sections
from .geo_mapping import (
    get_region_code,
    get_departement_code,
    get_commune_code,
    list_all_regions,
    list_all_departements
)

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("insee-entreprises")

# API Configuration
INSEE_API_BASE = "https://api.insee.fr/api-sirene/3.11"
INSEE_API_KEY = os.getenv("INSEE_API_KEY")
RECHERCHE_API_BASE = "https://recherche-entreprises.api.gouv.fr"

if not INSEE_API_KEY:
    logger.warning("INSEE_API_KEY not found in environment variables. SIREN/SIRET searches will fail.")

app = Server("insee-entreprises")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for enterprise search."""
    return [
        Tool(
            name="search_by_siren",
            description="Search enterprise by SIREN number (9 digits) using official INSEE API. Returns detailed and complete information about the legal entity (unité légale).",
            inputSchema={
                "type": "object",
                "properties": {
                    "siren": {
                        "type": "string",
                        "description": "9-digit SIREN number",
                        "pattern": "^[0-9]{9}$"
                    }
                },
                "required": ["siren"]
            }
        ),
        Tool(
            name="search_by_siret",
            description="Search establishment by SIRET number (14 digits) using official INSEE API. Returns detailed and complete information about the specific establishment (établissement).",
            inputSchema={
                "type": "object",
                "properties": {
                    "siret": {
                        "type": "string",
                        "description": "14-digit SIRET number",
                        "pattern": "^[0-9]{14}$"
                    }
                },
                "required": ["siret"]
            }
        ),
        Tool(
            name="search_entreprises",
            description="Advanced enterprise search with multiple filters including geographic criteria, activity sector/section, company name, and employee count. Use this for: searching by location (postal code, commune, department, region), industry/sector (Construction, Agriculture, etc.), company name, director name, address, employee count, or combining multiple criteria. Supports French activity section names (e.g., 'Construction', 'Information et communication') or codes (A-U).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for company name, address, or director name (optional)"
                    },
                    "code_postal": {
                        "type": "string",
                        "description": "Filter by postal code(s). Accepts comma-separated list (e.g., '75001,69002')"
                    },
                    "code_commune": {
                        "type": "string",
                        "description": "Filter by INSEE commune code(s). 5-character codes, comma-separated (e.g., '75056,69123')"
                    },
                    "departement": {
                        "type": "string",
                        "description": "Filter by department code(s). 2-3 digit codes, comma-separated (e.g., '75,69,974')"
                    },
                    "region": {
                        "type": "string",
                        "description": "Filter by region code(s). 2-digit codes, comma-separated (e.g., '11,84')"
                    },
                    "naf_code": {
                        "type": "string",
                        "description": "Filter by NAF/APE activity code (e.g., '62.01Z')"
                    },
                    "section_activite_principale": {
                        "type": "string",
                        "description": "Filter by activity section (A-U) or section name (e.g., 'Agriculture', 'Construction', 'Information et communication')"
                    },
                    "min_employees": {
                        "type": "integer",
                        "description": "Minimum number of employees"
                    },
                    "max_employees": {
                        "type": "integer",
                        "description": "Maximum number of employees"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "default": 1,
                        "minimum": 1
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Results per page (default: 10, max: 25)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 25
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for enterprise search."""
    try:
        if name == "search_by_siren":
            return await search_by_siren(arguments["siren"])
        elif name == "search_by_siret":
            return await search_by_siret(arguments["siret"])
        elif name == "search_entreprises":
            return await search_entreprises(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def search_by_siren(siren: str) -> list[TextContent]:
    """Search enterprise by SIREN using official INSEE API."""
    if not INSEE_API_KEY:
        return [TextContent(type="text", text="ERROR: INSEE_API_KEY not configured. Please add it to your .env file.")]

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{INSEE_API_BASE}/siren/{siren}"
        headers = {"X-INSEE-Api-Key-Integration": INSEE_API_KEY}

        response = await client.get(url, headers=headers)

        if response.status_code == 404:
            return [TextContent(type="text", text=f"No enterprise found with SIREN: {siren}")]

        response.raise_for_status()
        data = response.json()

        if "uniteLegale" not in data:
            return [TextContent(type="text", text=f"No enterprise found with SIREN: {siren}")]

        result = format_insee_unite_legale(data["uniteLegale"])
        return [TextContent(type="text", text=result)]


async def search_by_siret(siret: str) -> list[TextContent]:
    """Search establishment by SIRET using official INSEE API."""
    if not INSEE_API_KEY:
        return [TextContent(type="text", text="ERROR: INSEE_API_KEY not configured. Please add it to your .env file.")]

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{INSEE_API_BASE}/siret/{siret}"
        headers = {"X-INSEE-Api-Key-Integration": INSEE_API_KEY}

        response = await client.get(url, headers=headers)

        if response.status_code == 404:
            return [TextContent(type="text", text=f"No establishment found with SIRET: {siret}")]

        response.raise_for_status()
        data = response.json()

        if "etablissement" not in data:
            return [TextContent(type="text", text=f"No establishment found with SIRET: {siret}")]

        result = format_insee_etablissement(data["etablissement"])
        return [TextContent(type="text", text=result)]


async def search_entreprises(params: dict[str, Any]) -> list[TextContent]:
    """Perform advanced enterprise search with geographic and activity filters."""

    # Handle region parameter - convert name to code if needed
    if params.get("region"):
        region_input = params["region"].strip()
        # Check if already numeric code(s)
        if not region_input.replace(",", "").replace(" ", "").isdigit():
            # Try to convert name to code
            region_code = get_region_code(region_input)
            if not region_code:
                available_regions = list_all_regions()
                regions_list = "\n".join([f"  - {code}: {name}" for code, name in available_regions.items()])
                return [TextContent(
                    type="text",
                    text=f"Région invalide: '{region_input}'\n\nRégions disponibles:\n{regions_list}"
                )]
            params["region"] = region_code

    # Handle departement parameter - convert name to code if needed
    if params.get("departement"):
        dept_input = params["departement"].strip()
        # Check if already numeric/alphanumeric code(s) (2A, 2B for Corsica)
        is_code = all(part.strip().isdigit() or part.strip() in ["2A", "2B"]
                      for part in dept_input.split(","))
        if not is_code:
            # Try to convert name to code
            dept_code = get_departement_code(dept_input)
            if not dept_code:
                available_depts = list_all_departements()
                depts_list = "\n".join([f"  - {code}: {name}" for code, name in available_depts.items()])
                return [TextContent(
                    type="text",
                    text=f"Département invalide: '{dept_input}'\n\nDépartements disponibles:\n{depts_list}"
                )]
            params["departement"] = dept_code

    # Handle commune parameter - convert name to code if needed
    if params.get("code_commune"):
        commune_input = params["code_commune"].strip()
        # Check if already numeric code(s)
        if not commune_input.replace(",", "").replace(" ", "").isdigit():
            # Try to convert name to code
            # For communes, we might need département to disambiguate
            dept_for_commune = params.get("departement")
            commune_code = get_commune_code(commune_input, dept_for_commune)
            if not commune_code:
                error_msg = f"Commune invalide: '{commune_input}'"
                if not dept_for_commune:
                    error_msg += "\n\nNote: Plusieurs communes peuvent avoir le même nom. Spécifiez le département pour désambiguïser."
                return [TextContent(type="text", text=error_msg)]
            params["code_commune"] = commune_code

    # Handle section_activite_principale - convert label to code if needed
    if params.get("section_activite_principale"):
        section_input = params["section_activite_principale"].strip()

        # Check if it's already a valid section code (single letter A-U)
        if len(section_input) == 1 and section_input.upper() in "ABCDEFGHIJKLMNOPQRSTU":
            section_code = section_input.upper()
        else:
            # Try to convert section label to code
            section_code = get_section_code(section_input)
            if not section_code:
                available_sections = list_all_sections()
                sections_list = "\n".join([f"  - {code}: {label}" for code, label in available_sections.items()])
                return [TextContent(
                    type="text",
                    text=f"Invalid section: '{section_input}'\n\nAvailable sections:\n{sections_list}"
                )]

        params["section_activite_principale"] = section_code

    # Build query parts after all conversions
    query_parts = []

    if params.get("query"):
        query_parts.append(f"q={quote(params['query'])}")
    if params.get("code_postal"):
        query_parts.append(f"code_postal={params['code_postal']}")
    if params.get("code_commune"):
        query_parts.append(f"code_commune={params['code_commune']}")
    if params.get("departement"):
        query_parts.append(f"departement={params['departement']}")
    if params.get("region"):
        query_parts.append(f"region={params['region']}")
    if params.get("naf_code"):
        query_parts.append(f"activite_principale={quote(params['naf_code'])}")
    if params.get("section_activite_principale"):
        query_parts.append(f"section_activite_principale={params['section_activite_principale']}")
    if params.get("min_employees"):
        query_parts.append(f"tranche_effectif_salarie_min={params['min_employees']}")
    if params.get("max_employees"):
        query_parts.append(f"tranche_effectif_salarie_max={params['max_employees']}")

    page = params.get("page", 1)
    per_page = params.get("per_page", 10)
    query_parts.append(f"page={page}")
    query_parts.append(f"per_page={per_page}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{RECHERCHE_API_BASE}/search?{'&'.join(query_parts)}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            return [TextContent(type="text", text="No results found with the specified filters")]

        results = format_search_results(data, "advanced search")
        return [TextContent(type="text", text=results)]


def format_insee_unite_legale(unite_legale: dict[str, Any]) -> str:
    """Format INSEE API unité légale (enterprise) result."""
    lines = ["=" * 80]
    lines.append("UNITÉ LÉGALE (Enterprise)")
    lines.append("=" * 80)

    # Identifiers
    if unite_legale.get("siren"):
        lines.append(f"SIREN: {unite_legale['siren']}")

    # Company name
    periodesUniteLegale = unite_legale.get("periodesUniteLegale", [])
    if periodesUniteLegale:
        periode = periodesUniteLegale[0]
        if periode.get("denominationUniteLegale"):
            lines.append(f"Dénomination: {periode['denominationUniteLegale']}")
        elif periode.get("denominationUsuelle1UniteLegale"):
            lines.append(f"Dénomination usuelle: {periode['denominationUsuelle1UniteLegale']}")

        # Legal category
        if periode.get("categorieJuridiqueUniteLegale"):
            lines.append(f"Catégorie juridique: {periode['categorieJuridiqueUniteLegale']}")

        # Activity
        if periode.get("activitePrincipaleUniteLegale"):
            lines.append(f"Activité principale (NAF): {periode['activitePrincipaleUniteLegale']}")

        # Employee range
        if periode.get("trancheEffectifsUniteLegale"):
            lines.append(f"Tranche d'effectifs: {periode['trancheEffectifsUniteLegale']}")

        # Status
        if periode.get("etatAdministratifUniteLegale"):
            status = "Actif" if periode["etatAdministratifUniteLegale"] == "A" else "Inactif"
            lines.append(f"État administratif: {status}")

        # Dates
        if periode.get("dateDebut"):
            lines.append(f"Date de début: {periode['dateDebut']}")

    lines.append("=" * 80)
    return "\n".join(lines)


def format_insee_etablissement(etablissement: dict[str, Any]) -> str:
    """Format INSEE API établissement (establishment) result."""
    lines = ["=" * 80]
    lines.append("ÉTABLISSEMENT (Establishment)")
    lines.append("=" * 80)

    # Identifiers
    if etablissement.get("siret"):
        lines.append(f"SIRET: {etablissement['siret']}")
    if etablissement.get("siren"):
        lines.append(f"SIREN: {etablissement['siren']}")

    # Periods
    periodesEtablissement = etablissement.get("periodesEtablissement", [])
    if periodesEtablissement:
        periode = periodesEtablissement[0]

        # Address
        adresse = periode.get("adresseEtablissement", {})
        if adresse:
            address_parts = []
            if adresse.get("numeroVoieEtablissement"):
                address_parts.append(adresse["numeroVoieEtablissement"])
            if adresse.get("typeVoieEtablissement"):
                address_parts.append(adresse["typeVoieEtablissement"])
            if adresse.get("libelleVoieEtablissement"):
                address_parts.append(adresse["libelleVoieEtablissement"])
            if address_parts:
                lines.append(f"Adresse: {' '.join(address_parts)}")
            if adresse.get("codePostalEtablissement"):
                lines.append(f"Code postal: {adresse['codePostalEtablissement']}")
            if adresse.get("libelleCommuneEtablissement"):
                lines.append(f"Commune: {adresse['libelleCommuneEtablissement']}")

        # Activity
        if periode.get("activitePrincipaleEtablissement"):
            lines.append(f"Activité principale (NAF): {periode['activitePrincipaleEtablissement']}")

        # Status
        if periode.get("etatAdministratifEtablissement"):
            status = "Actif" if periode["etatAdministratifEtablissement"] == "A" else "Fermé"
            lines.append(f"État administratif: {status}")

        # Establishment type
        if periode.get("etablissementSiege"):
            siege = "Oui" if periode["etablissementSiege"] else "Non"
            lines.append(f"Établissement siège: {siege}")

        # Employee range
        if periode.get("trancheEffectifsEtablissement"):
            lines.append(f"Tranche d'effectifs: {periode['trancheEffectifsEtablissement']}")

    # Unit legale info
    uniteLegale = etablissement.get("uniteLegale", {})
    if uniteLegale:
        periodesUniteLegale = uniteLegale.get("periodesUniteLegale", [])
        if periodesUniteLegale:
            periodeUL = periodesUniteLegale[0]
            if periodeUL.get("denominationUniteLegale"):
                lines.append(f"\nDénomination de l'unité légale: {periodeUL['denominationUniteLegale']}")

    lines.append("=" * 80)
    return "\n".join(lines)


def format_enterprise_result(enterprise: dict[str, Any]) -> str:
    """Format a single enterprise result."""
    lines = ["=" * 80]
    
    # Basic information
    if enterprise.get("nom_complet"):
        lines.append(f"Company: {enterprise['nom_complet']}")
    if enterprise.get("nom_raison_sociale"):
        lines.append(f"Legal Name: {enterprise['nom_raison_sociale']}")
    
    # Identifiers
    if enterprise.get("siren"):
        lines.append(f"SIREN: {enterprise['siren']}")
    if enterprise.get("siret"):
        lines.append(f"SIRET: {enterprise['siret']}")
    
    # Activity
    if enterprise.get("activite_principale"):
        lines.append(f"NAF/APE Code: {enterprise['activite_principale']}")
    if enterprise.get("libelle_activite_principale"):
        lines.append(f"Activity: {enterprise['libelle_activite_principale']}")
    
    # Address
    siege = enterprise.get("siege", {})
    if siege:
        address_parts = []
        if siege.get("numero_voie"):
            address_parts.append(str(siege["numero_voie"]))
        if siege.get("type_voie"):
            address_parts.append(siege["type_voie"])
        if siege.get("libelle_voie"):
            address_parts.append(siege["libelle_voie"])
        if address_parts:
            lines.append(f"Address: {' '.join(address_parts)}")
        if siege.get("code_postal"):
            lines.append(f"Postal Code: {siege['code_postal']}")
        if siege.get("libelle_commune"):
            lines.append(f"City: {siege['libelle_commune']}")
    
    # Status
    if enterprise.get("etat_administratif"):
        status = "Active" if enterprise["etat_administratif"] == "A" else "Inactive"
        lines.append(f"Status: {status}")
    
    # Employees
    if enterprise.get("tranche_effectif_salarie"):
        lines.append(f"Employee Range: {enterprise['tranche_effectif_salarie']}")
    
    # Directors
    if enterprise.get("dirigeants"):
        lines.append("\nDirectors:")
        for dirigeant in enterprise["dirigeants"][:5]:
            if dirigeant.get("nom") or dirigeant.get("prenoms"):
                name = f"{dirigeant.get('prenoms', '')} {dirigeant.get('nom', '')}".strip()
                role = dirigeant.get("qualite", "")
                lines.append(f"  - {name} ({role})" if role else f"  - {name}")
    
    lines.append("=" * 80)
    return "\n".join(lines)


def format_search_results(data: dict[str, Any], query: str) -> str:
    """Format multiple search results."""
    total = data.get("total_results", 0)
    page = data.get("page", 1)
    per_page = data.get("per_page", 10)
    results = data.get("results", [])
    
    lines = [
        f"Search results for: {query}",
        f"Total results: {total} (showing page {page}, {len(results)} results)",
        "=" * 80
    ]
    
    for i, enterprise in enumerate(results, 1):
        lines.append(f"\n[{i}] {enterprise.get('nom_complet', 'N/A')}")
        lines.append(f"    SIREN: {enterprise.get('siren', 'N/A')}")
        lines.append(f"    SIRET: {enterprise.get('siret', 'N/A')}")
        
        if enterprise.get("activite_principale"):
            lines.append(f"    Activity: {enterprise.get('libelle_activite_principale', enterprise['activite_principale'])}")
        
        siege = enterprise.get("siege", {})
        if siege.get("code_postal") and siege.get("libelle_commune"):
            lines.append(f"    Location: {siege['code_postal']} {siege['libelle_commune']}")
        
        if enterprise.get("etat_administratif"):
            status = "Active" if enterprise["etat_administratif"] == "A" else "Inactive"
            lines.append(f"    Status: {status}")
    
    lines.append("\n" + "=" * 80)
    
    if total > page * per_page:
        lines.append(f"More results available. Use page={page + 1} to see the next page.")
    
    return "\n".join(lines)


async def async_main():
    """Run the MCP server asynchronously."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
