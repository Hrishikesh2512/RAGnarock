# Security Policy

The RAGnarok team takes the security of our application, our users, and our contributors seriously. This document outlines our supported versions, security model, and reporting process.

---

## Supported Versions

We provide security patches and updates for the following versions:

| Version | Supported | Notes |
| :--- | :--- | :--- |
| `0.1.x` (v1) | :white_check_mark: | Current active release branch (`main`) |
| `< 0.1.0` | :x: | Pre-release scaffolds; unsupported |

---

## Security Model & Privacy Guarantees

RAGnarok is designed around a strict zero-trust credential architecture:

1. **BYOK (Bring Your Own Key):**
   * LLM API keys (e.g. OpenRouter) are **never** stored in the database, configuration files, environment variables, or disk volumes.
   * Keys are passed per-request via the `X-Provider-Key` header and held solely in browser tab memory (`sessionStorage`).
2. **Access Log Redaction:**
   * HTTP request logging middleware explicitly strips and redacts sensitive headers, including `Authorization`, `X-Provider-Key`, and `Cookie`.
3. **Local & In-Memory Embeddings:**
   * Document and query embeddings are computed locally on the server using CPU models (`bge-small-en-v1.5`). Document content and embeddings are never dispatched to third-party embedding APIs.
4. **Isolated Workspaces & Repositories:**
   * Database queries strictly filter by `user_id` below the route layer to prevent horizontal privilege escalation.

---

## Reporting a Vulnerability

If you discover a security vulnerability in RAGnarok, **do not open a public GitHub issue**. Public issues disclose the problem before a fix exists.

Git Together contributors: tell a mentor in person. Do not put exploit detail in an event issue or pull request.

### Reporting Process

1. **Email or Private Advisory:**
   * Send a report to the maintainers at `security@nodedotai.org` (or submit a private vulnerability report via [GitHub Security Advisories](https://github.com/bit-nodedotai/RAGnarok/security/advisories/new)).
2. **Include Details:**
   * A clear description of the vulnerability.
   * Exact steps to reproduce or a proof of concept (PoC).
   * Potential impact and affected components (backend, frontend, or infrastructure).
3. **Response Timeline:**
   * **Acknowledgment:** Within **48 hours** of receiving your report.
   * **Triage & Status:** Within **5 business days**, detailing validity and planned remediation.
   * **Disclosure:** Coordinated public release after a patch has been merged and verified.

---

## Responsible Disclosure

We kindly ask reporters to:
- Give us reasonable time to investigate and resolve the issue before making any information public.
- Make a good-faith effort to avoid privacy violations, data destruction, and interruption or degradation of service during testing.
- Not access or modify data belonging to other users.

We appreciate the efforts of security researchers and open-source contributors who help keep RAGnarok safe for everyone.

