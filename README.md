# Pipeline de données sanitaires fictives (TP 19, SIE Groupe 7)

Chaîne ELT : PostgreSQL source, Airbyte, PostgreSQL entrepôt, Dagster (contrôles qualité), FastAPI.

## Architecture

    PostgreSQL source (5433) --Airbyte--> PostgreSQL entrepôt, schéma raw (5434)
    raw --Dagster--> dwh (données valides) et audit.rejected_records (rejets)
    dwh et audit --FastAPI (8001, Swagger sur /docs)--> indicateurs et rapport des rejets

## Prérequis

- Git, Python 3.10 ou plus récent, Docker Desktop (Docker Compose v2)
- Environ 4 processeurs et 8 Go de mémoire pour Airbyte

## Installation

1. Cloner le dépôt : git clone URL_DU_DEPOT puis entrer dans le dossier.
2. Démarrer les services : docker compose up -d --build
3. Charger la base source avec les données fournies : docker compose exec source-db psql -U source -d sourcedb -f /data/charger.sql
   (pour régénérer les données : python -m pip install -r scripts/requirements.txt puis python scripts/generate_data.py)
4. Installer Airbyte (procédure distincte) : curl -LsfS https://get.airbyte.com | bash - puis abctl local install --low-resource-mode. Configurer source, destination et connexion comme décrit dans docs/airbyte.md, puis lancer la synchronisation.
5. Ouvrir Dagster sur http://localhost:3000 et cliquer sur Materialize all.
6. Ouvrir l'API sur http://localhost:8001/docs.

## Tests et résultats attendus

Voir tests/RESULTATS_ATTENDUS.md. Vérification : docker compose exec warehouse-db psql -U dwh -d warehouse -f /tests/verification.sql

## Contenu du dépôt

- docker-compose.yml : bases PostgreSQL, Dagster, FastAPI
- scripts/ : générateur de données ; sql/ : scripts d'initialisation
- data/ : jeux de données (normal et avec erreurs) ; dagster/ : assets de qualité ; api/ : API FastAPI
- tests/ : requête de vérification et résultats attendus
- docs/ : dictionnaire de données, configuration Airbyte, contrat OpenAPI, captures, rapport, présentation

## Équipe (Groupe 7, SIE)

SAVADOGO ADJARATOU (données), 
TAO Aziz (Airbyte), 
OUEDRAOGO Adama (Dagster), 
SIMPORE Carine (FastAPI), 
SOUARA Audrey (DevOps et qualité). 