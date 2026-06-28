# AGENTS.md — SARL-Agent-AI

Lu par tout agent avant action, avec `project.yaml` et la skill
`sarl-agent-ai-operating-contract`.

## Projet

- `project_id`: **sarl-agent-ai** (voir `project.yaml` pour identité, contraintes,
  politique modèles, mémoire, risques).
- Ne jamais mélanger les projets. Identifier le `project_id` avant toute action.

## Contrat opérationnel (résumé)

1. Identifier `project_id`, lire `AGENTS.md`, `QUALITY.md`, `DELIVERY.md` + `project.yaml`.
2. Distinguer fait, hypothèse, décision, info obsolète.
3. Produire un rapport final structuré.
4. Écrire les décisions importantes en mémoire projet (MCP) quand active.
5. Ne jamais lire/afficher/modifier un secret sans autorisation explicite.
6. Ne jamais déployer, supprimer, migrer ou publier sans validation humaine.
7. Backup / checkpoint / commit avant toute modification importante.
8. Escalader en cas de doute.

## Gates qualité et livraison

- Lire `QUALITY.md` avant toute mission de code ou QA.
- Lire `DELIVERY.md` avant toute préparation de livraison.
- Une tâche code n'est pas terminée tant que tests/lint/typecheck/build/e2e
  applicables n'ont pas été exécutés ou explicitement déclarés indisponibles.
- Le merge, le déploiement, la migration, la suppression et toute action
  production restent soumis à validation humaine.

## Décision et délégation

- Toute mission entre par `sarl-orchestrator` (cerveau central), jamais
  directement par un agent spécialisé.
- L'orchestrateur décide, décompose, délègue, suit, consolide ; il n'exécute pas
  les actions critiques lui-même.
- `sarl-governor` vérifie (risque, coût, conformité, interdits) ; il ne décide
  pas à la place de l'orchestrateur.
- Humain valide les actions critiques (voir `project.yaml: human_validation_required`).

## Roster

- Central : sarl-router, sarl-orchestrator, sarl-governor, sarl-stack-steward.
- Dev : code-builder, codex-builder, code-reviewer, code-reviewer-critical, qa-agent.
- Recherche/doc : research-sage, docs-scribe.
- Ops : ops-foundation, cpanel-watch-agent, security-audit-agent.
- Métier : community-manager, support-agent, designer-3d-agent, bureau-etudes-agent.

## Modèles (voir `project.yaml: models`)

- Orchestration : Claude Sonnet / GPT (abonnement). Sérieux : DeepSeek. Simple :
  Gemini. Code avancé : Codex (codex-builder). Opus : exceptionnel, manuel.

## Style

- Garder le français quand l'utilisateur écrit en français.
- Terse : pas de remplissage, pas de longues explications sauf demande.
- Garder commandes, chemins, noms d'API, erreurs et code exacts.
- Pour les actions destructives, formulation normale claire avant action.
