#!/bin/bash
# Exemples de requêtes pour l'API INSEE Sirene

# Load API key from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found at $ENV_FILE"
    echo "Please create a .env file with your INSEE_API_KEY"
    echo "Example: INSEE_API_KEY=your_key_here"
    exit 1
fi

# Extract API key from .env file
API_KEY=$(grep "^INSEE_API_KEY=" "$ENV_FILE" | cut -d '=' -f2-)

if [ -z "$API_KEY" ]; then
    echo "ERROR: INSEE_API_KEY not found in .env file"
    echo "Please add: INSEE_API_KEY=your_key_here"
    exit 1
fi

echo "✓ API Key loaded from .env file"
echo ""

# ============================================
# API INSEE Sirene (Officielle)
# ============================================

echo "=== Recherche par SIREN (Unité Légale) ==="
# Exemple: SCI PAMADAIR (SIREN: 377709449)
curl -X 'GET' \
  "https://api.insee.fr/api-sirene/3.11/siren/377709449" \
  -H 'accept: application/json' \
  -H "X-INSEE-Api-Key-Integration: $API_KEY" | jq | head -n 50

echo -e "\n=== Recherche par SIRET (Établissement) ==="
# Exemple: SIRET 37770944900017
curl -X 'GET' \
  "https://api.insee.fr/api-sirene/3.11/siret/67205008502051" \
  -H 'accept: application/json' \
  -H "X-INSEE-Api-Key-Integration: $API_KEY" | jq | head -n 50


# ============================================
# API Recherche d'Entreprises (Publique)
# ============================================

echo -e "\n=== Recherche avancée: Construction à Paris ==="
curl -X 'GET' \
  "https://recherche-entreprises.api.gouv.fr/search?section_activite_principale=F&code_postal=75001&per_page=5" \
  -H 'accept: application/json' | jq | head -n 50

echo -e "\n=== Recherche par nom: Carrefour ==="
curl -X 'GET' \
  "https://recherche-entreprises.api.gouv.fr/search?q=carrefour&per_page=5" \
  -H 'accept: application/json' | jq | head -n 50

echo -e "\n=== Recherche par code NAF: 62.01Z (Programmation informatique) ==="
curl -X 'GET' \
  "https://recherche-entreprises.api.gouv.fr/search?activite_principale=62.01Z&per_page=5" \
  -H 'accept: application/json' | jq | head -n 50

# ============================================
# Métadonnées et documentation
# ============================================

echo -e "\n=== OpenAPI Specification (INSEE Sirene) ==="
echo "Téléchargement du schéma OpenAPI YAML depuis la documentation INSEE..."
mkdir -p openapi_schemas
curl -s -L 'https://api-apimanager.insee.fr/portal/environments/DEFAULT/apis/2ba0e549-5587-3ef1-9082-99cd865de66f/pages/6548510e-c3e1-3099-be96-6edf02870699/content' -o openapi_schemas/openapi_insee_sirene.yaml
echo "Conversion du YAML en JSON..."
if command -v yq >/dev/null 2>&1; then
  yq -o=json openapi_schemas/openapi_insee_sirene.yaml > openapi_schemas/openapi_insee_sirene.json
  echo "Saved to: openapi_schemas/openapi_insee_sirene.json"
else
  echo "Erreur : yq n'est pas installé. Installez-le pour convertir YAML en JSON."
fi

echo -e "\n=== OpenAPI Specification (Recherche Entreprises) ==="
echo "Téléchargement du schéma OpenAPI JSON depuis l'API Recherche d'Entreprises..."
mkdir -p openapi_schemas
curl -X 'GET' \
  'https://recherche-entreprises.api.gouv.fr/openapi.json' \
  -H 'accept: application/json' | jq '.' > openapi_schemas/openapi_recherche_entreprises.json
echo "Saved to: openapi_schemas/openapi_recherche_entreprises.json"