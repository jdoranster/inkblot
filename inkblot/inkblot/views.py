from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
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
dummys = {"lessons":[
            {
                "id" : 1,
                "title": "First Lesson",
                "instruction": "Select a phoneme and listen to the sound",
            },
            {
                "id" : 2,
                "title": "Second Lesson",
                "instruction": "Select the combination of phonemes to make a word",
            },
            {
                "id" : 3,
                "title": "Third Lesson",
                "instruction": "Find something new to say",
            },  
        ]
    }

@view_config(route_name='test_act', renderer='json')
@view_config(route_name='test_it', renderer='json')
def my_view(request):
    
    resource = request.matchdict['resource']
    if 'id' in request.matchdict:
        for dum in dummys:
            if dum['id'] == request.matchdict['id']:
                return (dum)
    return (dummys)
