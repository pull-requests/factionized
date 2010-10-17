from django.core.urlresolvers import reverse
from google.appengine.api import users

def google_user(request):
    """ Returns the user if it exists to the context for template rendering
    """
    context = {
        'logout_url': users.create_logout_url(reverse('auth_logout')),
        'login_url': users.create_login_url(reverse('auth_login'))
    }
    if request and hasattr(request, 'user') and request.user:
        context['user'] = request.user
    return context
