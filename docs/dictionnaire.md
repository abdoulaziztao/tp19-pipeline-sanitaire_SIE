| Table | Colonne | Type | Obligatoire | Règle de validité |
|---|---|---|---|---|
| structures_sanitaires | id_structure | VARCHAR(12) | oui | format STR-0000, unique |
| structures_sanitaires | nom, type_structure, region | VARCHAR | oui | non vide |
| structures_sanitaires | date_creation | DATE | non | entre 2000-01-01 et aujourd'hui |
| consultations | id_consultation | VARCHAR(14) | oui | format CSL-000000, unique |
| consultations | id_structure | VARCHAR(12) | oui | doit exister dans structures_sanitaires |
| consultations | id_patient | VARCHAR(14) | oui | non vide (PAT-00000) |
| consultations | date_consultation | DATE | oui | entre 2000-01-01 et aujourd'hui |
| consultations | age_patient | INT | non | entre 0 et 120 |
| consultations | sexe | CHAR(1) | non | M ou F |
| prestations | id_prestation | VARCHAR(14) | oui | format PRS-000000, unique |
| prestations | id_consultation | VARCHAR(14) | oui | doit exister dans consultations |
| prestations | montant_fcfa | NUMERIC(12,2) | oui | supérieur ou égal à 0 |
| prestations | date_prestation | DATE | oui | pas avant la consultation, pas dans le futur |
| audit.rejected_records | regle | VARCHAR(30) | oui | COMPLETUDE, UNICITE, VALIDITE_ID, COHERENCE_DATES, INTEGRITE_REF, VALIDITE_VALEUR |  