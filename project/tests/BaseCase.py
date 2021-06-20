import celery
import project
from project import factory
from project.factory import db
import unittest


class BaseCase(unittest.TestCase):
    def setUp(self):
        app = factory.create_app(celery=project.celery)
        self.app = app.test_client()
        self.db = db.get_db()
        self.base_url = "http://127.0.0.1:5000/vote2block/api/v1"
