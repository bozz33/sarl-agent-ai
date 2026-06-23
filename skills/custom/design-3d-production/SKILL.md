---
name: design-3d-production
description: Concevoir, auditer et produire des workflows 3D professionnels avec Blender, FreeCAD, glTF, USD, rendu, géométrie procédurale, optimisation temps réel et contrôle des licences. Utiliser pour concepts 3D, scènes, assets, visualisation architecturale, scripts Blender Python, exports, rendus, maquettes techniques et diagnostics de pipeline.
---

# Production 3D

## Charger les références utiles

- Lire `references/workflow.md` pour toute production.
- Lire `references/official-sources.md` avant recherche, choix de version ou affirmation technique.
- Lire `references/quality-gates.md` avant export ou livraison.

## Exécuter

1. Définir usage final: image, animation, temps réel, fabrication, BIM ou échange CAO.
2. Fixer unités, repère, échelle, tolérances, format, version logicielle et budget machine.
3. Séparer géométrie source, dérivés, textures, caches, rendus et exports.
4. Préserver provenance, licences, profils colorimétriques et droits des assets.
5. Choisir pipeline:
   - Blender pour modélisation, shading, animation, Geometry Nodes et rendu.
   - FreeCAD pour géométrie paramétrique, dimensions contraintes et échanges CAO.
   - glTF/GLB pour livraison temps réel.
   - USD pour scènes complexes, variantes et interchange DCC.
6. Automatiser opérations répétables par script versionné. Ne pas utiliser clics manuels comme seule procédure.
7. Valider scène puis export avec `references/quality-gates.md`.
8. Produire rapport: hypothèses, versions, sources, paramètres, limites, fichiers, contrôles, anomalies.

## Règles

- Ne jamais inventer dimensions, matériaux, performances ou licences.
- Ne jamais confondre visuel plausible et géométrie fabricable.
- Signaler approximation, non-manifold, intersections, normales, UV, échelle ou texture manquante.
- Ne jamais livrer comme “BIM conforme” sans schéma IFC, propriétés et validation métier.
- Ne jamais publier, acheter un asset ou lancer rendu coûteux sans validation humaine.
- Préférer documentation officielle correspondant exactement à version installée.

## Apprentissage

Lors d’une veille officielle:

1. Lire `references/official-sources.md`.
2. Vérifier uniquement changements depuis date du dernier rapport.
3. Distinguer documentation normative, note de version et exemple communautaire.
4. Écrire synthèse sourcée dans dossier `knowledge/official-research/`.
5. Mettre à jour `knowledge/CURRENT.md` avec faits encore valides, versions et dates.
6. Proposer modification du skill ou SOUL; ne jamais les réécrire automatiquement.
