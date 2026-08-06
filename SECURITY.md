# Security

Version: 1.0.0

Use synthetic data only. Never commit `.env`, passwords, tokens, private keys, recovery codes, student records, private repository information, or infrastructure details. The committed `source/.env.example` contains placeholders only.

Report a suspected vulnerability or credential exposure privately through an approved private repository vulnerability-reporting mechanism when enabled, the official course or syllabus channel, or the university's official IT/security channel. Do not open a public issue containing sensitive details and do not reproduce a suspected secret.

If a credential is exposed, stop using it, report privately, revoke or rotate it, remove it from the current tree, determine with the authorized owner whether history remediation is required, and verify the scans. Deleting the latest file is not sufficient when the value remains in history.

The `v1.0.0` application has no authentication and is not production-ready. Any future session secret belongs in environment configuration, must be strong and unique outside local development, and must never be committed.
