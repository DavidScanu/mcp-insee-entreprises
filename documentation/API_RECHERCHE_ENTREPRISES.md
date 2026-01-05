# API Recherche d'Entreprises - Documentation Complète

## Informations Générales

- **URL de base** : `https://recherche-entreprises.api.gouv.fr`
- **Version** : 1.0.0
- **Licence** : MIT License
- **Limite de requêtes** : 7 requêtes/seconde (code 429 si dépassement)
- **Documentation interactive** : https://recherche-entreprises.api.gouv.fr/docs/
- **Spécification OpenAPI** : https://recherche-entreprises.api.gouv.fr/openapi.json

## Endpoints Disponibles

### 1. GET `/search` - Recherche Textuelle

Récupère les unités légales et établissements correspondant à une recherche textuelle sur dénomination, adresse, dirigeants et élus.

#### Paramètres de Recherche Primaires

| Paramètre | Type | Requis | Description | Exemple |
|-----------|------|--------|-------------|---------|
| `q` | string | Oui | Termes de recherche (dénomination, adresse, dirigeants, élus) | `"la poste"` |
| `page` | integer | Non | Numéro de page (défaut: 1) | `1` |
| `per_page` | integer | Non | Résultats par page, max 25 (défaut: 10) | `10` |

#### Paramètres de Filtrage - Activité

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `activite_principale` | string | Code(s) NAF/APE (séparés par virgule) | `"01.12Z,28.15Z"` |
| `section_activite_principale` | string | Section(s) d'activité A-U (séparées par virgule) | `"A,B,C"` |
| `categorie_entreprise` | enum | Catégorie : PME, ETI, GE | `"PME"` |

#### Paramètres de Filtrage - Localisation

| Paramètre | Type | Format | Exemple |
|-----------|------|--------|---------|
| `code_postal` | string | 5 chiffres (séparés par virgule) | `"38540,38189"` |
| `code_commune` | string | Code INSEE 5 caractères | `"01247,01111"` |
| `departement` | string | 2-3 chiffres | `"02,89"` |
| `region` | string | 2 chiffres | `"11,76"` |
| `epci` | string | SIREN de l'EPCI | `"200058519,248100737"` |
| `code_collectivite_territoriale` | string | Code INSEE ou variante | - |

#### Paramètres de Filtrage - Identifiants Spécialisés

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `id_convention_collective` | string | IDCC | `"1090"` |
| `id_finess` | string | Identifiant FINESS (9 chiffres) | `"010003853"` |
| `id_rge` | string | Identifiant RGE | `"8611M10D109"` |
| `id_uai` | string | Identifiant UAI | `"0022004T"` |

#### Paramètres de Filtrage - Données Financières

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `ca_min` | integer | Chiffre d'affaires minimum | `100000` |
| `ca_max` | integer | Chiffre d'affaires maximum | `1000000` |
| `resultat_net_min` | integer | Résultat net minimum | `100000` |
| `resultat_net_max` | integer | Résultat net maximum | `1000000` |

#### Paramètres de Filtrage - Informations sur les Personnes

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `nom_personne` | string | Nom du dirigeant ou élu | `"Dupont"` |
| `prenoms_personne` | string | Prénoms | `"Jean"` |
| `date_naissance_personne_min` | date | Date minimum (YYYY-MM-DD) | `"1960-01-01"` |
| `date_naissance_personne_max` | date | Date maximum (YYYY-MM-DD) | `"1990-01-01"` |
| `type_personne` | enum | Type : `dirigeant`, `elu` | `"dirigeant"` |

#### Paramètres Booléens - Labels et Certifications

