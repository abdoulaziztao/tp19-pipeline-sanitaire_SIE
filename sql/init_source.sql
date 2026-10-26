CREATE TABLE structures_sanitaires (
  id_structure   VARCHAR(12),
  nom            VARCHAR(150),
  type_structure VARCHAR(50),
  region         VARCHAR(80),
  district       VARCHAR(80),
  date_creation  DATE
);
CREATE TABLE consultations (
  id_consultation   VARCHAR(14),
  id_structure      VARCHAR(12),
  id_patient        VARCHAR(14),
  date_consultation DATE,
  motif             VARCHAR(200),
  diagnostic        VARCHAR(200),
  age_patient       INT,
  sexe              CHAR(1)
);
CREATE TABLE prestations (
  id_prestation   VARCHAR(14),
  id_consultation VARCHAR(14),
  type_prestation VARCHAR(80),
  montant_fcfa    NUMERIC(12,2),
  date_prestation DATE
);