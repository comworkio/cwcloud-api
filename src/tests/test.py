from fastapi import FastAPI
from unittest import TestCase

from database.postgres_db import dbEngine
from entities.User import Base

class TestApp(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApp, self).__init__(*args, **kwargs)
        TestApp.get_app()
        Base.metadata.create_all(bind = dbEngine)

    @staticmethod
    def get_app():
        global app
        app = FastAPI(docs_url = "/")
        return app
