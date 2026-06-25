# Roster — sources de vérité

Trois fichiers décrivent les agents. Ils doivent rester alignés.

- `swarm.yaml` — workers Swarm (exécution) : **18**.
- `scripts/configure-active-profiles.py` — profils Hermes configurés : **19**
  (les 18 workers + `sarl-orchestrator-critical`, variante critique sans worker Swarm).
- `profiles/<nom>/SOUL.md` — identités versionnées : **7**.

## Table d'alignement

| Profil | Worker Swarm | Profil configuré | SOUL versionné |
|---|:---:|:---:|:---:|
| sarl-router | ✅ | ✅ | ✅ |
| sarl-orchestrator | ✅ | ✅ | ✅ |
| sarl-orchestrator-critical | — | ✅ | ❌ |
| sarl-governor | ✅ | ✅ | ❌ |
| sarl-stack-steward | ✅ | ✅ | ❌ |
| code-builder | ✅ | ✅ | ❌ |
| codex-builder | ✅ | ✅ | ❌ |
| code-reviewer | ✅ | ✅ | ❌ |
| code-reviewer-critical | ✅ | ✅ | ❌ |
| qa-agent | ✅ | ✅ | ❌ |
| research-sage | ✅ | ✅ | ❌ |
| docs-scribe | ✅ | ✅ | ❌ |
| ops-foundation | ✅ | ✅ | ❌ |
| cpanel-watch-agent | ✅ | ✅ | ✅ |
| security-audit-agent | ✅ | ✅ | ✅ |
| community-manager | ✅ | ✅ | ✅ |
| support-agent | ✅ | ✅ | ❌ |
| designer-3d-agent | ✅ | ✅ | ✅ |
| bureau-etudes-agent | ✅ | ✅ | ✅ |

## Écart connu

**12 SOUL manquants** (profil configuré mais pas de `profiles/<nom>/SOUL.md`
versionné) : `sarl-orchestrator-critical`, `sarl-governor`, `sarl-stack-steward`,
`code-builder`, `codex-builder`, `code-reviewer`, `code-reviewer-critical`,
`qa-agent`, `research-sage`, `docs-scribe`, `ops-foundation`, `support-agent`.

Ces profils tournent (SOUL appliqué dans le volume `hermes-agent-data`) mais leur
identité n'est pas tracée dans Git → pas reproductible sur un nouveau VPS.

Action : extraire les SOUL actifs depuis le volume vers `profiles/<nom>/SOUL.md`,
ou les rédiger à partir des skills de module correspondants (`sarl-module-*`).
