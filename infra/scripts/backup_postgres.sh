#!/bin/bash
# =============================================================================
# SNT AI — Postgres Backup Script
# =============================================================================
# Creates a timestamped compressed pg_dump and optionally uploads it to S3/GCS.
#
# Environment variables required:
#   POSTGRES_USER       — Postgres user (e.g. sntprod)
#   POSTGRES_PASSWORD   — Postgres password
#   POSTGRES_HOST       — Host (default: localhost)
#   POSTGRES_DB         — Database name (default: snt_ai)
#   BACKUP_DEST         — Local directory to write backups (default: /backups/postgres)
#
# Optional (for S3 upload):
#   S3_BUCKET           — e.g. s3://my-bucket/snt-backups/postgres
#   AWS_PROFILE / AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
#
# Cron suggestion (daily at 02:00):
#   0 2 * * * /opt/snt/scripts/backup_postgres.sh >> /var/log/snt-backup.log 2>&1
# =============================================================================
set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_DB="${POSTGRES_DB:-snt_ai}"
BACKUP_DEST="${BACKUP_DEST:-/backups/postgres}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="snt_ai_${TIMESTAMP}.dump.gz"
FILEPATH="${BACKUP_DEST}/${FILENAME}"
RETAIN_DAYS="${RETAIN_DAYS:-30}"

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting Postgres backup → ${FILEPATH}"
mkdir -p "${BACKUP_DEST}"

PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "${POSTGRES_HOST}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    -Fc \
    --no-password \
    | gzip > "${FILEPATH}"

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup written: ${FILEPATH} ($(du -sh "${FILEPATH}" | cut -f1))"

# Optional: upload to S3
if [[ -n "${S3_BUCKET:-}" ]]; then
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Uploading to ${S3_BUCKET}/${FILENAME} …"
    aws s3 cp "${FILEPATH}" "${S3_BUCKET}/${FILENAME}" --storage-class STANDARD_IA
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Upload complete."
fi

# Prune backups older than RETAIN_DAYS
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Pruning backups older than ${RETAIN_DAYS} days …"
find "${BACKUP_DEST}" -name "snt_ai_*.dump.gz" -mtime "+${RETAIN_DAYS}" -delete

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Postgres backup complete."
