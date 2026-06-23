---
name: engineering-design-office
description: Produire et auditer études techniques, notes de calcul, dimensionnements préparatoires, BIM/IFC, variantes et dossiers de bureau d’études avec traçabilité des données, unités, normes, hypothèses, calculs et revues. Utiliser pour structures, bâtiment, génie civil, mécanique, énergie, métrés, risques techniques et vérification documentaire.
---

# Bureau d’études

## Charger les références

- Toujours lire `references/study-method.md`.
- Lire `references/official-sources.md` avant toute citation normative.
- Lire `references/review-gates.md` avant conclusion ou livraison.

## Méthode

1. Identifier pays, juridiction, phase projet, discipline et responsabilité.
2. Établir registre des entrées: source, date, unité, précision, statut.
3. Établir hypothèses et inconnues séparément.
4. Définir normes applicables, édition, annexe nationale et hiérarchie contractuelle.
5. Poser schéma physique, cas de charge, combinaisons et critères.
6. Effectuer calculs avec unités explicites et contrôles indépendants.
7. Tester sensibilité aux hypothèses dominantes.
8. Comparer variantes avec sécurité, coût, réalisation, maintenance et carbone.
9. Produire note reproductible avec équations, résultats intermédiaires et limites.
10. Soumettre conclusions engageant sécurité ou conformité à revue experte.

## Règles

- Une donnée sans source reste `INCONNUE`.
- Une hypothèse reste `HYPOTHESE`, jamais fait.
- Ne jamais appliquer Eurocode sans annexe nationale et contexte projet.
- Ne jamais annoncer conformité sur base d’un résumé web.
- Ne jamais remplacer ingénieur habilité, organisme de contrôle ou signature réglementaire.
- Refuser précision supérieure aux données disponibles.
- Utiliser SI par défaut; tracer toute conversion.

## Apprentissage

Veille officielle:

1. Contrôler éditions, corrigenda, annexes et dates dans `references/official-sources.md`.
2. Écrire synthèse avec portée, changement, impact et projet concerné.
3. Stocker rapport dans `knowledge/official-research/`.
4. Consolider seulement faits vérifiés dans `knowledge/CURRENT.md`.
5. Toute évolution de méthode, norme ou SOUL passe par revue `sarl-governor`.
