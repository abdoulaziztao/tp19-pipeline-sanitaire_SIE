# Pipeline de données sanitaires fictives (TP 19, SIE Groupe 7)

Chaîne ELT : PostgreSQL source, Airbyte, PostgreSQL entrepôt, Dagster (contrôles qualité), FastAPI.

Toutes les données sont **fictives** (générées par script). Aucune donnée de patient réel.

## Architecture

```text
PostgreSQL source (5433) --Airbyte--> PostgreSQL entrepôt, schéma raw (5434)
raw --Dagster--> dwh (données valides) et audit.rejected_records (rejets)
dwh et audit --FastAPI (8001, Swagger sur /docs)--> indicateurs et rapport des rejets
```

| Service | Rôle | Adresse |
|---|---|---|
| source-db | PostgreSQL source (données fictives) | localhost:5433 |
| warehouse-db | PostgreSQL entrepôt (raw, dwh, audit) | localhost:5434 |
| Airbyte (abctl) | Ingestion source vers raw | http://localhost:8000 |
| Dagster | Orchestration et contrôles qualité | http://localhost:3000 |
| FastAPI | API REST (Swagger sur /docs) | http://localhost:8001/docs |

## Prérequis

- Git, Python 3.10 ou plus récent, Docker Desktop (Docker Compose v2)
- Environ 4 processeurs et 8 Go de mémoire pour Airbyte
- Ports libres : 3000, 5433, 5434, 8000, 8001

Vérifier les versions installées :

```bash
git --version
python --version        # ou python3 --version sous Linux / macOS
docker --version
docker compose version
```

## Installation (machine neuve)

### 1. Cloner le dépôt

```bash
git clone https://github.com/abdoulaziztao/tp19-pipeline-sanitaire_SIE
cd NOM_DU_DOSSIER
```

### 2. Démarrer les services

```bash
docker compose up -d --build
docker compose ps
```

Résultat attendu : les conteneurs `source-db`, `warehouse-db`, Dagster et FastAPI sont à l'état `running` (les bases en `healthy` si un healthcheck est défini).

### 3. Charger la base source

Avec les données fournies dans le dépôt :

```bash
docker compose exec source-db psql -U source -d sourcedb -f /data/charger.sql
```

Vérifier que les données sont chargées :

```bash
docker compose exec source-db psql -U source -d sourcedb -c "\dt"
```

Pour régénérer les données (facultatif) :

```bash
python -m pip install -r scripts/requirements.txt
python scripts/generate_data.py
```

### 4. Installer Airbyte (procédure distincte)

Airbyte n'est pas dans le `docker-compose.yml` : il s'installe avec `abctl`.

```bash
curl -LsfS https://get.airbyte.com | bash -
abctl local install --low-resource-mode
abctl local credentials
```

Sous Windows, utiliser WSL2 ou suivre la documentation officielle d'`abctl`. Docker Desktop doit être démarré.

Ouvrir ensuite http://localhost:8000 et se connecter avec les identifiants affichés par `abctl local credentials`.

Configurer dans Airbyte, comme décrit dans `docs/airbyte.md` :

1. **Source** : PostgreSQL, hôte `host.docker.internal`, port `5433`, base `sourcedb`, utilisateur `source`.
2. **Destination** : PostgreSQL, hôte `host.docker.internal`, port `5434`, base `warehouse`, utilisateur `dwh`, schéma `raw`.
3. **Connexion** : sélectionner les 3 flux (structures, consultations, prestations), puis lancer **Sync now**.

Les mots de passe sont ceux définis dans `docker-compose.yml` (ou le fichier `.env`).

Vérifier que la synchronisation a rempli le schéma `raw` :

```bash
docker compose exec warehouse-db psql -U dwh -d warehouse -c "\dt raw.*"
```

### 5. Lancer les contrôles qualité avec Dagster

1. Ouvrir http://localhost:3000
2. Aller dans **Assets**, puis cliquer sur **Materialize all**
3. Attendre que toutes les étapes soient en vert

Vérifier les résultats :

```bash
docker compose exec warehouse-db psql -U dwh -d warehouse -c "SELECT COUNT(*) FROM audit.rejected_records;"
```

### 6. Utiliser l'API

Ouvrir http://localhost:8001/docs, ou tester en ligne de commande :

```bash
curl http://localhost:8001/docs
```

Les routes d'indicateurs (par période et par structure) et du rapport des rejets sont listées dans Swagger et décrites dans le contrat OpenAPI de `docs/`.

## Tests et résultats attendus

Les résultats attendus sont dans `tests/RESULTATS_ATTENDUS.md`.

**Test de bout en bout (cas nominal)** : suivre les étapes 2 à 6 avec le jeu de données normal. Puis lancer la vérification :

```bash
docker compose exec warehouse-db psql -U dwh -d warehouse -f /tests/verification.sql
```

Comparer la sortie avec `tests/RESULTATS_ATTENDUS.md`.

**Scénario d'erreurs** : charger le jeu de données avec erreurs (dossier `data/`), relancer la synchronisation Airbyte, puis **Materialize all** dans Dagster. Les lignes invalides doivent apparaître dans `audit.rejected_records` avec leur motif :

```bash
docker compose exec warehouse-db psql -U dwh -d warehouse -c "SELECT * FROM audit.rejected_records LIMIT 20;"
```

## Arrêter et réinitialiser

```bash
# Arrêter les services (données conservées)
docker compose down

# Tout supprimer, y compris les volumes (retour à zéro)
docker compose down -v

# Désinstaller Airbyte
abctl local uninstall
```

## Problèmes fréquents

| Problème | Solution |
|---|---|
| Port déjà utilisé | Arrêter le programme qui occupe le port, ou changer le port dans `docker-compose.yml` |
| Airbyte ne se connecte pas aux bases | Vérifier que Docker Desktop est démarré et utiliser `host.docker.internal` comme hôte |
| Airbyte très lent | Fermer les autres applications, vérifier 4 processeurs et 8 Go alloués à Docker Desktop |
| Un conteneur redémarre en boucle | `docker compose logs NOM_DU_SERVICE` pour lire l'erreur |
| Dagster ne voit pas les tables `raw` | La synchronisation Airbyte n'a pas été lancée ou a échoué (étape 4) |

## Contenu du dépôt

- `docker-compose.yml` : bases PostgreSQL, Dagster, FastAPI
- `scripts/` : générateur de données ; `sql/` : scripts d'initialisation
- `data/` : jeux de données (normal et avec erreurs) ; `dagster/` : assets de qualité ; `api/` : API FastAPI
- `tests/` : requête de vérification et résultats attendus
- `docs/` : dictionnaire de données, configuration Airbyte, contrat OpenAPI, captures, rapport, présentation

## Équipe (Groupe 7, SIE)

- SAVADOGO Adjaratou : données
- TAO Abdoul Aziz : Airbyte
- OUEDRAOGO Adama : Dagster
- SIMPORE Carine : FastAPI
- SAOURA Audrey : DevOps et qualité