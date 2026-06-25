# Roster — sources de vérité

Trois fichiers décrivent les agents. Ils doivent rester alignés.

- `swarm.yaml` — workers Swarm (exécution) : **18**.
- `scripts/configure-active-profiles.py` — profils Hermes configurés : **19**
  (les 18 workers + `sarl-orchestrator-critical`, variante critique sans worker Swarm).
- `profiles/<nom>/SOUL.md` — identités versionnées : **19** (alignées).

## Table d'alignement

| Profil | Worker Swarm | Profil configuré | SOUL versionné |
|---|:---:|:---:|:---:|
| sarl-router | ✅ | ✅ | ✅ |
| sarl-orchestrator | ✅ | ✅ | ✅ |
| sarl-orchestrator-critical | — | ✅ | ✅ |
| sarl-governor | ✅ | ✅ | ✅ |
| sarl-stack-steward | ✅ | ✅ | ✅ |
| code-builder | ✅ | ✅ | ✅ |
| codex-builder | ✅ | ✅ | ✅ |
| code-reviewer | ✅ | ✅ | ✅ |
| code-reviewer-critical | ✅ | ✅ | ✅ |
| qa-agent | ✅ | ✅ | ✅ |
| research-sage | ✅ | ✅ | ✅ |
| docs-scribe | ✅ | ✅ | ✅ |
| ops-foundation | ✅ | ✅ | ✅ |
| cpanel-watch-agent | ✅ | ✅ | ✅ |
| security-audit-agent | ✅ | ✅ | ✅ |
| community-manager | ✅ | ✅ | ✅ |
| support-agent | ✅ | ✅ | ✅ |
| designer-3d-agent | ✅ | ✅ | ✅ |
| bureau-etudes-agent | ✅ | ✅ | ✅ |

## État

Roster aligné. Les 19 SOUL sont versionnés dans `profiles/<nom>/SOUL.md`
(les 12 manquants ont été extraits du volume `hermes-agent-data` actif et tracés).

`sarl-orchestrator-critical` reste sans worker Swarm dédié : c'est une variante
critique du profil orchestrateur, invoquée manuellement (cf. `project.yaml`).

Pour resynchroniser après modification d'un SOUL en production :
`docker exec sarl-hermes-agent cat /opt/data/profiles/<nom>/SOUL.md`.
