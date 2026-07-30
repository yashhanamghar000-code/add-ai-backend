"""
add-ai-backend only ENQUEUES ingestion jobs — the task implementation
lives entirely in add-ai-worker. Importing celery_app + task code from
another repo would recouple the two at the Python-import level, which
defeats the point of separate repos/images. `send_task` by string name
avoids that: this repo only needs to agree with add-ai-worker on the
task's *name* and *argument order*, both documented in both READMEs.
"""
from celery import Celery

from app.config.settings import settings

celery_client = Celery("add_ai_backend_producer", broker=settings.redis_url, backend=settings.redis_url)


def enqueue_ingestion(file_path: str, file_name: str, user_id: str, session_id: str, file_id: str):
    return celery_client.send_task(
        "app.tasks.process_document_task",
        args=[file_path, file_name, user_id, session_id, file_id],
    )
