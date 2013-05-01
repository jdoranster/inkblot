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
        admin = DBSession.query(User).filter(User.name == "admin").one()
        lesson1 = Lesson( title = "First Lesson",instruction = "Select a phoneme and listen to the sound", ltype = "phoneme")
        task1 = Task(prompt = "M", result = "m-recording.m4a")
        task2 = Task(prompt = "E", result = "e-recording.m4a")
        lesson1.tasks.extend([task1, task2])
        admin.lessons.append(lesson1)
        DBSession.add(lesson1)
        DBSession.flush()
        lesson2 = Lesson( title = "Second Lesson", instruction = "Select the combination of phonemes to make a word", ltype = "phoneme-word")
        task3 = Task(prompt = "B", result = "b-recording.m4a")
        task4 = Task(prompt = "F", result = "f-recording.m4a")
        lesson2.tasks.extend([task3, task4])
        admin.lessons.append(lesson2)
        DBSession.add(lesson2)
        DBSession.flush()
        lesson3 = Lesson( title = "Third Lesson", instruction = "Find something new to say", ltype = "drop-target")
        admin.lessons.append(lesson3)
        DBSession.add(lesson3)
        task5 = Task(prompt = "G", result = "b-recording.m4a")
        task6 = Task(prompt = "I", result = "f-recording.m4a")
        lesson1.tasks.extend([task5, task6])
        DBSession.add(lesson1)

        

        
        


