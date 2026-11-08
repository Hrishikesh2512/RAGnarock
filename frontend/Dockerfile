# syntax=docker/dockerfile:1

FROM node:22-alpine AS base

WORKDIR /app

ENV npm_config_update_notifier=false

# --- deps: reproducible install from the lockfile ---------------------------
FROM base AS deps

COPY package.json package-lock.json ./

RUN npm ci

# --- dev: source and node_modules are bind-mounted / volume-backed ---------
FROM deps AS dev

ENV CHOKIDAR_USEPOLLING=true

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# --- build: static assets for the edge image -------------------------------
FROM deps AS build

COPY . .

RUN npm run build
