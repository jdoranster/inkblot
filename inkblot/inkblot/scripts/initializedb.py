import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from inkblot.models import (
    DBSession,
    User,
    Group,
    Lesson,
    Task,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        admin = User(name='admin', password=u'2admin', email='root@localhost')
        DBSession.add(admin)
        g1 = Group(name='admin')
        DBSession.add(g1)
        g2 = Group(name='viewer')
        DBSession.add(g2)
        g3 = Group(name='editor')
        DBSession.add(g3)
        admin.groups.extend([g1,g2,g3])
        

        
        


