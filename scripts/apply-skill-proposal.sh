#!/usr/bin/env bash
# Application SUPERVISEE d'une proposition d'auto-amelioration.
#
# Ce script n'applique AUCUN changement automatiquement. Il prepare un cadre de
# revue humaine: branche dediee, affichage de la proposition, rappel des etapes
# (sandbox -> governor -> validation -> merge). La modification reelle reste
# effectuee/validee par un humain.
#
# Usage:
#   scripts/apply-skill-proposal.sh <chemin-proposition.md>
#
# La proposition vient typiquement de
#   /opt/data/profiles/sarl-orchestrator/knowledge/improvement-proposals/
# (la copier d'abord dans le repo si besoin).

set -euo pipefail

PROPOSAL="${1:-}"
if [[ -z "$PROPOSAL" || ! -f "$PROPOSAL" ]]; then
  echo "Usage: $0 <chemin-proposition.md>" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SLUG="$(basename "$PROPOSAL" .md | tr -c 'a-zA-Z0-9._-' '-' | cut -c1-50)"
BRANCH="improve/${SLUG}"

echo "=== Proposition ==="
cat "$PROPOSAL"
echo
echo "=== Verifications de securite ==="
if grep -qiE 'VALIDATION_HUMAINE_REQUISE:\s*oui' "$PROPOSAL"; then
  echo "OK: la proposition exige une validation humaine."
else
  echo "ATTENTION: marqueur VALIDATION_HUMAINE_REQUISE: oui absent — a verifier." >&2
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo
echo "=== Branche de revue ==="
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  echo "Branche ${BRANCH} existe deja."
else
  git checkout -b "${BRANCH}" >/dev/null 2>&1 && echo "Branche creee: ${BRANCH}"
fi

cat <<EOF

=== Etapes supervisees a executer A LA MAIN ===
1. Appliquer le CHANGEMENT_PROPOSE sur la cible indiquee (skill/SOUL/script).
2. Tester en sandbox/worktree:
     scripts/acceptance-test.sh        # si applicable
     python3 -m py_compile <fichiers modifies>
3. Faire verifier par le governor (risque, cout, conformite).
4. Obtenir la validation humaine explicite.
5. Commit + merge uniquement apres validation.

Aucune modification n'a ete appliquee par ce script.
Branche courante: $(git rev-parse --abbrev-ref HEAD) (precedente: ${CURRENT_BRANCH})
EOF
