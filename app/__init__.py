import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv('.env')


def make_celery(app_name=__name__):
    backend = os.getenv('CELERY_BACKEND')
    broker = os.getenv('CELERY_BROKER_URL')
    print(backend, broker)
    return Celery(app_name, backend = backend, broker = broker)

celery = make_celery()