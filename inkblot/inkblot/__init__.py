from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from inkblot.security import groupfinder

from .models import (
    DBSession,
    Base,
    )

#from sqlalchemy_traversal   import ISABase
#from sqlalchemy_traversal   import ISASession

#from .views import LessonView
import sqlalchemy as sa
from datetime import datetime
import inflect
def todict(self):
    def convert_datetime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S")
 
    d = {}
    for k,v in self.__dict__.iteritems():
        if k.startswith('_'):
            continue
        elif hasattr(v, '__iter__'):
            p = inflect.engine()
            col=[]
            for i in v:
                col.append(i.id)
            v = col
            k = "%s_ids" % p.singular_noun(k)
        elif type(v) == datetime:
            v = convert_datetime(v)
            
        yield (k, v)
    #for c in self.__table__.columns:
    #    if isinstance(c.type, sa.DateTime):
    #        value = convert_datetime(getattr(self, c.name))
    #    else:
    #        value = getattr(self, c.name)
 
        #yield(c.name, value)
 
def iterfunc(self):
    """Returns an iterable that supports .next()
        so we can do dict(sa_instance)
 
    """
    return self.todict()
 

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.todict = todict
    Base.__iter__ = iterfunc
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, root_factory='inkblot.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    #config.registry.registerUtility(DBSession, ISASession)
    #config.registry.registerUtility(Base, ISABase)
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('home', '/')
    config.add_route('test_lessons', '/test/lessons')
    config.add_route('test_lesson', '/test/lessons/{id}')
    config.add_route('test_tasks', '/test/tasks')
    
    #config.add_view(LessonView, attr='get', request_method='GET')
    #config.add_view(LessonView, attr='post', request_method='POST')
    #config.add_view(LessonView, attr='delete', request_method='DELETE')

    
    config.scan()
    return config.make_wsgi_app()
