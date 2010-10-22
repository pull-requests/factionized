from django.conf import settings
from django.http import HttpResponseRedirect
from google.appengine.api import users

def login_required(func):
    def _wrapper(request, *args, **kw):
        user = users.get_current_user()
        if user:
            return func(request, *args, **kw)
        else:
            url = settings.LOGIN_URL or users.create_login_url(request.get_full_path())
            return HttpResponseRedirect(url)

    return _wrapper
