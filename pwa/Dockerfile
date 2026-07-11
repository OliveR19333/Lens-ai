# Build the PWA and serve it via Caddy (auto-HTTPS) — used by
# infra/docker-compose.prod.yml. Build context is the REPO ROOT so we can copy
# both pwa/ and infra/Caddyfile.
#
#   docker build -f pwa/Dockerfile -t gas-web .

# ---- stage 1: build the static PWA ----
FROM node:20-alpine AS build
WORKDIR /app
COPY pwa/package*.json ./
RUN npm ci || npm install
COPY pwa/ .
# Same-origin API: axios baseURL "/api" → Caddy proxies to the backend. No
# domain baked in, so the same image works for any DOMAIN.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# ---- stage 2: serve with Caddy ----
FROM caddy:2-alpine
COPY infra/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv/pwa
EXPOSE 80 443
