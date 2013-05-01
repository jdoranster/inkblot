import cryptacular.bcrypt

import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Unicode,
    UnicodeText,
    DateTime,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    column_property,
    synonym,
    joinedload,
    )    


from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    authenticated_userid,
    forget,
    remember,
    ALL_PERMISSIONS
    )
   
from zope.sqlalchemy import ZopeTransactionExtension
#from sqlalchemy_traversal import TraversalMixin

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

def hash_password(password):
    return unicode(crypt.encode(password))


# specialized UserTask init
def _create_by_task(task):
    return UserTask(task=task)

def _create_by_group(group):
    return UserGroup(group=group)
   

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    password = Column(Unicode(60), nullable=False)
    lessons = relationship("Lesson", order_by="Lesson.id", backref="user")
    last_logged = Column(DateTime, default=datetime.datetime.utcnow)
    email = Column(Unicode(50))    
    progress = Column(Integer, default=0)
    # association proxy of "user_tasks" collection
    # to "tasks" attribute
    groups = association_proxy('user_groups', 'group', creator=_create_by_group)
    

    tasks = association_proxy('user_tasks', 'task', creator=_create_by_task)
    
    _password = Column('password', Unicode(60))    
    
    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    def __init__(self, name, password, email):
        self.name = name
        self.email = email
        self.password = password
        
            
    @classmethod
    def get_users(self):
        users = DBSession.query(User).all()
        return users
    
    
    @classmethod
    def get_user_by_id(self,user_id):
        user = DBSession.query(User).filter(User.id == user_id).one()
        return user    

    @classmethod
    def get_by_name(cls, name):
        return DBSession.query(cls).filter(cls.name == name).first()

    @classmethod
    def check_password(cls, name, password):
        user = cls.get_by_name(name)
        if not user:
            return False
        return crypt.check(user.password, password)



class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique = True, nullable=False)
 
    @classmethod
    def get_group(self, name):
        group = DBSession.query(Group).filter(Group.name == name).one()
        return group
 
 
class UserGroup(Base):
    __tablename__ = 'user_group'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    
    group = relationship(Group, lazy='joined')
    

class Lesson(Base):
    __tablename__ = 'lesson'
    id = Column(Integer, primary_key=True)
    ltype = Column(Unicode(255), nullable=False)
    title = Column(Unicode(255), unique=True, nullable=False)
    instruction = Column(Unicode(255), default=u'')

    user_id = Column(Integer, ForeignKey('user.id'))
    tasks = relationship("Task", 
                         order_by="Task.step",
                         backref=backref("lesson"),
                         collection_class=ordering_list('step'))
    created = Column(DateTime, default=datetime.datetime.utcnow)
    edited = Column(DateTime, default=datetime.datetime.utcnow)

    
class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    prompt =  Column(Unicode(255), default=u'', index=True, unique=True)
    lesson_id = Column(Integer, ForeignKey('lesson.id'))
    created = Column(DateTime, default=datetime.datetime.utcnow)
    edited = Column(DateTime, default=datetime.datetime.utcnow)
    result = Column(Unicode(255), default=u'')
    step = Column(Integer)
    prev_node_id = Column(Integer, ForeignKey('task.id'))
    prev = relationship(
            'Task',
            uselist=False,
            remote_side=[id],
            backref=backref('next', uselist=False))
               


class UserTask(Base):
    __tablename__ = 'user_task'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'), primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    task = relationship(Task, lazy='joined')
    
    def __init__(self, user=None, task=None):
         
        if user: self.user_id = user.id
        if task: self.task_id = task.id
         
        
              

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        #(Allow, Authenticated, 'view'),
        (Allow, 'group:editor', ('add', 'edit')),
        (Allow, 'group:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        pass # pragma: no cover

