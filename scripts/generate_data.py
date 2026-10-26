import argparse, csv, os, random
from datetime import date, timedelta
from faker import Faker

REGIONS = {"Centre": ["Ouagadougou", "Kombissiri"], "Hauts-Bassins": ["Bobo-Dioulasso", "Houndé"],
           "Boucle du Mouhoun": ["Dédougou", "Tougan"], "Est": ["Fada N'Gourma", "Bogandé"],
           "Nord": ["Ouahigouya", "Yako"], "Cascades": ["Banfora", "Sindou"]}
TYPES = ["CSPS", "CMA", "CHR", "CHU", "Clinique privée"]
MOTIFS = ["Fièvre", "Toux", "Douleurs abdominales", "Suivi de grossesse", "Vaccination", "Contrôle"]
DIAG = ["Paludisme simple", "Infection respiratoire aiguë", "Diarrhée aiguë", "Hypertension artérielle",
        "Diabète", "Anémie", "Malnutrition aiguë", "Plaie et traumatisme"]
PREST = {"Consultation générale": 1000, "Analyse biologique": 3500, "Vaccination": 500,
         "Soins infirmiers": 1500, "Radiographie": 7500, "Accouchement": 10000, "Médicaments": 2500}

def ecrire(chemin, colonnes, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(colonnes)
        w.writerows(lignes)

def main():
    p = argparse.ArgumentParser(description="Génère des données sanitaires fictives")
    p.add_argument("--structures", type=int, default=20)
    p.add_argument("--consultations", type=int, default=2000)
    p.add_argument("--anomalies", type=int, default=0, help="nombre d'anomalies injectées par type")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="data")
    a = p.parse_args()
    random.seed(a.seed)
    Faker.seed(a.seed)
    fake = Faker("fr_FR")
    os.makedirs(a.out, exist_ok=True)
    today = date.today()

    struct = []
    for i in range(1, a.structures + 1):
        region = random.choice(list(REGIONS))
        ville = random.choice(REGIONS[region])
        t = random.choice(TYPES)
        struct.append([f"STR-{i:04d}", f"{t} de {ville} {i}", t, region, ville,
                       fake.date_between(start_date="-25y", end_date="-2y")])

    cons, pres, k = [], [], 0
    for i in range(1, a.consultations + 1):
        d = today - timedelta(days=random.randint(1, 365))
        cid = f"CSL-{i:06d}"
        cons.append([cid, random.choice(struct)[0], f"PAT-{random.randint(1, 5000):05d}", d,
                     random.choice(MOTIFS), random.choice(DIAG), random.randint(0, 90), random.choice(["M", "F"])])
        for _ in range(random.randint(1, 3)):
            k += 1
            t = random.choice(list(PREST))
            dp = min(d + timedelta(days=random.randint(0, 2)), today)
            pres.append([f"PRS-{k:06d}", cid, t, PREST[t] * random.choice([1, 1, 2]), dp])

    n, nc, nk = a.anomalies, len(cons), len(pres)
    for j in range(n):
        b = random.choice(cons[:nc])
        cons.append(list(b))                                                          # identifiant en double
        cons.append([f"CSL-{nc + 2*j + 1:06d}", b[1], b[2], today + timedelta(days=30), *b[4:]])  # date future
        cons.append([f"CSL-{nc + 2*j + 2:06d}", b[1], "", b[3], *b[4:]])               # id_patient vide
        cons.append([f"XX-{j:04d}", *b[1:]])                                           # identifiant invalide
        q = random.choice(pres[:nk])
        pres.append(list(q))                                                           # identifiant en double
        pres.append([f"PRS-{nk + 2*j + 1:06d}", q[1], q[2], q[3], today + timedelta(days=30)])  # date future
        pres.append([f"PRS-{nk + 2*j + 2:06d}", q[1], q[2], "", q[4]])                 # montant vide
        pres.append([f"ZZ-{j:04d}", *q[1:]])                                           # identifiant invalide

    ecrire(f"{a.out}/structures_sanitaires.csv", ["id_structure", "nom", "type_structure", "region", "district", "date_creation"], struct)
    ecrire(f"{a.out}/consultations.csv", ["id_consultation", "id_structure", "id_patient", "date_consultation", "motif", "diagnostic", "age_patient", "sexe"], cons)
    ecrire(f"{a.out}/prestations.csv", ["id_prestation", "id_consultation", "type_prestation", "montant_fcfa", "date_prestation"], pres)
    chemin_conteneur = "/" + a.out.replace("\\", "/").strip("/")
    with open(f"{a.out}/charger.sql", "w", encoding="utf-8") as f:
        f.write("TRUNCATE structures_sanitaires, consultations, prestations;\n")
        for t in ["structures_sanitaires", "consultations", "prestations"]:
            f.write(f"COPY {t} FROM '{chemin_conteneur}/{t}.csv' CSV HEADER;\n")
    print(f"structures={len(struct)} consultations={len(cons)} prestations={len(pres)} anomalies/type={n}")

if __name__ == "__main__":
    main()