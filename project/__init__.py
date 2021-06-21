from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

def make_celery(app_name=__name__):
    broker_url = os.getenv("BROKER")
    return Celery(
        app_name,
        broker=os.getenv("BROKER"),
        backend=os.getenv("MONGO_DB_URI"),
    )


celery = make_celery()
