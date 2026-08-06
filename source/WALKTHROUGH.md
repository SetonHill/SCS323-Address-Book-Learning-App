# Step-Numbered Walkthrough

## Step 1 — Read the boundary

Location: repository root. Purpose: understand that this app contains only synthetic contacts and no authentication. Replace placeholders only in `.env`; never paste secrets into evidence.

## Step 2 — Follow one request

Open `app/main.py`, `app/validation.py`, `app/models.py`, and `app/templates/contact_form.html`. Trace browser form → FastAPI route → validation → SQLAlchemy transaction → redirect → Jinja response.

## Step 3 — Explain the schema

Open `alembic/versions/0001_create_address_book.py`. Identify each primary key, foreign key, cascade, constraint, and index. Explain why dependent address and phone facts do not belong as repeating columns in `contacts`.

```sql
SELECT c.first_name, c.last_name, a.city, p.phone_number
FROM contacts AS c
LEFT JOIN addresses AS a ON a.contact_id = c.id
LEFT JOIN phone_numbers AS p ON p.contact_id = c.id
ORDER BY c.last_name, c.first_name;
```

Expected: one contact may produce several joined rows because addresses and phone numbers are one-to-many relationships.

## Step 4 — Build the containers

Run the QUICKSTART commands. `compose.yaml` defines the app, private database, health checks, and named volume. The Dockerfile installs pinned dependencies and runs as the unprivileged `app` user.

## Step 5 — Exercise behavior

Create a contact, add an address and phone, search by name, edit the last name, remove the dependent records, and confirm deletion. Try an invalid email and duplicate email; the page should explain the problem without a traceback or database details.

## Step 6 — Read health and logs

```shell
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/ready
docker compose logs --tail=30 app
```

Expected: metadata names version `1.0.0`; logs contain event names but no contact values, credentials, or SQL parameters.

## Step 7 — Run tests

```shell
docker compose exec app pytest
```

Unit tests cover validation. Integration/database tests cover health, readiness, create, address, phone, search, edit, delete, and duplicate-email recovery.

## Step 8 — Recover safely

- Database unhealthy: inspect `docker compose logs database`; do not expose port 5432.
- App exits: preserve the first exception and verify `DATABASE_URL` names service `database`.
- Migration fails: stop, preserve output, and correct the migration through review; do not edit the live schema manually.
- Port busy: stop the conflicting local project; do not change production mappings silently.
- Need a disposable reset: first confirm all data is synthetic and unneeded, then run `docker compose down --volumes`, rebuild, migrate, and seed. Never use that reset on the CyberRange production VM.

## Step 9 — Use the course workflow

Open an issue, run Issue Planner, create a short-lived branch, make focused commits, open a pull request, run checks and Pull Request Reviewer, disposition findings, and merge only when the course conditions are satisfied. Agents cannot approve, merge, deploy, grade, or author your explanation.

## Step 10 — Prepare Week 8 deployment

Later, follow Lab 04 and the companion deployment guide. Deploy the exact reviewed release beneath the assigned `/opt/SCS323` directory on the CyberRange VM. A Git push is not deployment. Never copy uncommitted MacBook files or publish private addresses, credentials, or configuration.
