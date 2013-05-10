from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import unauthenticated_userid
from inkblot.security import groupfinder

from .models import (
    DBSession,
    Base,
    User,
    )

#from sqlalchemy_traversal   import ISABase
#from sqlalchemy_traversal   import ISASession

#from .views import LessonView
import sqlalchemy as sa
from datetime import datetime
import inflect

# hack to allow JSON serialization of sqlalchemy objects.
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

def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        return User.get_user_by_id(userid)
        

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.todict = todict
    Base.__iter__ = iterfunc
    authn_policy = AuthTktAuthenticationPolicy(
        'mysecret', callback=groupfinder, 
        cookie_name = 'X-Messaging-Token',hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, root_factory='inkblot.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', path='inkblot:static', cache_max_age=3600)
    config.add_request_method(get_user, 'user', reify=True)
    #config.registry.registerUtility(DBSession, ISASession)
    #config.registry.registerUtility(Base, ISABase)
    config.include('cornice')
    config.add_route('whoami','/whoami')
    config.add_route('signin', '/user/sign_in')
    config.add_route('signout', '/user/sign_out')
    
    config.add_route('home', '/')
    config.add_route('test_lessons', '/test/lessons')
    config.add_route('test_lesson', '/test/lessons/{id}')
    config.add_route('test_tasks', '/test/tasks')
    
    #config.add_view(LessonView, attr='get', request_method='GET')
    #config.add_view(LessonView, attr='post', request_method='POST')
    #config.add_view(LessonView, attr='delete', request_method='DELETE')

    
    config.scan()
    return config.make_wsgi_app()
