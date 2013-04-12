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

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    column_property,
    )


from zope.sqlalchemy import ZopeTransactionExtension
#from sqlalchemy_traversal import TraversalMixin

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    password = Column(Unicode(60), nullable=False)
    lessons = relationship("Lesson", order_by="Lesson.id", backref="user")
    last_logged = Column(DateTime, default=datetime.datetime.utcnow)

class Lesson(Base):
    __tablename__ = 'lesson'
    id = Column(Integer, primary_key=True)
    ltype = Column(Unicode(255), nullable=False)
    title = Column(Unicode(255), unique=True, nullable=False)
    instruction = Column(Unicode(255), default=u'')
    user_id = Column(Integer, ForeignKey('user.id'))
    tasks = relationship("Task", order_by="Task.id", backref="lesson")
    created = Column(DateTime, default=datetime.datetime.utcnow)
    edited = Column(DateTime, default=datetime.datetime.utcnow)
    
class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    page =  Column(Unicode(255), default=u'')
    lesson_id = Column(Integer, ForeignKey('lesson.id'))
    created = Column(DateTime, default=datetime.datetime.utcnow)
    edited = Column(DateTime, default=datetime.datetime.utcnow)
    
    