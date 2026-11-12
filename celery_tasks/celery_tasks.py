"""
celery workers will handle task and if it fails it retries up to 3 times with the time frame of 60 minute
if it finaly fails then it will mark the task as undone and log it to redis
"""


import asyncio

from utility import email as e

from celery_tasks.celery_instance import celery_app


@celery_app.task(bind=True, max_retries= 3)
def email_verify_token_task(self, email: str, token: str):
    try:
        asyncio.run(e.send_email_verify_token(email, token))
    except Exception as exc:
        raise self.retry(exc= exc, countdown=60)


@celery_app.task(bind=True, max_retries= 3)
def password_reset_code_task(self, email: str, otp: str):
    
    try:
        asyncio.run(e.send_password_reset_code(email, otp))
    except Exception as exc:
        raise self.retry(exc= exc, countdown=60)


@celery_app.task(bind=True, max_retries= 3)
def login_notification_task(self, email: str, name: str):
    
    try:
        asyncio.run(e.send_login_notification(email, name))
    except Exception as exc:
        raise self.retry(exc= exc, countdown=60)


@celery_app.task(bind= True, max_retries= 3)
def aproval_needed_task(self, email: str, username: str, post_title: str):
    try:
        asyncio.run(e.send_post_need_approval(email, username, post_title))
    except Exception as exc:
        raise self.retry(exc= exc, countdown= 60)
    
    
@celery_app.task(bind= True, max_retries= 3)
def notify_author_task(self, author_email: str, post_title: str):
    try:
        asyncio.run(e.send_comment_notification(author_email, post_title))   
    except Exception as exc:
        raise self.retry(exc= exc, countdown= 60)
    