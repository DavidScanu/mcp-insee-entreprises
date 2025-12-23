# INSEE Entreprises MCP Server

Serveur MCP (Model Context Protocol) pour interroger l'API SIRENE de l'INSEE et rechercher des entreprises françaises.

## Fonctionnalités

Ce serveur MCP fournit plusieurs outils pour rechercher des entreprises :

### 🔍 Outils disponibles

1. **search_by_siren** - Recherche par numéro SIREN (9 chiffres)
   - Retourne les informations détaillées sur l'entité juridique

2. **search_by_siret** - Recherche par numéro SIRET (14 chiffres)
   - Retourne les informations détaillées sur l'établissement

3. **search_by_name** - Recherche par nom d'entreprise, adresse ou dirigeant
   - Supporte la recherche partielle et phonétique
   - Pagination disponible

4. **search_by_activity** - Recherche par code NAF/APE
   - Trouve toutes les entreprises avec l'activité spécifiée
   - Pagination disponible

5. **advanced_search** - Recherche avancée avec filtres multiples
   - Code postal
   - Code NAF/APE
   - Nombre d'employés (min/max)
   - Pagination disponible

## Installation

### Prérequis

- Python 3.12+
- uv (gestionnaire de paquets Python)

### Installation avec uv

```bash
cd /home/user/mcp-servers/insee-entreprises
uv sync
```

## Configuration

### Ajout au fichier de configuration Claude Desktop

Ajoutez ceci à votre configuration MCP (`~/Library/Application Support/Claude/claude_desktop_config.json` sur macOS ou `%APPDATA%\Claude\claude_desktop_config.json` sur Windows) :

```json
{
  "mcpServers": {
    "insee-entreprises": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/user/mcp-servers/insee-entreprises",
        "run",
        "insee-entreprises"
      ]
    }
  }
}
```

## Utilisation

Une fois le serveur configuré, vous pouvez l'utiliser dans Claude Desktop :

### Exemples de requêtes

1. **Recherche par SIREN**
   ```
   Trouve-moi les informations sur l'entreprise avec le SIREN 552032534
   ```

2. **Recherche par nom**
   ```
   Recherche les entreprises nommées "Carrefour"
   ```

3. **Recherche par dirigeant**
   ```
   Trouve les entreprises dirigées par "Jean Dupont"
   ```

4. **Recherche par activité**
   ```
   Liste les entreprises avec le code NAF 62.01Z (programmation informatique)
   ```

5. **Recherche avancée**
   ```
   Trouve les entreprises de programmation informatique à Paris avec plus de 50 employés
   ```

## Informations retournées

Pour chaque entreprise, le serveur retourne :

- **Identification** : SIREN, SIRET, dénomination sociale
- **Activité** : Code NAF/APE et libellé
- **Adresse** : Adresse complète du siège social
- **Statut** : Actif/Inactif
- **Effectifs** : Tranche d'effectif salarié
- **Dirigeants** : Liste des dirigeants et leur fonction

## API Utilisée

Ce serveur utilise l'**API Recherche d'Entreprises** maintenue par l'INSEE :
- Base URL : https://recherche-entreprises.api.gouv.fr
- Limite : 7 requêtes par seconde
- Disponibilité : 100%
- Accès : Ouvert (pas d'authentification requise)

## Limites

- L'API ne peut pas accéder aux :
  - Prédécesseurs/successeurs d'établissements
  - Entreprises non diffusibles
  - Rejets d'inscriptions RCS

## Support

Pour toute question ou problème :
- Documentation API : https://recherche-entreprises.api.gouv.fr/docs/
- Contact : Via https://annuaire-entreprises.data.gouv.fr/faq/parcours?question=contact

## Licence

MIT
