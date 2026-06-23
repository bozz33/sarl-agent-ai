# Tests profils avances economiques - 18 juin 2026

Profils crees et testes :

```text
sarl-governor       GOVERNOR_OK
sarl-stack-steward  STEWARD_OK
code-builder        BUILDER_OK
code-reviewer       REVIEWER_OK
qa-agent            QA_OK
ops-foundation      OPS_OK
```

Tous les gateways restent arretes.

## Modeles

| Profile | Primaire |
|---|---|
| `sarl-governor` | DeepSeek Reasoner |
| `sarl-stack-steward` | Gemini 2.5 Flash |
| `code-builder` | DeepSeek Chat |
| `code-reviewer` | DeepSeek Reasoner |
| `qa-agent` | OpenRouter Laguna free |
| `ops-foundation` | OpenRouter Laguna free |

Chaque profil possede doubles fallbacks.

## Securite

- `SOUL.md` dedie ;
- checkpoints actifs ;
- `sarl-policy-guard` allowliste ;
- `hermes hooks doctor` valide sur les six profils ;
- `code-builder` et `qa-agent` utilisent backend Docker ;
- daemon Docker inaccessible : execution code fail-closed ;
- aucun socket hote monte ;
- aucun projet charge.

Les profils code/QA ne doivent pas recevoir de tache executable avant mise en
place du daemon sandbox dedie.
