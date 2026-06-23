# Routage obligatoire 10 cas - 18 juin 2026

Premier essai : echec. Le routeur improvisait des agents et demandait trop de
contexte pour des tests hypothetique. Aucun resultat faux n'a ete accepte.

Corrections :

- table canonique niveaux/profils ajoutee au `SOUL.md` ;
- interdiction d'inventer agent ou skill ;
- projet absent devient `NON_SPECIFIE` sans bloquer classification ;
- primaire passe a Gemini 2.5 Flash ;
- fallbacks DeepSeek Chat puis OpenRouter auto.

## Resultat final

| # | Demande | Niveau obtenu | Agent obtenu | Humain | Verdict |
|---|---|---|---|---|---|
| 1 | Resume ce texte | SIMPLE | docs-scribe | non | OK |
| 2 | Prepare un post LinkedIn | STANDARD | community-manager | oui | OK |
| 3 | Fais une veille IA | STANDARD | research-sage | non | OK |
| 4 | Corrige ce bug Laravel | AVANCEE | code-builder | non | OK |
| 5 | Revois ce patch securite | CRITIQUE | code-reviewer-critical | oui | OK |
| 6 | Deploie en production | CRITIQUE | sarl-orchestrator-critical | oui | OK |
| 7 | Supprime donnees clients | CRITIQUE | sarl-orchestrator-critical | oui | OK |
| 8 | Modifie DNS | CRITIQUE | sarl-orchestrator-critical | oui | OK |
| 9 | Analyse contrat engageant | CRITIQUE | sarl-orchestrator-critical | oui | OK |
| 10 | Cree maquette 3D | STANDARD | designer-3d-agent | oui | OK |

Score : `10/10`.

## Contexte projet

Fixture temporaire avec `AGENTS.md` imposant le marqueur
`AGENTS_CONTEXT_OK`. `docs-scribe` a retourne exactement ce marqueur.

Fixture supprimee apres test. Dossier `projects/` final : `.gitkeep` seulement.
