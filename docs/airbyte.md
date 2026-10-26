# Configuration Airbyte

Installation : abctl local install --low-resource-mode (interface sur http://localhost:8000).

| Élément | Paramètres |
|---|---|
| Source Postgres | host.docker.internal, port 5433, base sourcedb, schéma public, utilisateur source |
| Destination Postgres | host.docker.internal, port 5434, base warehouse, schéma raw, utilisateur dwh |
| Connexion | 3 flux (structures_sanitaires, consultations, prestations), mode Full refresh avec Overwrite, fréquence manuelle |