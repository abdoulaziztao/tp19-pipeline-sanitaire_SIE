TRUNCATE structures_sanitaires, consultations, prestations;
COPY structures_sanitaires FROM '/data/structures_sanitaires.csv' CSV HEADER;
COPY consultations FROM '/data/consultations.csv' CSV HEADER;
COPY prestations FROM '/data/prestations.csv' CSV HEADER;
