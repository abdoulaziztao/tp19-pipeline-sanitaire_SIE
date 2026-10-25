CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS dwh;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE dwh.structures_sanitaires (
  id_structure   VARCHAR(12) PRIMARY KEY,
  nom            VARCHAR(150) NOT NULL,
  type_structure VARCHAR(50)  NOT NULL,
  region         VARCHAR(80)  NOT NULL,
  district       VARCHAR(80),
  date_creation  DATE
);
CREATE TABLE dwh.consultations (
  id_consultation   VARCHAR(14) PRIMARY KEY,
  id_structure      VARCHAR(12) NOT NULL REFERENCES dwh.structures_sanitaires (id_structure),
  id_patient        VARCHAR(14) NOT NULL,
  date_consultation DATE NOT NULL CHECK (date_consultation >= DATE '2000-01-01'),
  motif             VARCHAR(200),
  diagnostic        VARCHAR(200),
  age_patient       INT CHECK (age_patient BETWEEN 0 AND 120),
  sexe              CHAR(1) CHECK (sexe IN ('M', 'F'))
);
CREATE TABLE dwh.prestations (
  id_prestation   VARCHAR(14) PRIMARY KEY,
  id_consultation VARCHAR(14) NOT NULL REFERENCES dwh.consultations (id_consultation),
  type_prestation VARCHAR(80) NOT NULL,
  montant_fcfa    NUMERIC(12,2) NOT NULL CHECK (montant_fcfa >= 0),
  date_prestation DATE NOT NULL
);
CREATE TABLE audit.rejected_records (
  id                BIGSERIAL PRIMARY KEY,
  table_source      VARCHAR(50) NOT NULL,
  id_enregistrement VARCHAR(50),
  regle             VARCHAR(30) NOT NULL,
  motif             TEXT NOT NULL,
  valeur_brute      JSONB,
  run_id            VARCHAR(64),
  rejected_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON dwh.consultations (id_structure, date_consultation);
CREATE INDEX ON dwh.prestations (id_consultation);
CREATE INDEX ON audit.rejected_records (run_id);