from .models import User
import logging

log = logging.getLogger(__name__)


#USERS = {'editor':'editor',
#          'viewer':'viewer'}
#GROUPS = {'editor':['group:editors']}

    
def groupfinder(name, request):
    log.debug("------------ groupfinder called with userid: %s" % name)
    #user = request.user
    if name is not None:
        user = User.get_by_name(name)
        groups = [ group.name for group in user.groups ]
        log.debug("------------ groupfinder returning groups: %s" % groups)
        return groups
    return None
