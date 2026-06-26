#!/usr/bin/env bash
# Set up WebODM (orthomosaic + elevation from drone photos, spec §7) on this host.
#
# WebODM is a large multi-container app of its own, so it runs from its official
# stack rather than inside our compose. This script clones and starts it, then
# prints the values to put in backend/.env.
#
#   ./setup-webodm.sh
#
# Requires Docker. First run downloads several GB and can take a while.
set -euo pipefail

WEBODM_DIR="${WEBODM_DIR:-$HOME/WebODM}"
WEBODM_PORT="${WEBODM_PORT:-8000}"

if [ ! -d "$WEBODM_DIR" ]; then
  echo "Cloning WebODM into $WEBODM_DIR ..."
  git clone --depth 1 https://github.com/OpenDroneMap/WebODM "$WEBODM_DIR"
fi

cd "$WEBODM_DIR"
echo "Starting WebODM on port $WEBODM_PORT ..."
./webodm.sh start --port "$WEBODM_PORT"

cat <<EOF

────────────────────────────────────────────────────────────────────
WebODM is starting at http://localhost:$WEBODM_PORT
1. Open it in a browser and create the admin account (first run).
2. Put these in backend/.env:

   WEBODM_BASE_URL=http://host.docker.internal:$WEBODM_PORT/api
   WEBODM_USERNAME=<the admin user you just created>
   WEBODM_PASSWORD=<that admin password>

3. Restart the backend:  docker compose -f infra/docker-compose.prod.yml up -d backend worker
────────────────────────────────────────────────────────────────────
EOF
