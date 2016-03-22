# -*- coding: utf-8 -*-

import unittest
from boxoffice import app, db, init_for
from .fixtures import Fixtures


class TestDatabaseFixture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        setUp that runs once before every Test Class.
        Creates DB schema and adds fixtures.
        """
        init_for('testing')
        db.create_all()
        f = Fixtures()
        f.make_fixtures()

    @classmethod
    def tearDownClass(cls):
        """
        tearDown that runs once after every Test Class
        Remove test session and tables.
        """
        db.session.rollback()
        db.drop_all()
