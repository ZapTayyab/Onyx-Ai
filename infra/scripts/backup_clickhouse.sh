#!/bin/bash
# =============================================================================
# SNT AI — ClickHouse Backup Script
# =============================================================================
# Streams every table in the database out as a gzipped TabSeparated dump
# (one .tsv.gz per table, named snt_ai_<timestamp>_<table>.tsv.gz).
# Restore with: zcat file.tsv.gz | clickhouse-client --query
#   "INSERT INTO <db>.<table> ... FORMAT TabSeparated"
#
# Environment variables required:
#   CLICKHOUSE_HOST       — Host (default: localhost)
#   CLICKHOUSE_PORT       — HTTP port (default: 8123)
#   CLICKHOUSE_USER       — ClickHouse user (default: default)
#   CLICKHOUSE_PASSWORD   — ClickHouse password
#   CLICKHOUSE_DB         — Database to back up (default: snt_ai)
#   BACKUP_DEST           — Local directory (default: /backups/clickhouse)
#
# Optional (for S3 upload):
#   S3_BUCKET             — e.g. s3://my-bucket/snt-backups/clickhouse
#
# Cron suggestion (daily at 03:00):
#   0 3 * * * /opt/snt/scripts/backup_clickhouse.sh >> /var/log/snt-backup.log 2>&1
# =============================================================================
set -euo pipefail

CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
CLICKHOUSE_PORT="${CLICKHOUSE_PORT:-8123}"
CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
CLICKHOUSE_DB="${CLICKHOUSE_DB:-snt_ai}"
BACKUP_DEST="${BACKUP_DEST:-/backups/clickhouse}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="snt_ai_${TIMESTAMP}"
RETAIN_DAYS="${RETAIN_DAYS:-30}"

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting ClickHouse backup → ${BACKUP_DEST}/${BACKUP_NAME}"
mkdir -p "${BACKUP_DEST}"

# Get list of all tables in the database
TABLES=$(curl -sS \
    -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
    "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
    --data "SELECT name FROM system.tables WHERE database = '${CLICKHOUSE_DB}' FORMAT TabSeparated")

for TABLE in ${TABLES}; do
    OUTFILE="${BACKUP_DEST}/${BACKUP_NAME}_${TABLE}.tsv.gz"
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Dumping ${CLICKHOUSE_DB}.${TABLE} → ${OUTFILE}"
    curl -sS \
        -u "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
        "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
        --data "SELECT * FROM ${CLICKHOUSE_DB}.${TABLE} FORMAT TabSeparated" \
        | gzip > "${OUTFILE}"
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Done: $(du -sh "${OUTFILE}" | cut -f1)"
done

# Optional: upload to S3
if [[ -n "${S3_BUCKET:-}" ]]; then
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Uploading to ${S3_BUCKET} …"
    for OUTFILE in "${BACKUP_DEST}"/${BACKUP_NAME}_*.tsv.gz; do
        aws s3 cp "${OUTFILE}" "${S3_BUCKET}/${BACKUP_NAME}/" --storage-class STANDARD_IA
    done
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Upload complete."
fi

# Prune old backups
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Pruning backups older than ${RETAIN_DAYS} days …"
find "${BACKUP_DEST}" -name "snt_ai_*.tsv.gz" -mtime "+${RETAIN_DAYS}" -delete

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] ClickHouse backup complete."
