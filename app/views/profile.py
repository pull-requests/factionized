import re

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from app.decorators import login_required
from app.models import Profile
from app.shortcuts import render

from lib.bigdoorkit.resources import EndUser

@login_required
def index(request, profile_id):
    return render('profile/index.html')


@login_required
def show(request, profile_id):

    profile = Profile.filter('uid =', user_id).get()
    bd_end_user = EndUser(end_user_login=profile.uid)

    return render('profile/show.html', {'bd_end_user':bd_end_user})

@login_required
def edit(request):
    raise NotImplementedError, 'have not done it yet, so there'

@login_required
def new(request):
    user = request.user

    existing_profile = Profile.filter('user =', user).get()
    if existing_profile:
        redirect(reverse('profile_edit', profile=existing_profile.uid))

    return render('profile/new.html', {'user': user})


valid_name_regex = re.compile('^[^a-zA-Z0-9 ]$')
def validate_name(name):
    return valid_name_regex.match(name)

@login_required
def create(request):
    user = request.user

    existing_profile = Profile.filter('user =', user).get()
    if existing_profile:
        return HttpResponse(status=400)

    name = request.GET.get('name', None)

    if not name:
        raise Exception, 'do something smart here'

    raise NotImplementedError, 'may not be used'

