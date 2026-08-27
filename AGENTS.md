# SNT AI — Run Commands

- Full stack (Docker, builds images, runs infra + backend :8000):
  ```
  docker compose -f infra/docker-compose.yml up --build
  ```
  Add `-d` to run detached; stop with `docker compose -f infra/docker-compose.yml down`.
- Frontend (local dev): `cd frontend && npm run dev` — http://localhost:3000
- Backend only (infra already up): `docker compose -f infra/docker-compose.yml up backend frontend`
- Backend API / Swagger: http://localhost:8000 / http://localhost:8000/docs
- Dev login (dev-only, `backend/app/routers/auth.py`): `admin@snt.ai` / `admin`