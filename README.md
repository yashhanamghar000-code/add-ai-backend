# add-ai-backend

The API gateway / composition root. Owns the FastAPI app, HTTP routers,
and the use-case layer (`ChatWorkflowService`, `RetrievalService`,
`HistoryService`, `SessionService` — copied from the original monolith
**unmodified**, since they only ever depended on interfaces, never
concrete infrastructure). What changed is `app/container.py` and
`app/clients/*`: every adapter that used to be an in-process object
(loaded model, DB session, Qdrant client) is now a small HTTP client
pointed at another repo's service.

This repo also holds NO secrets and NO database connection — it forwards
auth to `add-ai-auth-service` and every repository call to
`add-ai-data-service`.

## Talks to (via env vars, see `.env.example`)
`add-ai-embeddings-service`, `add-ai-reranker-service`, `add-ai-llm-service`,
`add-ai-vectorstore-service`, `add-ai-sparseindex-service`,
`add-ai-data-service`, `add-ai-auth-service`, and Redis (to enqueue
ingestion jobs that `add-ai-worker` picks up — this repo never imports
the worker's task code, only its task *name*, so the two can be
deployed independently).

## API
Unchanged from the original monolith — the frontend needs zero changes:
- `POST /api/auth/register`, `/login`, `GET /me`, `POST /logout`
- `POST /api/upload`, `GET /api/upload/status/{task_id}`
- `POST /api/chat`
- `GET /api/conversations`, `GET /api/conversations/{session_id}/files`
- `GET /api/chat/history/{user_id}/{session_id}`
- `DELETE /api/session/{session_id}`, `DELETE /api/documents/{file_id}`
- `GET /api/documents/{file_id}/file`

## Run the full stack standalone
Build every other repo's image first (or `docker compose build` from
`add-ai-orchestration`), then:
```bash
cp .env.example .env
docker compose up --build
```
This repo's own `docker-compose.yml` brings up every dependency
(Postgres, Qdrant, Redis, and all 7 other services) so you can exercise
the whole API from one place without hand-wiring six other repos'
compose files together.

## Local dev (live reload)
```bash
docker compose up --build   # docker-compose.override.yml bind-mounts ./app and ../add-ai-core
```
or outside Docker:
```bash
pip install -r requirements.txt && pip install -e ../add-ai-core
uvicorn app.main:app --reload --port 8000
```
Point the `*_SERVICE_URL` env vars at `localhost:<port>` if you're
running the other services outside Docker too, or leave them as
Docker service names if the rest of the stack is in containers.

## Note: no worker in this repo
Uploading enqueues a Celery job by name (`app.tasks.process_document_task`)
via Redis — it does not import or run the task. You need
`add-ai-worker` running (with a shared `storage` volume, see
`add-ai-orchestration`) for uploads to actually get ingested.
