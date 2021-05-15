from celery import Celery
from dotenv import load_dotenv
import os

def make_celery(app_name=__name__):
    broker_url = os.getenv('BROKER')
    return Celery(
        app_name,
        broker="amqp://yafiabiyyu:yafi2105@localhost/unixuser",
        backend="mongodb://172.17.0.2/celery_task"
    )
celery = make_celery()