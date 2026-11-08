# syntax=docker/dockerfile:1

# Build the SPA, then serve it from Caddy together with the API proxy.
# Build context is the repository root so both frontend and infra files are visible.

FROM node:22-alpine AS web-build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build

# --- runtime ----------------------------------------------------------------
FROM caddy:2-alpine AS runtime

COPY infra/Caddyfile /etc/caddy/Caddyfile

COPY --from=web-build /app/dist /srv

EXPOSE 80 443 443/udp
