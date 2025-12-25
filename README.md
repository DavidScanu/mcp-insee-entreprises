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
   - Utilise l'API officielle INSEE Sirene
   - Retourne les informations complètes et officielles de l'unité légale
   - Données: dénomination, catégorie juridique, activité (NAF), effectifs, état administratif

2. **search_by_siret** - Recherche par numéro SIRET (14 chiffres)
   - Utilise l'API officielle INSEE Sirene
   - Retourne les informations complètes et officielles de l'établissement
   - Données: adresse complète, activité (NAF), type d'établissement (siège/secondaire), effectifs, état administratif

3. **advanced_search** - Recherche avancée avec filtres multiples
   - Nom d'entreprise, adresse, dirigeant
   - Code postal
   - Code NAF/APE
   - Section d'activité (A-U) avec conversion automatique nom → code
   - Nombre d'employés (min/max)
   - Pagination disponible

## Prérequis


- Python 3.12+
- uv (gestionnaire de paquets Python)
- Clé API INSEE (gratuite) - [Obtenir une clé](https://portail-api.insee.fr/)
- jq (pour le formatage JSON dans les scripts bash)
- yq (pour convertir le schéma OpenAPI YAML en JSON)

#### Installer jq et yq

Pour installer jq :
```bash
sudo apt-get install jq
```

Pour installer yq (version Go, recommandée) :
```bash
sudo wget -O /usr/local/bin/yq "https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64"
sudo chmod +x /usr/local/bin/yq
```
Ou via pip (version Python) :
```bash
pip install yq
```


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

3. **Configurer la clé API INSEE** :

Créez un fichier `.env` à la racine du projet:
```bash
cp .env.example .env
```

Éditez le fichier `.env` et ajoutez votre clé API INSEE:
```
INSEE_API_KEY=votre_clé_api_ici
```

> **Note** : Pour obtenir gratuitement une clé API INSEE, rendez-vous sur https://portail-api.insee.fr/

4. **Ajouter le serveur MCP à Claude Code** (scope user) :

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

5. **Vérifier l'installation** :
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

## API Utilisées

Ce serveur MCP utilise deux API complémentaires de l'INSEE:

### 1. API INSEE Sirene (Officielle)

Utilisée pour les recherches **SIREN** et **SIRET** - Données officielles et complètes:

- **Base URL**: `https://api.insee.fr/api-sirene/3.11`
- **Authentification**: Clé API requise (gratuite) - configurée via le fichier `.env`
- **Endpoints**:
  - `/siren/{siren}` - Informations sur l'unité légale
  - `/siret/{siret}` - Informations sur l'établissement
- **Limite**: 30 requêtes/minute (en environnement d'intégration)

#### Documentation
- Portail API: https://portail-api.insee.fr/ (pour obtenir une clé API)
- Documentation complète: https://portail-api.insee.fr/catalog/api/2ba0e549-5587-3ef1-9082-99cd865de66f/doc
- Spécifications OpenAPI: https://api-apimanager.insee.fr/portal/environments/DEFAULT/apis/2ba0e549-5587-3ef1-9082-99cd865de66f/pages/6548510e-c3e1-3099-be96-6edf02870699/content

#### Exemple de requête curl

Recherche par SIRET :

```bash
curl -X GET "https://api.insee.fr/api-sirene/3.11/siret/67205008502051" \
  -H "X-INSEE-Api-Key-Integration: VOTRE_CLE_API_INSEE"
```

Avec récupération automatique de la clé depuis le fichier `.env` :

```bash
source .env && curl -X GET "https://api.insee.fr/api-sirene/3.11/siret/67205008502051" \
  -H "X-INSEE-Api-Key-Integration: $INSEE_API_KEY"
```

Avec formatage JSON via `jq` :

```bash
source .env && curl -X GET "https://api.insee.fr/api-sirene/3.11/siret/67205008502051" \
  -H "X-INSEE-Api-Key-Integration: $INSEE_API_KEY" | jq '.'
```

### 2. API Recherche d'Entreprises

Utilisée pour la recherche **avancée** avec filtres multiples:

- **Base URL**: `https://recherche-entreprises.api.gouv.fr`
- **Authentification**: Aucune (accès libre)
- **Limite**: 7 requêtes par seconde
- **Disponibilité**: 100%

#### Documentation
- Documentation: https://www.data.gouv.fr/dataservices/api-recherche-dentreprises
- Swagger: https://recherche-entreprises.api.gouv.fr/docs/
- OpenAPI: https://recherche-entreprises.api.gouv.fr/openapi.json

#### Limites
- Pas d'accès aux prédécesseurs/successeurs d'établissements
- Pas d'accès aux entreprises non diffusibles
- Pas d'accès aux rejets d'inscriptions RCS

### Test des APIs

Un script bash `scripts/insee_api.sh` est inclus pour tester les appels aux deux APIs. Assurez-vous d'avoir `jq` et  `yq` installés pour le formatage JSON et la conversion du YAML vers JSON.

```bash
chmod +x scripts/insee_api.sh
./scripts/insee_api.sh
```

**Dépannage** :

- **Clé API INSEE invalide ou absente** : vérifiez le contenu du fichier `.env` et la variable `INSEE_API_KEY`.
- **Caractères spéciaux mal affichés (Ã©, Ã , etc.)** : assurez-vous que votre terminal et vos fichiers sont en UTF-8.
- **Erreur : yq n'est pas installé** : installez `yq`.
- **Erreur : jq n'est pas installé** : installez `jq`.

---

## TODO

- Tester le serveur MCP la recherche par SIREN et SIRET (API officielle INSEE Sirene 3.11)
- Tester le serveur MCP avec la nouvelle version de l'API INSEE Sirene (v4.0)
- Ajouter des exemples d'utilisation avancée dans la documentation
- Ajouter la recherche par critères géographiques (région, département)

---

## Développeur

Serveur MCP développé par **David Scanu**
- https://github.com/DavidScanu
- https://www.linkedin.com/in/davidscanu14/