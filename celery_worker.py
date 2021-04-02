from project import celery
from project.factory import create_app
from project.celery_utils import init_celery

app = create_app()
init_celery(celery, app)