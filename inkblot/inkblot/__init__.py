from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

#from sqlalchemy_traversal   import ISABase
#from sqlalchemy_traversal   import ISASession

#from .views import LessonView

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    #config.registry.registerUtility(DBSession, ISASession)
    #config.registry.registerUtility(Base, ISABase)
    config.add_route('home', '/')
    config.add_route('test_lessons', '/test/lessons')
    config.add_route('test_lesson', '/test/lessons/{id}')
    config.add_route('test_tasks', '/test/tasks')
    
    #config.add_view(LessonView, attr='get', request_method='GET')
    #config.add_view(LessonView, attr='post', request_method='POST')
    #config.add_view(LessonView, attr='delete', request_method='DELETE')

    
    config.scan()
    return config.make_wsgi_app()
