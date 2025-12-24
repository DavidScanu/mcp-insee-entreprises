# INSEE Entreprises MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2.svg)](https://claude.com/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API SIRENE](https://img.shields.io/badge/API-SIRENE%20INSEE-red.svg)](https://www.data.gouv.fr/dataservices/api-recherche-dentreprises)

Serveur MCP (Model Context Protocol) pour interroger l'**API SIRENE** de l'INSEE et rechercher des entreprises françaises.

## Fonctionnalités

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
   - Section d'activité (A-U)
   - Nombre d'employés (min/max)
   - Pagination disponible

## Prérequis

- Python 3.12+
- uv (gestionnaire de paquets Python)

### Installer UV 

Pour installer `uv`, exécutez la commande suivante :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Pour plus d'informations, consultez la documentation officielle : https://astral.sh/uv/docs/getting-started/installation

Pour vérifier l'installation, exécutez :

```bash
uv --version
```  

Pour connaitre le chemin d'installation de `uv`, exécutez :

```bash
which uv
```

Pour ajouter `uv` à votre variable d'environnement PATH, ajoutez la ligne suivante à votre fichier de configuration de shell (`~/.bashrc`, `~/.zshrc`, etc.) :

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Après avoir modifié ce fichier, rechargez la configuration du shell avec :

```bash
source ~/.bashrc
```

## Installation du serveur MCP

1. **Cloner le dépôt** (si ce n'est pas déjà fait) :
```bash
git clone git@github.com:DavidScanu/mcp-insee-entreprises.git
cd mcp-insee-entreprises
```

2. **Installer les dépendances avec uv** :
```bash
uv sync
```

3. **Ajouter le serveur MCP à Claude Code** (scope user) :

```bash
claude mcp add --transport stdio insee-entreprises --scope user -- uv --directory <chemin/absolu/vers/mcp-insee-entreprises> run insee-entreprises
```

> **Note** : Remplacez `<chemin/absolu/vers/mcp-insee-entreprises>` par le chemin absolu vers votre installation du serveur.

**Alternative si `uv` n'est pas dans votre PATH** :

Si la commande `uv` n'est pas reconnue, utilisez le chemin complet vers `uv` (généralement `~/.local/bin/uv` ou `~/.cargo/bin/uv`) :

```bash
claude mcp add --transport stdio insee-entreprises --scope user -- ~/.local/bin/uv --directory <chemin/absolu/vers/mcp-insee-entreprises> run insee-entreprises
```

Pour trouver le chemin complet vers `uv`, utilisez :
```bash
which uv
```

4. **Vérifier l'installation** :
```bash
claude mcp list
```

### Installation manuelle (alternative)

Si vous préférez configurer manuellement, ajoutez ceci à votre fichier `~/.claude.json` :

```json
{
  "mcpServers": {
    "insee-entreprises": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/david/mcp-servers/mcp-insee-entreprises",
        "run",
        "insee-entreprises"
      ]
    }
  }
}
```

**Si `uv` n'est pas dans votre PATH**, utilisez le chemin absolu vers `uv` :

```json
{
  "mcpServers": {
    "insee-entreprises": {
      "command": "/home/david/.local/bin/uv",
      "args": [
        "--directory",
        "/home/david/mcp-servers/mcp-insee-entreprises",
        "run",
        "insee-entreprises"
      ]
    }
  }
}
```

> **Note** : Utilisez `which uv` pour trouver le chemin exact vers `uv` sur votre système.

> **Note** : Pour Claude Desktop, utilisez plutôt le fichier de configuration Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` sur macOS ou `%APPDATA%\Claude\claude_desktop_config.json` sur Windows).

## Configuration

### Scope d'installation

Ce serveur est installé en **scope user**, ce qui signifie qu'il est :
- Disponible pour tous vos projets Claude Code
- Stocké dans `~/.claude.json`
- Privé à votre compte utilisateur

### Gestion du serveur

```bash
# Lister tous les serveurs MCP configurés
claude mcp list

# Obtenir les détails du serveur
claude mcp get insee-entreprises

# Supprimer le serveur
claude mcp remove insee-entreprises

# Vérifier le statut (dans Claude Code)
/mcp
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

6. **Recherche par section d'activité**
   ```
   Liste les entreprises dans la section "Construction" à Marseille
   ```

   ou

   ```
   Recherche les entreprises dans le secteur de l'information et communication (section J)
   ```

## Sections d'activité NAF

Le serveur supporte la recherche par section d'activité (niveau 1 de la nomenclature NAF). Vous pouvez utiliser soit le code (lettre A-U) soit le libellé de la section.

| Code | Libellé |
|------|---------|
| A | Agriculture, sylviculture et pêche |
| B | Industries extractives |
| C | Industrie manufacturière |
| D | Production et distribution d'électricité, de gaz, de vapeur et d'air conditionné |
| E | Production et distribution d'eau ; assainissement, gestion des déchets et dépollution |
| F | Construction |
| G | Commerce ; réparation d'automobiles et de motocycles |
| H | Transports et entreposage |
| I | Hébergement et restauration |
| J | Information et communication |
| K | Activités financières et d'assurance |
| L | Activités immobilières |
| M | Activités spécialisées, scientifiques et techniques |
| N | Activités de services administratifs et de soutien |
| O | Administration publique |
| P | Enseignement |
| Q | Santé humaine et action sociale |
| R | Arts, spectacles et activités récréatives |
| S | Autres activités de services |
| T | Activités des ménages en tant qu'employeurs |
| U | Activités extra-territoriales |

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

### Documentation de l'API

- API Recherche d’Entreprises : https://www.data.gouv.fr/dataservices/api-recherche-dentreprises
- Documentation API : https://recherche-entreprises.api.gouv.fr/docs/
- OpenAPI Specification : https://recherche-entreprises.api.gouv.fr/openapi.json

### Limites

- L'API ne peut pas accéder aux :
  - Prédécesseurs/successeurs d'établissements
  - Entreprises non diffusibles
  - Rejets d'inscriptions RCS

## TODO

- Une seule fonction de recherche avec des paramètres optionnels
- Filtrage par localisation géographique (région, département)
- Support pour d'autres API INSEE (ex. API Sirene complète)

## Développeur

Serveur MCP développé par **David Scanu**
- https://github.com/DavidScanu
- https://www.linkedin.com/in/davidscanu14/