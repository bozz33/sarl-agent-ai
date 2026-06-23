# Workflow de production

## Brief minimal

- Objectif et audience
- Dimensions, unités, repère, tolérances
- Images/plans/références et droits
- Logiciel/version et moteur de rendu
- Format source et livrables
- Budget polygones, textures, mémoire, rendu
- Date, niveau de finition, critères d’acceptation

## Structure recommandée

```text
project/
  source/
  references/
  geometry/
  textures/
  caches/
  renders/
  exports/
  scripts/
  reports/
```

## Pipeline

1. Bloquer volumes et caméra.
2. Valider échelle et proportions.
3. Construire topologie ou modèle paramétrique.
4. Nommer objets, collections, matériaux et variantes.
5. Déplier UV ou définir coordonnées procédurales.
6. Construire matériaux physiquement cohérents.
7. Éclairer, gérer exposition et colorimétrie.
8. Tester rendu brouillon.
9. Optimiser géométrie, instances, textures et caches.
10. Exporter copie dérivée; préserver source.
11. Réimporter export dans outil indépendant.

## Rapport

Inclure versions, unités, moteur, color management, polycount, taille textures,
temps de rendu, formats, licences, contrôles réussis et écarts ouverts.
