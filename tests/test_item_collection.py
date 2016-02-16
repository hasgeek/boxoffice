import unittest
from boxoffice import app, init_for
from boxoffice.models import (db)
from fixtures import init_data


class TestItemCollectionAPI(unittest.TestCase):

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_for('test')
        db.create_all()
        init_data()
        self.client = app.test_client()

    def test_item_collection(self):
        resp = self.client.get('/rootconf/2016')
        self.assertEquals(resp.status_code) == 200

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
