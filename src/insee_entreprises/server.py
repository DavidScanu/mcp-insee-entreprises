#!/usr/bin/env python3
"""
MCP Server for INSEE SIRENE API.

Provides tools to search French enterprises using:
- SIREN (enterprise identifier)
- SIRET (establishment identifier)
- Company name (denomination)
- Director name (dirigeant)
- Activity code (NAF/APE)
"""

import asyncio
import logging
from typing import Any
from urllib.parse import quote

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("insee-entreprises")

# API Configuration
SIRENE_API_BASE = "https://api.insee.fr/entreprises/sirene/V3.11"
RECHERCHE_API_BASE = "https://recherche-entreprises.api.gouv.fr"

app = Server("insee-entreprises")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for enterprise search."""
    return [
        Tool(
            name="search_by_siren",
            description="Search enterprise by SIREN number (9 digits). Returns detailed information about the legal entity.",
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
            description="Search establishment by SIRET number (14 digits). Returns detailed information about the specific establishment.",
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
            name="search_by_name",
            description="Search enterprises by company name, address, or director name. Supports partial matches and phonetic search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (company name, address, director name, etc.)"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
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
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_by_activity",
            description="Search enterprises by NAF/APE activity code. Returns all enterprises with the specified activity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "naf_code": {
                        "type": "string",
                        "description": "NAF/APE activity code (e.g., '62.01Z' for computer programming)"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
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
                },
                "required": ["naf_code"]
            }
        ),
        Tool(
            name="advanced_search",
            description="Advanced search with multiple filters: postal code, employee count, NAF code, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Main search term (optional)"
                    },
                    "postal_code": {
                        "type": "string",
                        "description": "Filter by postal code"
                    },
                    "naf_code": {
                        "type": "string",
                        "description": "Filter by NAF/APE activity code"
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
        elif name == "search_by_name":
            return await search_by_name(
                arguments["query"],
                arguments.get("page", 1),
                arguments.get("per_page", 10)
            )
        elif name == "search_by_activity":
            return await search_by_activity(
                arguments["naf_code"],
                arguments.get("page", 1),
                arguments.get("per_page", 10)
            )
        elif name == "advanced_search":
            return await advanced_search(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def search_by_siren(siren: str) -> list[TextContent]:
    """Search enterprise by SIREN using Recherche Entreprises API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{RECHERCHE_API_BASE}/search?q={siren}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return [TextContent(type="text", text=f"No enterprise found with SIREN: {siren}")]
        
        result = format_enterprise_result(data["results"][0])
        return [TextContent(type="text", text=result)]


async def search_by_siret(siret: str) -> list[TextContent]:
    """Search establishment by SIRET using Recherche Entreprises API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{RECHERCHE_API_BASE}/search?q={siret}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return [TextContent(type="text", text=f"No establishment found with SIRET: {siret}")]
        
        result = format_enterprise_result(data["results"][0])
        return [TextContent(type="text", text=result)]


async def search_by_name(query: str, page: int = 1, per_page: int = 10) -> list[TextContent]:
    """Search enterprises by name, address, or director."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{RECHERCHE_API_BASE}/search?q={quote(query)}&page={page}&per_page={per_page}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return [TextContent(type="text", text=f"No results found for: {query}")]
        
        results = format_search_results(data, query)
        return [TextContent(type="text", text=results)]


async def search_by_activity(naf_code: str, page: int = 1, per_page: int = 10) -> list[TextContent]:
    """Search enterprises by NAF/APE activity code."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{RECHERCHE_API_BASE}/search?activite_principale={quote(naf_code)}&page={page}&per_page={per_page}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return [TextContent(type="text", text=f"No enterprises found with NAF code: {naf_code}")]
        
        results = format_search_results(data, f"NAF code {naf_code}")
        return [TextContent(type="text", text=results)]


async def advanced_search(params: dict[str, Any]) -> list[TextContent]:
    """Perform advanced search with multiple filters."""
    query_parts = []
    
    if params.get("query"):
        query_parts.append(f"q={quote(params['query'])}")
    if params.get("postal_code"):
        query_parts.append(f"code_postal={params['postal_code']}")
    if params.get("naf_code"):
        query_parts.append(f"activite_principale={quote(params['naf_code'])}")
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
