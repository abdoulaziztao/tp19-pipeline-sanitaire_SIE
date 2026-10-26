TRUNCATE structures_sanitaires, consultations, prestations;
COPY structures_sanitaires FROM '/data/erreurs/structures_sanitaires.csv' CSV HEADER;
COPY consultations FROM '/data/erreurs/consultations.csv' CSV HEADER;
COPY prestations FROM '/data/erreurs/prestations.csv' CSV HEADER;
