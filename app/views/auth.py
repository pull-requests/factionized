from google.appengine.api import users
from django.shortcuts import render_to_response

def login(request):
    return render_to_response('auth/login.html')

def logout(request):
    return render_to_response('auth/logout.html')
