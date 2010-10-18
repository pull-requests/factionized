import re

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings

from app.decorators import login_required
from app.models import Profile
from app.shortcuts import render

from app.lib import facebook

#from bigdoorkit.resources.user import EndUser

@login_required
def index(request, profile_id):
    return render('profile/index.html')


@login_required
def show(request, profile_id):
    profile = Profile.all().filter('uid =', profile_id).get()
    #bd_end_user = EndUser(end_user_login=profile.uid)

    if profile.uid == request.profile.uid:
        is_editable = True
        return render('profile/show.html', {'bd_end_user':None, 'is_editable':is_editable})

    return render('profile/show.html', {'bd_end_user':None})

@login_required
def edit(request,code=None):
    profile = request.profile
    fb_cookie = facebook.get_user_from_cookie(request.COOKIES,
                                              settings.FACEBOOK_APP_ID,
                                              settings.FACEBOOK_SECRET_KEY)
    user = None
    if not profile.fb_token and fb_cookie:
        try:
            # Grab the users profile from facebook to get their UID
            graph = facebook.GraphAPI(fb_cookie["access_token"])
            user = graph.get_object("me")
        except facebook.GraphAPIError, e:
            profile.fb_token = ''
            profile.fb_uid = ''
            profile.fb_auth = False
            profile.put()

        if user is not None:
            # Add the information to the profile object
            profile.fb_token = fb_cookie["access_token"]
            profile.fb_uid = str(user["id"])
            profile.fb_auth = True
            profile.put()

    #bd_end_user = EndUser(end_user_login=profile.uid)

    return render('profile/edit.html', {'bd_end_user':None})

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

