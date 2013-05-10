import unittest
from pyramid import testing
import json

from test_models import initTestDB

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = initTestDB()
        

    def tearDown(self):
        testing.tearDown()
        self.session.remove()

    def test_user_signup_service(self):
        from inkblot.views import sign_in
        request = testing.DummyRequest()
        request.body = json.dumps({"name": "tester", 
                             "password": "2easy",
                             "remember": True})
        info = sign_in(request)
        self.assertEqual(info['status'], 'OK')