# ADR 0001 - Host the SPA on Vercel, keep the API on the VM

- **Status:** Accepted
- **Date:** 2026-11-08
- **Decision log:** D13 in [`docs/architecture.md`](../architecture.md#19-decision-log)

## Context

The hosted demo needs a public URL while keeping the API deployable with the same
compose file contributors run. Serving the SPA and API from Caddy on one VM is
simple but has no CDN and no per-pull-request preview. Git Together also
needs a zero-cost hosting story: every component except the AWS instance must
stay on a free tier.

Vercel Hobby can build and serve the Vite SPA for free, including preview
deployments and TLS. It cannot host the API: uploads need a persistent disk,
ingestion uses `BackgroundTasks`, and the Python image is far outside practical
function bundle limits.

## Decision

- Vercel Hobby hosts the static SPA, built from `frontend/` with
  `npm run build` and served from `dist/`.
- The API, Postgres, uploads, and the Caddy edge stay on a single ARM64 EC2
  instance running the `prod` compose profile.
- The browser calls the API directly (no Vercel proxy), so the API owns an exact
  `ALLOWED_ORIGINS` CORS allowlist and the SPA sends a bearer token.
- `frontend/vercel.json` provides the SPA rewrite for client-side routes and the
  SPA's security headers.
- The Caddy SPA build remains in `infra/compose.prod.yml` as the same-origin
  fallback for local TLS smoke tests and for use if the Vercel project is
  unavailable.

## Consequences

- Cross-origin CORS becomes part of the API contract: preflight for
  `Authorization` and `X-Provider-Key`, `Vary: Origin`, and `Retry-After`
  exposure.
- Hosted guest sessions use a bearer token in `sessionStorage`. A cookie set by
  a different registrable domain is a third-party cookie and is blocked by
  Safari and Firefox, even with `SameSite=None`.
- Vercel Hobby is limited to personal, non-commercial use and can be suspended
  at Vercel's discretion. The static build is portable to another static host,
  so this is not a lock-in.
- The SPA has a second build path (Vercel) in addition to the Caddy image. This
  is the deliberate exception to the one-artifact principle.

## Alternatives considered

- **Caddy same-origin (D8):** simplest and already in the scaffold, but no CDN
  and no preview deployment per pull request.
- **Cloudflare Pages:** comparable free static hosting with no non-commercial
  clause, but it adds a second deployment target and was not the hosting chosen
  for the demo.
- **Proxy `/api/*` through Vercel rewrites:** avoids CORS, but streaming SSE
  through the CDN proxy is not guaranteed to stay incremental.
- **Serverless API on Vercel:** ruled out by persistent uploads, background
  ingestion, and image size.

## Verification

- A Vite React SPA is a supported Vercel framework preset; build command
  `npm run build` and output `dist` need no custom configuration, and the
  `vercel.json` rewrite is the documented fix for SPA deep links.
- Hobby includes 100 GB fast data transfer and 1,000,000 CDN requests per month,
  well above demo traffic for a ~350 KB bundle.
- Hobby permits 100 deployments per day, enough for Git Together.
- The API build is already `linux/arm64`-compatible; Vercel only receives static
  assets.
