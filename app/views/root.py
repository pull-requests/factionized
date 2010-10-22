from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from app.shortcuts import render

def index(request):
    if hasattr(request, 'user') and request.user:
        return render('root/index_profile.html', {'profile':request.profile})
    return render('root/index_anonymous.html')
