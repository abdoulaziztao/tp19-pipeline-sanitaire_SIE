SELECT 'structures chargées' AS indicateur, COUNT(*) AS valeur FROM dwh.structures_sanitaires
UNION ALL SELECT 'consultations chargées', COUNT(*) FROM dwh.consultations
UNION ALL SELECT 'prestations chargées', COUNT(*) FROM dwh.prestations
UNION ALL SELECT 'rejets du dernier run', COUNT(*) FROM audit.rejected_records
  WHERE run_id = (SELECT run_id FROM audit.rejected_records ORDER BY rejected_at DESC LIMIT 1);

SELECT table_source, regle, COUNT(*) AS nb_rejets
FROM audit.rejected_records
WHERE run_id = (SELECT run_id FROM audit.rejected_records ORDER BY rejected_at DESC LIMIT 1)
GROUP BY table_source, regle ORDER BY table_source, regle;