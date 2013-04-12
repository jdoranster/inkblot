from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError
import logging
log = logging.getLogger(__name__)


from .models import (
    DBSession,
    User,
    Lesson,
    Task,
    )


@view_config(route_name='home', renderer='templates/mytemplate.pt')
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

@view_config(route_name='test_lessons', renderer='json')
def test_lessons(request):
    
    return (dummy_lessons)



@view_config(route_name='test_lesson', renderer='json', request_method=['GET','PUT', 'DELETE'])
def test_lesson(request):
    if request.method == 'GET':
        if 'id' in request.matchdict:
            id = request.matchdict['id']
            log.debug("---------------- lesson id = %s,%s" % (id, id.__class__))
            lessons=dummy_lessons['lessons']
            for lesson in lessons:
                log.debug("lesson['id'] = %s,%s" % (lesson['id'], lesson['id'].__class__))
                if id == lesson['id']:
                    return lesson
            
        return []
    else:
        log.error("Not yet supporting method %s for lesson" % request.method)
        return []


@view_config(route_name='test_tasks', renderer='json', request_method=['GET','PUT', 'DELETE'])
def test_tasks(request):
    if request.method == 'GET':
        log.debug("^^^^^^^ request.params: %r" % request.params)
        log.debug("^^^^^^^ request.params[ids[]]: %r" % request.params.getall('ids[]'))
        if 'ids[]' in request.params:
            ids = request.params.getall('ids[]')
            log.debug("---------------- task ids = %s,%s" % (ids, ids.__class__))
            tasks=dummy_tasks['tasks']
            result={'tasks':[]}
            for task in tasks:
                log.debug("task['id'] = %s,%s" % (task['id'], task['id'].__class__))
                if str(task['id']) in ids:
                    result['tasks'].append(task)
            
        return result
    else:
        log.error("Not yet supporting method %s for tasks" % request.method)
        return []

