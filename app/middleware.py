from google.appengine.api import users
from app import context

class GoogleUserMiddleware(object):

    def process_request(self, request):
        user = users.get_current_user()
        if user:
            request.user = user

class ContextMiddleware(object):
    """ Adds the request to the current thread context for access accross
    accross the project
    """
    def process_request(self, request):
        context.request = request