| Paramètre | Description |
|-----------|-------------|
| `convention_collective_renseignee` | Au moins un établissement avec convention collective |
| `egapro_renseignee` | Index égalité professionnelle H/F renseigné |
| `est_achats_responsables` | Label Relations Fournisseurs et Achats Responsables (RFAR) |
| `est_alim_confiance` | Résultat contrôle sanitaire Alim'Confiance disponible |
| `est_association` | Identifiant association ou nature juridique spécifique |
| `est_bio` | Certification agriculture biologique (Agence Bio) |
| `est_collectivite_territoriale` | Est une collectivité territoriale |
| `est_entrepreneur_individuel` | Est une entreprise individuelle |
| `est_entrepreneur_spectacle` | Détient une licence entrepreneur du spectacle |
| `est_ess` | Appartient à l'Économie Sociale et Solidaire |
| `est_finess` | Établissement du domaine sanitaire et social (FINESS) |
| `est_organisme_formation` | Est un organisme de formation |
| `est_patrimoine_vivant` | Détient le label Entreprise du Patrimoine Vivant (EPV) |
| `est_qualiopi` | Détient la certification Qualiopi |
| `est_rge` | Reconnu Garant de l'Environnement |
| `est_siae` | Structure d'insertion par l'activité économique |
| `est_service_public` | Administration reconnue service public |
| `est_l100_3` | Administration au sens de l'article L.100-3 |
| `est_societe_mission` | Est une société à mission |
| `est_uai` | Possède un établissement avec identifiant UAI |

#### Paramètres Additionnels

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `nature_juridique` | string | Catégorie juridique INSEE (séparées par virgule) | `"7344,6544"` |
| `tranche_effectif_salarie` | string | Tranche d'effectif salarié (séparées par virgule) | `"NN,00,01"` |
| `etat_administratif` | enum | État : `A` (Actif), `C` (Cessée) | `"A"` |
| `limite_matching_etablissements` | integer | Nombre max d'établissements retournés (1-100, défaut: 10) | `10` |
| `minimal` | boolean | Réponse minimaliste excluant champs secondaires | `false` |
| `include` | string | Avec `minimal=true` : champs à inclure (séparés par virgule) | `"dirigeants,finances"` |

**Valeurs possibles pour `include`** : `complements`, `dirigeants`, `finances`, `matching_etablissements`, `siege`, `score`

---

### 2. GET `/near_point` - Recherche Géographique

Retourne les unités légales et établissements autour de coordonnées géographiques.

#### Paramètres Obligatoires

| Paramètre | Type | Description |
|-----------|------|-------------|
| `lat` | float | Latitude (géocodage SIRENE data.gouv.fr) |
| `long` | float | Longitude (géocodage SIRENE data.gouv.fr) |

#### Paramètres Optionnels

| Paramètre | Type | Défaut | Contrainte | Description |
|-----------|------|--------|-----------|-------------|
| `radius` | float | 5 km | ≤ 50 km | Rayon de recherche en kilomètres |
| `activite_principale` | string | - | - | Code(s) NAF (séparés par virgule) |
| `section_activite_principale` | string | - | A-U | Section(s) d'activité (séparées par virgule) |
| `limite_matching_etablissements` | integer | 10 | 1-100 | Nombre max d'établissements |
| `minimal` | boolean | false | - | Réponse minimaliste |
| `include` | string | - | - | Champs additionnels avec `minimal=true` |
| `page` | integer | 1 | - | Numéro de page |
| `per_page` | integer | 10 | Max 25 | Résultats par page |

---

## Schémas de Réponse

### Structure Principale (200 OK)

```json
{
  "results": [
    // Array d'unités légales
  ],
  "total_results": 12345,
  "page": 1,
  "per_page": 10,
  "total_pages": 1235
}
```

### Note importante sur le filtrage géographique

Lorsque vous utilisez des filtres géographiques (département, région, code postal, commune), l'API recherche les **établissements** correspondants, mais retourne les **unités légales** (entreprises).

**Comportement clé :**
- Le filtre `departement=14` trouve toutes les entreprises ayant au moins un établissement dans le Calvados (14)
- Le champ `siege` contient toujours l'adresse du siège social (qui peut être dans un autre département)
- Le champ `matching_etablissements` contient la liste des établissements correspondant aux critères de recherche

