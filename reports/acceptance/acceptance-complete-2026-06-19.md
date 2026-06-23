# Acceptation SARL-Agent-AI - 19 juin 2026

## Verdict

Le socle complet sans projet et sans provider premium est fonctionnel.

Marqueurs finaux :

```text
SARL_ACCEPTANCE_OK
MODEL_WORKFLOW_SMOKE_OK
KANBAN_WORKFLOW_OK
ROUTAGE_10_10
```

## Tests valides

- quatre conteneurs actifs et sains ;
- ports Hermes limites a `127.0.0.1` ;
- MCP et sandbox sans port hote publie ;
- reseau sandbox interne ;
- controle sandbox par socket Unix partage, sans API TCP ;
- image Python/Node approuvee prechargee et executee ;
- ecriture Workspace avec UID applicatif ;
- 6/6 tests unitaires du hook ;
- blocage runtime d'une commande `docker compose down` ;
- hook doctor sur 17 profils ;
- checkpoints actifs sur 17 profils ;
- MCP memoire teste sur 17 profils ;
- 13/13 tests MCP dont integration PostgreSQL reelle ;
- ecriture et recherche semantique Gemini/pgvector reelles ;
- 100 sessions MCP par lots sans fuite PostgreSQL ;
- nettoyage final : zero projet DB, zero memoire, zero chunk ;
- worktree reel cree puis nettoye ;
- workflow Kanban cree, commente, reassigne, termine et archive ;
- 13 profils valides sans outil ;
- `code-builder` et `qa-agent` valides avec terminal sandbox reel ;
- routage canonique valide 10/10 ;
- timer systemd governor/steward actif et tick reussi ;
- checksums et extraction isolee du backup valides ;
- aucun projet present dans `projects/`, hors `.gitkeep`.

## Dependances externes non activables automatiquement

- Claude/Anthropic : credential absent ;
- OpenAI/Codex : credential ou OAuth absent ;
- Tailscale : installation/authentification administrateur absente ;

Les profils `codex-builder` et `code-reviewer-critical` restent donc
volontairement inactifs. Aucun credential, modele premium ou acces reseau n'a
ete invente.
