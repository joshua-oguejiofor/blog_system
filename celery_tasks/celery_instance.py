from celery import Celery
from core.config import settings

celery_app= Celery(
    "blog",  # name of celery application
    broker= settings.REDIS_URL, # making redis the message broker
    backend= settings.REDIS_URL, # task result will be stored
    include=["celery_tasks.celery_tasks"] # location for celery tasks
)

#------------- this update celery configuration -----#
celery_app.conf.update(
    task_serializer="json", # convert task to json before senging to redis
    accept_content=["json"], # only accept json messages
    result_serializer="json",# convert task result to json then store
    timezone="UTC", #utc timezone for task scheduling
    enable_utc=True,
)
