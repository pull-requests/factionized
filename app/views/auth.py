from google.appengine.api import users
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

def login(request):
    user = users.get_current_user()

    if user:
        profile = request.profile
        next = request.GET.get('next', 
                               reverse('profile_show', 
                                       kwargs=dict(profile_id=profile.uid)))
        return redirect(next)

    return redirect(users.create_login_url(next))

def logout(request):
    user = users.get_current_user()
    if user:
        return redirect(users.create_logout_url(reverse('root_index')))
    return redirect(reverse('root_index'))
