from celery import Celery
import os

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery = Celery(
    'backend_tasks',
    broker=redis_url,
    backend=redis_url,
)

celery.conf.update(task_serializer='json', accept_content=['json'], result_serializer='json')

@celery.task
def send_welcome_email(user_id, email):
    # Simulated background job. Replace with real email sending.
    print(f"[Celery] Sending welcome email to user {user_id} <{email}>")
    return True
