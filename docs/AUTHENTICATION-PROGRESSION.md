# Authentication Progression Reference

Version: 1.0.0
Target application release: 1.1.0

This is an instructor/reference specification for a later authentication progression. It is not a completed solution and does not change the `v1.0.0` unauthenticated CRUD baseline on the default branch.

Students begin from tag `v1.0.0` and create their own instructor-directed practice branch. Graded semester implementation belongs in the assigned organization-owned private team repository, not this public reference repository or a personal repository.

## Planned Reference Location

A completed reference, if separately authorized and reviewed, uses branch `solution/authentication-v1.1.0` and release tag `v1.1.0`. The solution branch must not replace `main` as the initial student experience. Do not create or cite that branch or tag as available until it exists and passes protected checks.

## Required Progression

1. **Registration:** accept a normalized email and password, reject duplicates safely, and return validation without revealing sensitive data.
2. **Password storage:** use a maintained adaptive password-hashing library with unique salts. Never store or log plaintext passwords or reversible encryption keys.
3. **Login and logout:** verify credentials using constant-time library behavior, establish a server-validated session, rotate session identifiers when appropriate, and invalidate the session on logout.
4. **Session protection:** load a strong session secret from environment configuration. Provide only a placeholder in `.env.example`. Use secure cookie attributes appropriate to the deployed environment and explain local HTTP limitations.
5. **Protected routes:** require authentication for contact pages and mutations. Redirect or reject unauthenticated requests consistently.
6. **Per-user ownership:** associate every contact with its owning user. Every read, update, and delete query must enforce ownership; object identifiers alone never grant access.
7. **Database migration:** add users, ownership keys, indexes, and constraints through a reviewed Alembic migration. Define how existing synthetic contacts receive a safe development owner without fabricating production identity.
8. **Authorization tests:** test registration, hashing, successful and failed login, logout, protected routes, session invalidation, ownership isolation, cross-user access denial, migration behavior, and absence of sensitive output.
9. **Production-secret guidance:** use an approved secret manager or deployment environment, rotate secrets through an authorized process, separate environments, require HTTPS, and never treat `.env` or classroom defaults as production-safe.

## Evidence Expectations

Record the issue and acceptance criteria, migration plan, threat assumptions, tests, required agent checkpoints, finding disposition, sanitized verification, and rollback. A likely secret finding stops work and cannot be overridden by a student.
