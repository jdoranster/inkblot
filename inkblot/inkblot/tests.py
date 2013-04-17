import unittest
import transaction

from pyramid import testing

from .models import DBSession


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            user = User(name='tester', password=u'test')
            DBSession.add(user)
            lesson1 = Lesson( title = "Test Lesson",instruction = "Select a phoneme and listen to the sound", ltype = "phoneme")
            task1 = Task(word = "M", sound = "m-recording.m4a")
            task2 = Task(word = "E", sound = "e-recording.m4a")
            lesson1.tasks.extend([task1,task2])
            user.lessons.append(lesson1)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import test_lessons
        request = testing.DummyRequest()
        info = test_lessons(request)
        print ("info %r" % info)
        self.assertNEqual(info['lessons'])
        self.assertEqual(info['lessons'].name, 'one')
        self.assertEqual(info['project'], 'inkblot')
