from google.appengine.api import users
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from app.shortcuts import render

def login(request):
    user = users.get_current_user()
    next = request.GET.get('next', reverse('user_index'))
    if user:
        return redirect(next)
    return render('auth/login.html', {
        'login_url': users.create_login_url(next)
    })

def logout(request):
    user = users.get_current_user()
    if user:
        return redirect(users.create_logout_url(reverse('user_index')))
    return redirect(reverse('user_index'))