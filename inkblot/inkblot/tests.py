import unittest
import transaction

from pyramid import testing

from .models import (
    DBSession, 
    Base, 
    User, 
    Lesson, 
    Task
    )


def _registerRoutes(config):
    config.add_route('view_page', '{pagename}')
    
def _initTestDB():
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        user = User(name='tester', password=u'2easy')
        lesson1 = Lesson( title = "Test Lesson",instruction = "Test this!", ltype = "testy")
        task1 = Task(word = "X", sound = "loud.mp4")
        lesson1.tasks.append(task1)
        user.lessons.append(lesson1)
        DBSession.add(user)
        
    return DBSession


class TestMyModels(unittest.TestCase):
    def setUp(self):
        self.session = _initTestDB()

    def tearDown(self):
        self.session.remove()
        
        
    def _make_user(self, name, password):

        user = User(name = name, password = password)
        self.session.add(user)
        return user
        
    def _make_lesson(self, title, instruction, ltype):

        lesson = Lesson( title = title, instruction = instruction, ltype = ltype)
        self.session.add(lesson) 
        return lesson
    
    def _make_task(self, word, sound):

        task = Task(word = word, sound = sound)
        self.session.add(task)
        return task
        

    def test_user(self):
        
        u2 = self.session.query(User).filter(User.name == 'tester').first()
        self.assertEqual(u2.name, 'tester')
        self.assertEqual(u2.password, u'2easy') 
        
    def test_lesson(self):
        
        l2 = self.session.query(Lesson).filter(Lesson.title =='Test Lesson').first()
        self.assertEqual(l2.instruction, 'Test this!')
        self.assertEqual(l2.title, 'Test Lesson')
        self.assertEqual(l2.ltype, 'testy')
        

    def test_task(self):
        
        t2 = self.session.query(Task).filter(Task.word == 'X').first()
        self.assertEqual(t2.word, 'X')
        self.assertEqual(t2.sound, 'loud.mp4')
        
    def test_all(self):
        user = self.session.query(User).filter(User.name == 'tester').first()
        self.assertEqual(len(user.lessons), 1)
        lesson = user.lessons.pop()
        self.assertEqual(lesson.title, 'Test Lesson')
        self.assertEqual(len(lesson.tasks), 1)
        task = lesson.tasks.pop()
        self.assertEqual(task.word, 'X')
        
        

