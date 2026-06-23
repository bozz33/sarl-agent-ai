# Rollback phase 2

Backup de reference :

```text
/root/SARL-agent-ai-rollback/pre-phase2-20260618T144910Z
```

Verification :

```bash
cd /root/SARL-agent-ai-rollback/pre-phase2-20260618T144910Z
sha256sum -c SHA256SUMS
```

Restauration complete :

```bash
sudo ./restore.sh
```

Le script restaure projet, images et volumes, puis relance Compose.
PostgreSQL reste manuel pour eviter l'ecrasement accidentel d'une base recente.