**Exemple :** Une recherche `departement=14` peut retourner :
- Une entreprise avec siège à Paris (75)
- Mais ayant plusieurs établissements dans le Calvados (14)
- Les établissements du Calvados seront listés dans `matching_etablissements`

### Unité Légale

| Propriété | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `siren` | string | Identifiant SIREN (9 chiffres) | `"356000000"` |
| `nom_complet` | string | Nom complet de l'entreprise | `"la poste"` |
| `nom_raison_sociale` | string | Raison sociale | `"LA POSTE"` |
| `sigle` | string | Sigle | `null` |
| `nombre_etablissements` | integer | Nombre total d'établissements | `12734` |
| `nombre_etablissements_ouverts` | integer | Nombre d'établissements actifs | `9524` |
| `date_creation` | date | Date de création (YYYY-MM-DD) | `"1991-01-01"` |
| `date_fermeture` | date | Date de fermeture | `null` |
| `date_mise_a_jour` | date | Date de dernière mise à jour | `"2022-05-31"` |
| `etat_administratif` | string | État : `A` (Actif) ou `C` (Cessé) | `"A"` |
| `nature_juridique` | string | Code catégorie juridique INSEE | `"5510"` |
| `activite_principale` | string | Code NAF/APE | `"53.10Z"` |
| `section_activite_principale` | string | Section d'activité (A-U) | `"H"` |
| `categorie_entreprise` | string | PME, ETI ou GE | `"GE"` |
| `annee_categorie_entreprise` | string | Année de référence | `"2020"` |
| `caractere_employeur` | string | `O` (Oui) ou `N` (Non) | `"O"` |
| `tranche_effectif_salarie` | string | Code tranche d'effectif | `"53"` |
| `annee_tranche_effectif_salarie` | string | Année de référence | `"2020"` |
| `statut_diffusion` | string | `O` (Diffusible) ou `P` (Partiel) | `"O"` |

### Établissement (Siège et Matching)

| Propriété | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `siret` | string | Identifiant SIRET (14 chiffres) | `"35600000000048"` |
| `est_siege` | boolean | Est le siège social | `true` |
| `ancien_siege` | boolean | Était un ancien siège | `false` |
| `activite_principale` | string | Code NAF/APE | `"53.10Z"` |
| `activite_principale_registre_metier` | string | Activité au registre des métiers | `null` |
| `adresse` | string | Adresse complète | `"9 RUE DU COLONEL PIERRE AVIA 75015 PARIS 15"` |
| `numero_voie` | string | Numéro de voie | `"9"` |
| `indice_repetition` | string | Indice de répétition (bis, ter...) | `null` |
| `type_voie` | string | Type de voie (RUE, AVE...) | `"RUE"` |
| `libelle_voie` | string | Nom de la voie | `"DU COLONEL PIERRE AVIA"` |
| `code_postal` | string | Code postal | `"75015"` |
| `commune` | string | Code INSEE commune | `"75115"` |
| `libelle_commune` | string | Nom de la commune | `"PARIS 15"` |
| `departement` | string | Code département | `"75"` |
| `region` | string | Code région | `"11"` |
| `epci` | string | Code EPCI | `"200058519"` |
| `latitude` | string | Latitude | `"48.83002"` |
| `longitude` | string | Longitude | `"2.275688"` |
| `geo_id` | string | Identifiant géographique | `"75115_2214"` |
| `etat_administratif` | string | État : `A` (Actif) ou `F` (Fermé) | `"A"` |
| `date_creation` | date | Date de création | `"2003-01-01"` |
| `date_debut_activite` | date | Date de début d'activité | `"2014-04-29"` |
| `date_fermeture` | date | Date de fermeture | `null` |
| `date_mise_a_jour` | datetime | Date de mise à jour | `"2023-09-21T03:34:50"` |
| `caractere_employeur` | string | `O` (Oui) ou `N` (Non) | `"O"` |
| `tranche_effectif_salarie` | string | Code tranche d'effectif | `"41"` |
| `annee_tranche_effectif_salarie` | string | Année de référence | `"2020"` |
| `statut_diffusion_etablissement` | string | `O` (Diffusible) ou `P` (Partiel) | `"O"` |
| `liste_enseignes` | array | Liste des enseignes | `["LA POSTE"]` |
| `nom_commercial` | string | Nom commercial | `null` |
| `complement_adresse` | string | Complément d'adresse | `"DIRECTION GENERALE DE LA POSTE"` |
| `cedex` | string | Code CEDEX | `null` |
| `distribution_speciale` | string | Distribution spéciale | `null` |

