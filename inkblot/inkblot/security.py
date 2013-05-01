USERS = {'editor':'editor',
          'viewer':'viewer'}
GROUPS = {'editor':['group:editors']}

def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
    
#def groupfinder(userid, request):
#    user = request.user
#    if user is not None:
#        return [ group.name for group in request.user.groups ]
#    return None
