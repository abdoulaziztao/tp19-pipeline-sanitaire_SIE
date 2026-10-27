# Résultats attendus

## Scénario nominal (data/charger.sql)
- structures chargées : 20
- consultations chargées : 2000
- prestations chargées : égal au nombre de prestations de la base source
- rejets du dernier run : 0

## Scénario d'erreurs (data/erreurs/charger.sql)
Données avec 5 anomalies de chaque type par table.
- consultations chargées : 2000 (aucune ligne erronée n'entre dans dwh)
- prestations chargées : même nombre que dans le scénario nominal
- rejets du dernier run : 40
- 5 rejets pour chacune des 8 combinaisons : consultations et prestations avec UNICITE, COHERENCE_DATES, COMPLETUDE, VALIDITE_ID