# Address Book Quick Start

This classroom application uses synthetic data only. It has no accounts, passwords, or authentication. Docker Desktop on the issued MacBook is the supported local-development environment.

## 1. Prepare configuration

```shell
cp .env.example .env
```

Open `.env` and replace only the local development password placeholder. Never commit `.env`.

## 2. Build and start

```shell
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Expected: `database` and `app` become healthy. If port 8000 is already allocated, stop the earlier local project instead of publishing PostgreSQL or choosing an undocumented production port.

## 3. Migrate, seed, and test

```shell
docker compose exec app alembic upgrade head
docker compose exec app python -m app.seed
docker compose exec app pytest
```

Expected: migration `0001` applies, three synthetic contacts are created once, and all tests pass.

## 4. Use the web app

Open <http://127.0.0.1:8000>. Search, create, edit, and delete a contact; add and remove an address and phone number. Check <http://127.0.0.1:8000/health> and <http://127.0.0.1:8000/ready>.

## 5. Stop safely

```shell
docker compose down
```

This retains the named PostgreSQL volume. `docker compose down --volumes` deletes the synthetic database and is used only for the explicitly documented reset after confirming nothing is needed.