### Listes Spécialisées (par Établissement)

| Propriété | Type | Description |
|-----------|------|-------------|
| `liste_finess` | array[string] | Identifiants FINESS Géographiques |
| `liste_finess_juridique` | array[string] | Identifiants FINESS Juridiques |
| `liste_idcc` | array[string] | Identifiants conventions collectives (ex: `["0923"]`) |
| `liste_id_bio` | array[string] | Identifiants Agence Bio |
| `liste_rge` | array[string] | Identifiants RGE/ADEME |
| `liste_uai` | array[string] | Identifiants UAI (éducation) |
| `liste_id_organisme_formation` | array[string] | Numéros de déclaration d'activité formation |

### Objet Dirigeants (Tableau Optionnel)

#### Personne Physique

```json
{
  "type_dirigeant": "personne physique",
  "nom": "Dupont",
  "prenoms": "Jean",
  "annee_de_naissance": "1964",
  "date_de_naissance": "1964-09",
  "qualite": "Directeur général",
  "nationalite": "Française"
}
```

#### Personne Morale

```json
{
  "type_dirigeant": "personne morale",
  "siren": "784824153",
  "denomination": "EXEMPLE SAS",
  "qualite": "Commissaire aux comptes titulaire"
}
```

### Objet Finances (Optionnel)

```json
{
  "2021": {
    "ca": 26617000000,
    "resultat_net": 2597000000
  },
  "2020": {
    "ca": 25000000000,
    "resultat_net": 2000000000
  }
}
```

### Objet Compléments (Optionnel)

Contient des informations additionnelles sur les labels, certifications et caractéristiques spécifiques :

