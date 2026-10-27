import os
import pandas as pd
from datetime import date
from dagster import (asset, AssetExecutionContext, AssetSelection, Definitions,
                     ScheduleDefinition, define_asset_job)
from sqlalchemy import create_engine, text

URL = os.environ.get("WAREHOUSE_URL", "postgresql+psycopg2://dwh:dwh@warehouse-db:5432/warehouse")
engine = create_engine(URL)

def lire(table, colonnes, dates):
    df = pd.read_sql(f"SELECT {', '.join(colonnes)} FROM raw.{table}", engine)
    for c in dates:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

def ecrire_rejets(df, table, cle, rejets, run_id):
    if not rejets:
        return
    lignes = [{"t": table, "k": None if pd.isna(df.at[r["i"], cle]) else str(df.at[r["i"], cle]),
               "r": r["regle"], "m": r["motif"], "b": df.loc[r["i"]].to_json(date_format="iso"),
               "run": run_id} for r in rejets]
    with engine.begin() as c:
        c.execute(text("INSERT INTO audit.rejected_records (table_source, id_enregistrement, regle, motif, "
                       "valeur_brute, run_id) VALUES (:t, :k, :r, :m, CAST(:b AS jsonb), :run)"), lignes)

def controler(df, table, cle, motif_id, obligatoires, dates, ctx, extras=()):
    rejets = []
    def rejeter(masque, regle, motif):
        for i in df.index[masque]:
            rejets.append({"i": i, "regle": regle, "motif": motif})
    for col in obligatoires:                                                    # 1. complétude
        rejeter(df[col].isna() | df[col].astype(str).str.strip().eq(""), "COMPLETUDE", f"Champ obligatoire vide : {col}")
    rejeter(~df[cle].astype(str).str.match(motif_id), "VALIDITE_ID", f"Identifiant {cle} au format invalide")  # 2. identifiants
    rejeter(df.duplicated(cle, keep="first"), "UNICITE", f"Identifiant {cle} en double")                      # 3. unicité
    for col in dates:                                                           # 4. cohérence des dates
        d = df[col]
        rejeter((d > pd.Timestamp(date.today())) | (d < pd.Timestamp("2000-01-01")), "COHERENCE_DATES",
                f"Date {col} dans le futur ou avant 2000")
    for masque, regle, motif in extras:
        rejeter(masque, regle, motif)
    exclus = {r["i"] for r in rejets}
    propres = df.drop(index=list(exclus)).copy()
    ecrire_rejets(df, table, cle, rejets, ctx.run_id)
    ctx.add_output_metadata({"lignes_lues": len(df), "lignes_valides": len(propres), "lignes_rejetees": len(exclus)})
    return propres

@asset(group_name="brut")
def raw_structures():
    return lire("structures_sanitaires", ["id_structure", "nom", "type_structure", "region", "district", "date_creation"], ["date_creation"])

@asset(group_name="brut")
def raw_consultations():
    return lire("consultations", ["id_consultation", "id_structure", "id_patient", "date_consultation", "motif",
                                  "diagnostic", "age_patient", "sexe"], ["date_consultation"])

@asset(group_name="brut")
def raw_prestations():
    return lire("prestations", ["id_prestation", "id_consultation", "type_prestation", "montant_fcfa", "date_prestation"], ["date_prestation"])

@asset(group_name="qualite")
def structures_valides(context: AssetExecutionContext, raw_structures):
    return controler(raw_structures, "structures_sanitaires", "id_structure", r"^STR-\d{4}$",
                     ["id_structure", "nom", "type_structure", "region"], ["date_creation"], context)

@asset(group_name="qualite")
def consultations_valides(context: AssetExecutionContext, raw_consultations, structures_valides):
    extras = [(~raw_consultations["id_structure"].isin(structures_valides["id_structure"]),
               "INTEGRITE_REF", "Structure inconnue ou rejetée")]
    return controler(raw_consultations, "consultations", "id_consultation", r"^CSL-\d{6}$",
                     ["id_consultation", "id_structure", "id_patient", "date_consultation"], ["date_consultation"], context, extras)

@asset(group_name="qualite")
def prestations_valides(context: AssetExecutionContext, raw_prestations, consultations_valides):
    dates = consultations_valides.set_index("id_consultation")["date_consultation"]
    extras = [(~raw_prestations["id_consultation"].isin(dates.index), "INTEGRITE_REF", "Consultation inconnue ou rejetée"),
              (raw_prestations["date_prestation"] < raw_prestations["id_consultation"].map(dates), "COHERENCE_DATES",
               "Prestation antérieure à la consultation"),
              (raw_prestations["montant_fcfa"] < 0, "VALIDITE_VALEUR", "Montant négatif")]
    return controler(raw_prestations, "prestations", "id_prestation", r"^PRS-\d{6}$",
                     ["id_prestation", "id_consultation", "type_prestation", "montant_fcfa", "date_prestation"],
                     ["date_prestation"], context, extras)

@asset(group_name="entrepot")
def entrepot_charge(context: AssetExecutionContext, structures_valides, consultations_valides, prestations_valides):
    with engine.begin() as c:
        c.execute(text("TRUNCATE dwh.prestations, dwh.consultations, dwh.structures_sanitaires"))
        for nom, df in [("structures_sanitaires", structures_valides), ("consultations", consultations_valides),
                        ("prestations", prestations_valides)]:
            df.to_sql(nom, c, schema="dwh", if_exists="append", index=False, method="multi", chunksize=1000)
    context.add_output_metadata({"structures": len(structures_valides), "consultations": len(consultations_valides),
                                 "prestations": len(prestations_valides)})

pipeline = define_asset_job("pipeline_sanitaire", selection=AssetSelection.all())
defs = Definitions(
    assets=[raw_structures, raw_consultations, raw_prestations, structures_valides, consultations_valides,
            prestations_valides, entrepot_charge],
    jobs=[pipeline],
    schedules=[ScheduleDefinition(job=pipeline, cron_schedule="0 2 * * *")],
)