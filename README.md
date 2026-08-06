# SCS323 Address Book Learning App

Version: 1.0.0

This public, semester-neutral repository is the canonical SCS323 Address Book learning application. Release `v1.0.0` is the unauthenticated CRUD baseline for learning FastAPI, server-rendered HTML, PostgreSQL, Alembic, Docker Compose, testing, and request tracing.

It is a learning and reference application, not a production identity system and not a student's semester project. Graded semester work belongs in the assigned organization-owned private team repository. Do not make a personal repository the authoritative course record.

## Get the Baseline With Git

```shell
git clone https://github.com/SetonHill/SCS323-Address-Book-Learning-App.git
cd SCS323-Address-Book-Learning-App
git switch --detach v1.0.0
cd source
```

The detached tag is the reproducible reference. To modify the baseline for an instructor-directed practice exercise, create your own local branch before editing:

```shell
git switch -c lab/address-book-practice
```

Do not push practice work to this canonical repository. Follow the course directions for evidence and for any later transition to the assigned private team repository.

## Download From the Web

Open the repository's **Code** menu and choose **Download ZIP**, then extract it and open the `source` directory. A ZIP download is suitable for running the example but does not contain Git history or support branch practice. Use the Git method when the activity requires commits or branches.

## Configure and Run

From `source`:

```shell
cp .env.example .env
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
docker compose exec app alembic upgrade head
docker compose exec app python -m app.seed
docker compose exec app pytest
```

Replace the password placeholder in `.env` with a local-only development password. Never commit or share `.env`. Open <http://127.0.0.1:8000>, then stop safely:

```shell
docker compose down
```

Detailed application guidance is in [`source/QUICKSTART.md`](source/QUICKSTART.md) and [`source/WALKTHROUGH.md`](source/WALKTHROUGH.md).

## Authentication Progression

Version `v1.0.0` intentionally has no accounts, login, or authorization. [`docs/AUTHENTICATION-PROGRESSION.md`](docs/AUTHENTICATION-PROGRESSION.md) defines the instructor/reference progression planned for `v1.1.0` without publishing a completed solution as the default starting point. Stable companion references are listed in [`docs/COMPANION-LINKS.md`](docs/COMPANION-LINKS.md).

## Provenance and License

The 33-file `source` tree is preserved byte-for-byte from the verified protected source identified in [`PROVENANCE.md`](PROVENANCE.md). No open-source license has been added because no organization-approved license was present in that source. Public visibility alone does not grant permission beyond applicable law and explicit course authorization.
