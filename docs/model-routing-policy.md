# Politique de routage modeles

## Principe

Utiliser le modele le moins couteux capable de reussir correctement.

| Niveau | Usage | Cible |
|---|---|---|
| SIMPLE | Resume, extraction, titre | Groq ou Gemini Flash |
| STANDARD | Documentation, recherche, support | Gemini, DeepSeek ou OpenRouter |
| AVANCEE | Code, debug, architecture | DeepSeek Reasoner, Codex si active |
| CRITIQUE | Production, securite, DB, juridique | Claude/GPT/Codex + humain |

Fallback technique gere panne, quota ou reseau. Escalade gere risque et
complexite. Aucun modele premium pour une tache simple.

