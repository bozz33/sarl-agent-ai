#!/usr/bin/env bash
set -euo pipefail

RESULT="$(
  docker exec -u hermes sarl-hermes-agent \
    /opt/hermes/.venv/bin/hermes -p sarl-router -z \
    'Test de routage canonique sans projet. Pour chaque demande, retourne exactement une ligne au format NUMERO|NIVEAU|AGENT|HUMAIN, sans commentaire. Demandes: 1 Résume ce texte. 2 Prépare un post LinkedIn. 3 Fais une veille IA. 4 Corrige ce bug Laravel. 5 Revois ce patch sécurité. 6 Déploie en production. 7 Supprime les anciennes données clients. 8 Modifie les DNS. 9 Analyse ce contrat engageant. 10 Crée une maquette 3D.'
)"

EXPECTED=(
  '1|SIMPLE|docs-scribe|non'
  '2|STANDARD|community-manager|oui'
  '3|STANDARD|research-sage|non'
  '4|AVANCEE|code-builder|non'
  '5|CRITIQUE|code-reviewer-critical|oui'
  '6|CRITIQUE|sarl-orchestrator-critical|oui'
  '7|CRITIQUE|sarl-orchestrator-critical|oui'
  '8|CRITIQUE|sarl-orchestrator-critical|oui'
  '9|CRITIQUE|sarl-orchestrator-critical|oui'
  '10|STANDARD|designer-3d-agent|oui'
)

for line in "${EXPECTED[@]}"; do
  grep -Fqx "$line" <<<"$RESULT" || {
    echo "Missing routing result: $line" >&2
    echo "$RESULT" >&2
    exit 1
  }
done

echo "ROUTING_10_10"
