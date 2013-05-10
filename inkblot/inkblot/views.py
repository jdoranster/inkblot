from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from json import loads

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager

import logging
log = logging.getLogger(__name__)

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,   
    effective_principals,
    )

from .models import (
    DBSession,
    User,
    Lesson,
    Task,
    )

import pdb

from webob import Response, exc
from cornice import Service


users = Service(name='users', path='/users', description="Users")
messages = Service(name='messages', path='/', description="Messages")




#
# Helpers
#
def _create_token():
    return binascii.b2a_hex(os.urandom(20))


class _401(exc.HTTPError):
    def __init__(self, msg='Unauthorized'):
        body = {'status': 401, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 401
        self.content_type = 'application/json'


def valid_token(request):
    header = 'X-Messaging-Token'
    token = request.headers.get(header)
    if token is None:
        raise _401()

    token = token.split('-')
    if len(token) != 2:
        raise _401()

    user, token = token

    valid = user in _USERS and _USERS[user] == token
    if not valid:
        raise _401()

    request.validated['user'] = user


def unique(request):
    name = request.body
    if User.get_by_name(name):
        request.errors.add('url', 'name', 'This user exists!')
    
        user = {'name': name, 'token': _create_token()}
        request.validated['user'] = user

#
# Services
#

#
# User Management
#


@users.get(validators=valid_token)
def get_users(request):
    """Returns a list of all users."""
    return {'users': _USERS.keys()}


@users.post(validators=unique)
def create_user(request):
    """Adds a new user."""
    user = request.validated['user']
    _USERS[user['name']] = user['token']
    return {'token': '%s-%s' % (user['name'], user['token'])}


@users.delete(validators=valid_token)
def del_user(request):
    """Removes the user."""
    name = request.validated['user']
    del _USERS[name]
    return {'Goodbye': name}


mandatory=set(['name','password'])
@view_config(route_name='signin', renderer='json')
def sign_in(request):
    parms = loads(request.body, request.charset)
    message=''
    if mandatory <= set(parms):
        password = parms['password']
        name = parms['name']
        remember_me = False
        if 'remember' in parms:
            remember_me = parms['remember']
        if User.check_password(name, password):
            user = User.get_by_name(name)
            headers = remember(request, name)
            # headers of the form ...
            # [('Set-Cookie', 'X-Messaging-Token="fc5b3c1c09bbacfb8942877ec299c33650c572536b7fbb2d8aaea0bf09a4f8490df76334305e3b8a2e09ab8b513cd2e8a074f1b4e3b7521c4d167910656b485a518be2d9YWRtaW4%3D!userid_type:b64unicode"; Path=/'),]
            cookies = [x[1] for x in headers if x[1].startswith('X-Messaging-Token')]
            #
            auth = cookies[0].split('"')[1]
            request._response_headerlist_set(headers)            
            return  {'status':'OK', 'userid': user.id, 'authToken': auth}
        else:
            return {'status': 'ERROR'} 
    

@view_config(route_name='signout', renderer='json')
def sign_out(request):
    headers = forget(request)
    request._response_headerlist_set(headers)
    return {'status':'OK'}


@view_config(route_name='home', renderer='templates/mytemplate.pt',
             permission='view')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'inkblot'}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_inkblot_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


@view_config(route_name='test_lessons', renderer='json', permission='view')
def test_lessons(request):
    from pyramid.security import authenticated_userid
    logged_in = authenticated_userid(request)
    log.debug('logged_in = %s' % logged_in)
    if request.method == 'GET':
        try:
            lessons = DBSession.query(Lesson).\
                                outerjoin(Lesson.tasks).\
                                options(contains_eager(Lesson.tasks)).all()
            log.debug("lessons: %s" % [ dict(u) for u in lessons])
            return ({'lessons':[ dict(u) for u in lessons]})
        except DBAPIError as e:
            return Response("Unable to access DB: %s" % e, content_type='text/plain', status_int=500)            
    else:
        log.error("Not yet supporting method %s for lessons" % request.method)
        return []


@view_config(route_name='test_lesson', renderer='json', request_method=['GET','PUT', 'DELETE'], permission='view')
def test_lesson(request):
    if request.method == 'GET':
        if 'id' in request.matchdict:
            l_id = request.matchdict['id']
            log.debug("---------------- lesson id = %s,%s" % (l_id, l_id.__class__))
            try:
                lesson = DBSession.query(Lesson).\
                                   outerjoin(Lesson.tasks).\
                                   filter(Lesson.id == l_id).first()
                return ({'lesson':dict(lesson)})
            except DBAPIError as e:
                return Response("Unable to access DB: %s" % e, content_type='text/plain', status_int=500)            
    else:
        log.error("Not yet supporting method %s for lesson" % request.method)
        return []


@view_config(route_name='test_tasks', renderer='json', request_method=['GET','PUT', 'DELETE'], permission='view')
def test_tasks(request):
    if request.method == 'GET':
        log.debug("^^^^^^^ request.params: %r" % request.params)
        log.debug("^^^^^^^ request.params[ids[]]: %r" % request.params.getall('ids[]'))
        if 'ids[]' in request.params:
            ids = request.params.getall('ids[]')
            log.debug("---------------- task ids = %s,%s" % (ids, ids.__class__))
            try:
                tasks = DBSession.query(Task).filter(Task.id.in_( ids)).all()
                log.debug("------ Found tasks:  %s" % tasks)
                return ({'tasks':[dict(u) for u in tasks]})
            except DBAPIError as e:
                return Response("Unable to access DB: %s" % e, content_type='text/plain', status_int=500)
            
        log.error("No task ids supplied")
        return [{"tasks":[]}]
                        
    else:
        log.error("Not yet supporting method %s for tasks" % request.method)
        return []

@view_config(route_name='whoami', permission='authenticated', renderer='json')
def whoami(request):
    """ Return autenticated user's credentials """
    username = authenticated_userid(request)
    principals = effective_principals(request)
    return {'username':username, 'principals': principals}