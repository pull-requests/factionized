from google.appengine.api import users
from app import context
from app.models import Profile

class GoogleUserMiddleware(object):

    def process_request(self, request):
        user = users.get_current_user()
        if user:
            request.user = user
            try:
                request.profile = Profile.all().filter('user =', user)[0]
            except IndexError, e:
                p = Profile()
                p.user = user
                p.put()
                request.profile = p

class ContextMiddleware(object):
    """ Adds the request to the current thread context for access accross
    accross the project
    """
    def process_request(self, request):
        context.request = request
