import os
from datetime import date
from typing import Literal, Optional
from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text

engine = create_engine(os.environ.get("WAREHOUSE_URL", "postgresql+psycopg2://dwh:dwh@warehouse-db:5432/warehouse"))
app = FastAPI(title="API des indicateurs sanitaires – TP 19", version="1.0.0",
              description="Indicateurs agrégés par période et par structure, et rapport des données rejetées.")

Granularite = Literal["jour", "semaine", "mois", "annee"]
GRAN = {"jour": "day", "semaine": "week", "mois": "month", "annee": "year"}

def lire(sql, params=None):
    with engine.connect() as c:
        return [dict(r) for r in c.execute(text(sql), params or {}).mappings()]

@app.get("/health", tags=["Technique"], summary="État de l'API et de la base")
def health():
    lire("SELECT 1")
    return {"statut": "ok"}

@app.get("/structures", tags=["Référentiel"], summary="Liste des structures sanitaires validées")
def structures():
    return lire("SELECT id_structure, nom, type_structure, region, district FROM dwh.structures_sanitaires ORDER BY id_structure")

@app.get("/indicateurs/consultations", tags=["Indicateurs"], summary="Consultations par période et par structure")
def indicateurs_consultations(granularite: Granularite = "mois", id_structure: Optional[str] = None,
                              date_debut: Optional[date] = None, date_fin: Optional[date] = None):
    return lire("""
        SELECT date_trunc(:g, c.date_consultation)::date AS periode, c.id_structure, s.nom AS structure,
               COUNT(*) AS nb_consultations, COUNT(DISTINCT c.id_patient) AS nb_patients
        FROM dwh.consultations c JOIN dwh.structures_sanitaires s ON s.id_structure = c.id_structure
        WHERE (CAST(:s AS text) IS NULL OR c.id_structure = :s)
          AND (CAST(:d1 AS date) IS NULL OR c.date_consultation >= :d1)
          AND (CAST(:d2 AS date) IS NULL OR c.date_consultation <= :d2)
        GROUP BY 1, 2, 3 ORDER BY 1, 2""",
        {"g": GRAN[granularite], "s": id_structure, "d1": date_debut, "d2": date_fin})

@app.get("/indicateurs/prestations", tags=["Indicateurs"], summary="Prestations et montants par période et par structure")
def indicateurs_prestations(granularite: Granularite = "mois", id_structure: Optional[str] = None,
                            date_debut: Optional[date] = None, date_fin: Optional[date] = None):
    return lire("""
        SELECT date_trunc(:g, p.date_prestation)::date AS periode, c.id_structure, s.nom AS structure,
               COUNT(*) AS nb_prestations, SUM(p.montant_fcfa) AS montant_total_fcfa
        FROM dwh.prestations p
        JOIN dwh.consultations c ON c.id_consultation = p.id_consultation
        JOIN dwh.structures_sanitaires s ON s.id_structure = c.id_structure
        WHERE (CAST(:s AS text) IS NULL OR c.id_structure = :s)
          AND (CAST(:d1 AS date) IS NULL OR p.date_prestation >= :d1)
          AND (CAST(:d2 AS date) IS NULL OR p.date_prestation <= :d2)
        GROUP BY 1, 2, 3 ORDER BY 1, 2""",
        {"g": GRAN[granularite], "s": id_structure, "d1": date_debut, "d2": date_fin})

DERNIER = "(SELECT run_id FROM audit.rejected_records ORDER BY rejected_at DESC LIMIT 1)"

@app.get("/rejets/resume", tags=["Rejets"], summary="Nombre de rejets par table, règle et motif (dernier run par défaut)")
def rejets_resume(run_id: Optional[str] = None):
    return lire(f"""SELECT table_source, regle, motif, COUNT(*) AS nb_rejets FROM audit.rejected_records
                    WHERE run_id = COALESCE(CAST(:r AS text), {DERNIER})
                    GROUP BY 1, 2, 3 ORDER BY 1, 2""", {"r": run_id})

@app.get("/rejets", tags=["Rejets"], summary="Détail des enregistrements rejetés")
def rejets(table_source: Optional[str] = None, regle: Optional[str] = None, run_id: Optional[str] = None,
           limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return lire(f"""SELECT table_source, id_enregistrement, regle, motif, valeur_brute, run_id, rejected_at
                    FROM audit.rejected_records
                    WHERE run_id = COALESCE(CAST(:r AS text), {DERNIER})
                      AND (CAST(:t AS text) IS NULL OR table_source = :t)
                      AND (CAST(:g AS text) IS NULL OR regle = :g)
                    ORDER BY id LIMIT :lim OFFSET :off""",
                {"r": run_id, "t": table_source, "g": regle, "lim": limit, "off": offset})