- `collectivite_territoriale` : Objet avec code INSEE, niveau, élus
- `convention_collective_renseignee` : Boolean
- `liste_idcc` : Array des conventions collectives de l'UL
- `liste_finess_juridique` : Array FINESS juridiques de l'UL
- `egapro_renseignee` : Boolean
- `est_achats_responsables` : Boolean
- `est_alim_confiance` : Boolean
- `est_association` : Boolean
- `est_bio` : Boolean
- `est_entrepreneur_individuel` : Boolean
- `est_entrepreneur_spectacle` : Boolean
- `est_ess` : Boolean
- `est_finess` : Boolean
- `est_organisme_formation` : Boolean
- `est_patrimoine_vivant` : Boolean
- `est_qualiopi` : Boolean
- `est_rge` : Boolean
- `est_siae` : Boolean
- `est_service_public` : Boolean
- `est_l100_3` : Boolean
- `est_societe_mission` : Boolean
- `est_uai` : Boolean
- `bilan_ges_renseigne` : Boolean (bilan GES publié - ADEME)
- `identifiant_association` : String (numéro RNA)
- `statut_bio` : Boolean (demande de certification bio en cours)
- `statut_entrepreneur_spectacle` : String
- `type_siae` : String (type de structure d'insertion)
- `liste_id_organisme_formation` : Array

### Objet Collectivité Territoriale

```json
{
  "code_insee": "01",
  "code": "01",
  "niveau": "département",
  "elus": [
    {
      "nom": "Dupont",
      "prenoms": "Marie",
      "annee_de_naissance": "1964",
      "fonction": "Maire",
      "sexe": "F"
    }
  ]
}
```

---

## Codes de Réponse HTTP

| Code | Description |
|------|-------------|
| 200 | Succès - Liste des unités légales et établissements |
| 400 | Requête incorrecte (ex: "Veuillez indiquer au moins un paramètre de recherche.") |
| 429 | Dépassement de la limite de volumétrie (>7 requêtes/seconde) |

---

## Sections d'Activité NAF (A-U)

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

---

## Exemples d'Utilisation

### Recherche simple par nom

```bash
curl -X GET "https://recherche-entreprises.api.gouv.fr/search?q=la%20poste&page=1&per_page=10" \
  -H "accept: application/json"
```

### Recherche par SIREN

```bash
curl -X GET "https://recherche-entreprises.api.gouv.fr/search?q=356000000" \
  -H "accept: application/json"
```

### Recherche par code postal et activité

```bash
curl -X GET "https://recherche-entreprises.api.gouv.fr/search?q=boulangerie&code_postal=75015&activite_principale=10.71C" \
  -H "accept: application/json"
```

### Recherche par section d'activité

```bash
curl -X GET "https://recherche-entreprises.api.gouv.fr/search?q=&section_activite_principale=L&code_postal=14000" \
  -H "accept: application/json"
```

### Recherche géographique

```bash
curl -X GET "https://recherche-entreprises.api.gouv.fr/near_point?lat=48.8566&long=2.3522&radius=5" \
  -H "accept: application/json"
```

### Recherche avancée avec filtres multiples

```bash
curl -X GET "https://recherche-entreprises.api.gouv.fr/search?q=&section_activite_principale=J&departement=75&tranche_effectif_salarie=12,21&est_ess=true" \
  -H "accept: application/json"
```

---

## Limitations et Règles

### Contraintes

- **Limite de requêtes** : 7 requêtes/seconde maximum
- **Pagination** : Maximum 25 résultats par page
- **Rayon de recherche géographique** : Maximum 50 km

### Limitations Fonctionnelles

- Pas d'accès aux prédécesseurs/successeurs d'établissements
- Pas d'accès aux entreprises non-diffusibles (statut de diffusion partiel)
- Pas d'accès aux rejets d'immatriculation RCS
- Recherche textuelle limitée à : dénomination, adresse, dirigeants et élus

### Patterns de Validation

**Code postal** : `^((0[1-9])|([1-8][0-9])|(9[0-8])|(2A)|(2B))[0-9]{3}$`

**Département** : `\b([013-8]\d?|2[aAbB1-9]?|9[0-59]?|97[12346])\b`

---

## Ressources Externes

- [Documentation SIRENE INSEE](https://www.sirene.fr)
- [Nomenclature NAF/APE](https://www.sirene.fr/static-resources/documentation/v_sommaire_311.htm)
- [Codes géographiques INSEE](https://www.insee.fr)
- [Liste des administrations françaises](https://www.data.gouv.fr/fr/datasets/liste-des-administrations-francaises/)
- [Données publiques Data.gouv.fr](https://www.data.gouv.fr)
- [API Recherche d'Entreprises sur API.gouv.fr](https://api.gouv.fr/les-api/api-recherche-entreprises)
- [Page Data.gouv.fr de l'API](https://www.data.gouv.fr/dataservices/api-recherche-dentreprises)

---

## Notes Techniques

### Architecture de l'API

L'API Recherche d'Entreprises interroge la base SIRENE de l'INSEE et agrège plusieurs sources de données publiques :

- Base SIRENE (entreprises et établissements)
- Registre National des Associations (RNA)
- Données financières
- Certifications et labels (RGE, Qualiopi, Bio, ESS, etc.)
- Identifiants sectoriels (FINESS, UAI, etc.)
- Données géographiques (géocodage)

### Mise à Jour des Données

Les données sont mises à jour quotidiennement à partir des sources officielles. Le champ `date_mise_a_jour` indique la dernière actualisation pour chaque entité.

### Statut de Diffusion

Certaines entreprises ont un statut de diffusion partiel (`statut_diffusion: "P"`), ce qui limite les informations accessibles publiquement conformément à la réglementation sur la protection des données.