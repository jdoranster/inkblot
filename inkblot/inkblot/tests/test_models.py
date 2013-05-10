import unittest
import transaction

from pyramid import testing

from inkblot.models import (
    DBSession, 
    Base, 
    User, 
    Group,
    Lesson, 
    Task
    )


def _registerRoutes(config):
    config.add_route('view_page', '{pagename}')


def initTestDB():
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        user = User(name=u'tester', password=u'2easy', email=u'test@foo.com')
        DBSession.add(user)
        DBSession.flush()
        lesson1 = Lesson( title = u"Test Lesson",instruction = u"Test this!", ltype = u"testy")
        DBSession.add(lesson1)
        task1 = Task(prompt = "X", result = "loud.mp4" )
        
        DBSession.add(task1)
        DBSession.flush()
        
    return DBSession


def _make_user(session, name, password, email):

    user = User(name = name, password = password, email = email)
    session.add(user)
    session.flush()
    return user

    
def _make_lesson(session, title, instruction, ltype):

    lesson = Lesson( title = title, instruction = instruction, ltype = ltype)
    session.add(lesson) 
    session.flush()
    return lesson


def _make_task(session, prompt, result, next_step=None, step=0):

    task = Task(prompt=prompt, result=result)
    session.add(task)
    session.flush()
    return task


class TestUserModels(unittest.TestCase):
    def setUp(self):
        self.session = initTestDB()

    def tearDown(self):
        self.session.remove()

    def test_user(self):
        
        u2 = self.session.query(User).filter(User.name == u'tester').first()
        self.assertEqual(u2.name, u'tester')
        self.assertEqual(u2.email, u'test@foo.com')
        self.assertEqual(u2.progress, 0)
        
    def test_doesnt_exist(self):
        from sqlalchemy.orm.exc import NoResultFound
        query = self.session.query(User).filter(User.name == u'nobdy')
        self.assertRaises(NoResultFound, query.one)

    def test_already_exist(self):
        from sqlalchemy.exc import IntegrityError
        self.assertRaises(IntegrityError, 
                          _make_user,self.session, u'tester', u'2easy', u'test@foo.com')

    def test_password_hashing(self):
        import cryptacular.bcrypt
        crypt = cryptacular.bcrypt.BCRYPTPasswordManager()
        u2 = self.session.query(User).filter(User.name == u'tester').first()
        self.assertTrue(crypt.check(u2.password, u'2easy'))

    def test_password_checking(self):
        user = self.session.query(User).filter(User.name == u'tester').first()
        self.assertTrue(User.check_password(u'tester', u'2easy'))
        self.assertFalse(User.check_password(u'tester', u'wrong'))
        self.assertFalse(User.check_password(u'nobody', u'2easy'))
        
        
class TestLessonModels(unittest.TestCase):
    
    def setUp(self):
        self.session = initTestDB()

    def tearDown(self):
        self.session.remove()
        
        
    def test_lesson(self):
        
        l2 = self.session.query(Lesson).filter(Lesson.title == u'Test Lesson').first()
        self.assertEqual(l2.instruction, u'Test this!')
        self.assertEqual(l2.title, u'Test Lesson')
        self.assertEqual(l2.ltype, u'testy')
        self.assertEqual(l2.tasks, [])
        

    def test_doesnt_exist(self):
        from sqlalchemy.orm.exc import NoResultFound
        query = self.session.query(Lesson).filter(Lesson.title == u'Test Nothing')
        self.assertRaises(NoResultFound, query.one)

    def test_aleady_exists(self):
        from sqlalchemy.exc import IntegrityError
        self.assertRaises(IntegrityError, 
                          _make_lesson,self.session, u"Test Lesson",u"Test this!",u"testy")
        
class TestTaskModels(unittest.TestCase):
    def setUp(self):
        self.session = initTestDB()

    def tearDown(self):
        self.session.remove()
                 
    def test_task(self):
        t2 = self.session.query(Task).filter(Task.prompt == 'X').first()
        self.assertEqual(t2.prompt, 'X')
        self.assertEqual(t2.result, 'loud.mp4')
        self.assertIsNone(t2.step )
        self.assertIsNone(t2.next)
        self.assertIsNone(t2.prev)
        
        
    def test_doesnt_exist(self):
        from sqlalchemy.orm.exc import NoResultFound
        query = self.session.query(Task).filter(Task.prompt == u'GGGG')
        self.assertRaises(NoResultFound, query.one)

    def test_aleady_exists(self):
        from sqlalchemy.exc import IntegrityError
        self.assertRaises(IntegrityError, 
                          _make_task, self.session, "X","loud.mp4")
                
 
     
class TestAllModels(unittest.TestCase):
    def setUp(self):
        self.session = initTestDB()

    def tearDown(self):
        self.session.remove()    
        
    def test_add_user_groups(self):
        user = self.session.query(User).filter(User.name == 'tester').first()
        self.assertEqual( len(user.lessons), 0)
        ged = self.session.query(Group).filter(Group.name == 'editor').first()
        user.groups.append(ged)
        self.assertEqual(len(user.groups), 1)
        
        
    def test_add_lessons(self):
        user = self.session.query(User).filter(User.name == 'tester').first()
        self.assertEqual( len(user.lessons), 0)
        l1 = self.session.query(Lesson).filter(Lesson.title == u'Test Lesson').first()
        user.lessons.append(l1)
        l2 = _make_lesson(self.session, u"Test Lesson 2", u"More instructions", "test_type2")
        user.lessons.append(l2)
        self.session.flush()
        self.assertEqual(len(user.lessons), 2)
        user.lessons.remove(l1)
        self.assertEqual(len(user.lessons), 1)        
    
    def test_add_tasks(self):   
        l1 = self.session.query(Lesson).filter(Lesson.id == 1).first()
        self.assertEqual( len(l1.tasks), 0)
        t1 = self.session.query(Task).filter(Task.prompt == 'X').first()
        l1.tasks.append(t1)
        self.session.flush()
        self.assertEqual(l1.tasks[0].step, 0)
        t2 = _make_task(self.session, 'Z', 'sleep.mp4')
        l1.tasks.append(t2)
        self.session.flush()        
        self.assertEqual(len(l1.tasks), 2)
        self.assertEqual(t2.step, 1)
        l1.tasks.remove(t1)
        self.assertEqual(len(l1.tasks), 1)
        user = self.session.query(User).filter(User.name == 'tester').first()
        self.assertEqual(len(user.tasks), 0)
        user.tasks.append(t2)
        self.assertEqual(len(user.tasks), 1)

    def test_pair_tasks(self):
        l1 = self.session.query(Lesson).filter(Lesson.id == 1).first()
        t1 = self.session.query(Task).filter(Task.prompt == 'X').first()
        t2 = _make_task(self.session, 'Z', 'sleep.mp4')
        t3 = _make_task(self.session, 'Y', 'silence.mp4')
        t1.next = t2
        l1.tasks.extend([t1,t2,t3])
        self.assertIsNotNone(t1.next)
        self.assertEqual(t2.prev, t1)
        

        
 