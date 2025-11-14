from celery_worker import send_welcome_email
from celery_worker import celery

# convenience wrapper to call the background task
def schedule_welcome(user_id, email):
    send_welcome_email.delay(user_id, email)
