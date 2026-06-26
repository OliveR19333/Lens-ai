#!/usr/bin/env bash
# One-paste production bootstrap for the GAS Property Mapping System.
#
# Run on a FRESH Ubuntu 22.04/24.04 server (e.g. Hetzner CPX41, Ashburn) as root:
#
#   curl -fsSL https://raw.githubusercontent.com/OliveR19333/Lens-ai/claude/new-session-hzjb8c/infra/bootstrap.sh | bash
#
# (or: git clone the repo, then `sudo bash infra/bootstrap.sh`)
#
# It installs Docker, fetches the code, asks for your domain + admin password,
# generates the other secrets, brings up the full stack with automatic HTTPS,
# and initializes the database. Re-running it is safe.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/OliveR19333/Lens-ai.git}"
BRANCH="${BRANCH:-claude/new-session-hzjb8c}"
APP_DIR="${APP_DIR:-/opt/gas-mapping}"

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
info() { printf "  %s\n" "$1"; }

bold "▶ GAS Property Mapping — server bootstrap"

# --- 1. Docker ---
if ! command -v docker >/dev/null 2>&1; then
  bold "Installing Docker…"
  curl -fsSL https://get.docker.com | sh
fi
docker compose version >/dev/null 2>&1 || { echo "Docker Compose plugin missing"; exit 1; }

# --- 2. Code ---
if [ ! -d "$APP_DIR/.git" ]; then
  bold "Cloning repository → $APP_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  bold "Updating repository in $APP_DIR"
  git -C "$APP_DIR" pull --ff-only || true
fi
cd "$APP_DIR"

# --- 3. Secrets / config (prompt only for what a human must choose) ---
gen() { openssl rand -base64 36 | tr -d '\n/+=' | cut -c1-40; }

read -rp "Domain for the app (e.g. mapping.example.com): " DOMAIN
read -rp "Admin username [admin]: " ADMIN_USERNAME
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
read -rsp "Admin password (your login): " ADMIN_PASSWORD; echo
[ -n "$DOMAIN" ] && [ -n "$ADMIN_PASSWORD" ] || { echo "Domain and admin password are required."; exit 1; }

JWT_SECRET="$(gen)$(gen)"
POSTGRES_PASSWORD="$(gen)"

# backend/.env — app secrets
if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; fi
set_kv() { # key value file
  if grep -q "^$1=" "$3"; then
    sed -i "s|^$1=.*|$1=$2|" "$3"
  else
    echo "$1=$2" >> "$3"
  fi
}
set_kv ADMIN_USERNAME "$ADMIN_USERNAME" backend/.env
set_kv ADMIN_PASSWORD "$ADMIN_PASSWORD" backend/.env
set_kv JWT_SECRET "$JWT_SECRET" backend/.env
set_kv DATABASE_URL "postgresql+psycopg2://gas:${POSTGRES_PASSWORD}@db:5432/gas_mapping" backend/.env

# infra/.env — values docker compose interpolates
cat > infra/.env <<EOF
DOMAIN=$DOMAIN
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
WEBODM_BASE_URL=http://host.docker.internal:8000/api
EOF

# --- 4. Bring up the stack ---
bold "Building and starting the stack (first run pulls images — a few minutes)…"
cd infra
docker compose -f docker-compose.prod.yml up -d --build

bold "Waiting for the backend to be reachable…"
for i in $(seq 1 60); do
  if docker compose -f docker-compose.prod.yml exec -T backend python -c "import urllib.request as u; u.urlopen('http://localhost:8080/health')" >/dev/null 2>&1; then
    break
  fi
  sleep 3
done

bold "Initializing the database…"
docker compose -f docker-compose.prod.yml exec -T backend python -m app.cli initdb

cat <<EOF

────────────────────────────────────────────────────────────────────
✅ Stack is up.

Next:
  1. Point DNS: an A record for  $DOMAIN  →  this server's IP.
     Caddy will fetch an HTTPS certificate automatically once DNS resolves
     (give it a minute or two on first request).
  2. Open  https://$DOMAIN  and log in as  $ADMIN_USERNAME  / (your password).
  3. iPhone: open that URL in Safari → Share → Add to Home Screen.
  4. Parcel data: Settings → Import (download a county GeoJSON from
     https://tn-tnmap.opendata.arcgis.com/ ).
  5. WebODM (photos → maps):  bash $APP_DIR/infra/setup-webodm.sh
  6. AI model:  python $APP_DIR/backend/scripts/fetch_model.py <roboflow .pt url> \\
                  $APP_DIR/infra/models/yolov8n-aerial-property.pt

Add a teammate:
  docker compose -f $APP_DIR/infra/docker-compose.prod.yml exec backend \\
    python -m app.cli createuser devan a-temp-password "Devan Teaster"
────────────────────────────────────────────────────────────────────
EOF
