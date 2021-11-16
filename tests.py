import unittest
import os
from src import db
from app import app, create_app

class Main(unittest.TestCase):
    def SetUp(self)->None:
        app = create_app(config_class='config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        client = self.app.test_client(use_cookies=True)
        with self.app.app_context():
            db.create_all()

    def TearDown(self)->None:
        with self.app.app_context():
            db.drop_all()
            print('dropping test.sqlite ... ')
            os.unlink('test.sqlite')

if __name__ == '__main__':
    unittest.main()
