from django.core.urlresolvers import reverse
from django.conf import settings
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
    if request and hasattr(request, 'profile') and request.profile:
        context['profile'] = request.profile

    # Add the Facebook API key to the context for easy retrieval
    context['fb_app_id'] = settings.FACEBOOK_APP_ID
    context['fb_key'] = settings.FACEBOOK_API_KEY
    context['fb_secret'] = settings.FACEBOOK_SECRET_KEY
    return context
