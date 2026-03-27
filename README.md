# Trips Planner MVP 1

This repository now follows the MVP 1 split architecture:

- `frontend/`: Next.js App Router app for UI and SSR, intended for Vercel
- `backend/`: FastAPI modular monolith for business logic and persistence, intended for Render
- PostgreSQL: managed database accessed only by the backend

## Run Everything With Docker

1. Copy the optional Docker env file if you need Google integrations:

```bash
cp .env.docker.example .env
```

2. Start the full stack:

```bash
docker compose up --build
```

3. Open the apps:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Backend health: http://localhost:8000/health
- PostgreSQL: localhost:5432

The frontend container runs in `next dev` mode with bind-mounted source, and the backend container runs with `uvicorn --reload` plus bind-mounted source. Changes under `frontend/` or `backend/` should reload automatically without restarting their containers.

All application routes under `/dashboard` and `/trips` require login and redirect to `/login` when there is no backend session.

4. Stop everything:

```bash
docker compose down
```

5. Stop and remove DB data too:

```bash
docker compose down -v
```

## Local development without Docker

### PostgreSQL

```bash
docker run --name trips-postgres   -e POSTGRES_USER=postgres   -e POSTGRES_PASSWORD=postgres   -e POSTGRES_DB=trips_planner   -p 5432:5432   -d postgres:16
```

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
