from pyramid.response import Response
from pyramid.view import view_config, view_defaults

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
    )

from .security import USERS

from .models import (
    DBSession,
    User,
    Lesson,
    Task,
    )

import pdb

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)


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
dummy_lessons = {"lessons":[
            {
                "id" : 1,
                "title": "First Lesson",
                "instruction": "Select a phoneme and listen to the sound",
                "ltype" : "phoneme",
                "task_ids" : [ 4,5 ],
           },
            {
                "id" : 2,
                "title": "Second Lesson",
                "instruction": "Select the combination of phonemes to make a word",
                "ltype" : "phoneme",
                "task_ids":[ 6, 7]

            },
            {
                "id" : 3,
                "title": "Third Lesson",
                "instruction": "Find something new to say",
                "ltype" : "drop-target",
                "task_ids": [],
                
            },  
        ]
    }

dummy_tasks = {
    "tasks" : [
            {
                "id": 4,
                "word":"M",
                "sound" : "m-recording.m4a",
                "lesson_id" : 1,
            },
            {
                "id": 5,
                "word":"E",
                "sound" : "e-recording.m4a",
                "lesson_id" : 1,
            },
            {
                "id": 6,
                "word": "B",
                "sound": "b-recording.m4a",
                "lesson_id" : 2,
            },
            {
                "id": 7,
                "word":"F",
                "sound": "f-recording.m4a",
                "lesson_id" : 2,
            },            
        ]
        
    
}

@view_config(route_name='test_lessons', renderer='json', permission='view')
def test_lessons(request):
    from pyramid.security import authenticated_userid
    logged_in = authenticated_userid(request)
    
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

