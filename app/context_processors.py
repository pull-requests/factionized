from django.core.urlresolvers import reverse
from google.appengine.api import users

def google_user(request):
    """ Returns the user if it exists to the context for template rendering
    """
    if request and hasattr(request, 'user') and request.user:
        return {
            'user': request.user,
            'logout_url': users.create_logout_url(reverse('auth_logout'))
        }
