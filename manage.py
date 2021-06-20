from project import factory
import project

app = factory.create_app(celery=project.celery)
