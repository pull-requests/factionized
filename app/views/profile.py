import re
import cgi
import urllib

from hashlib import sha1
from hmac import new as hmac
from random import getrandbits
from time import time

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from google.appengine.api import urlfetch

from app.decorators import login_required
from app.models import Profile
from app.shortcuts import render

from app.lib import facebook
#from app.lib import oauth2 as oauth
from app.lib.fb import FacebookUser
#from app.lib.tw import TwitterUser

#from bigdoorkit.resources.user import EndUser

from bigdoorkit import Client

@login_required
def index(request, profile_id=None):
    return render('profile/index.html')


@login_required
def show(request, profile_id):
    profile = Profile.all().filter('uid =', profile_id).get()
    #bd_end_user = EndUser(end_user_login=profile.uid)

    eul = "profile:%s" % profile.uid
    c = Client(settings.BDM_SECRET, settings.BDM_KEY)
    try:
        bd_end_user = c.get('end_user/%s' % eul)[0]
    except ValueError, e:
        payload = dict(end_user_login=eul)
        bd_end_user = c.post('end_user', payload=payload)[0]

    if profile.uid == request.profile.uid:
        is_editable = True
        return render('profile/show.html', {'bd_end_user':bd_end_user, 'is_editable':is_editable})

    return render('profile/show.html', {'bd_end_user':bd_end_user})

@login_required
def edit(request):
    profile = request.profile

    # The user might have deauthorized us, try and grab their
    # profile with the access token we've stored
    try:
        # Grab the users profile from facebook to get their UID
        graph = facebook.GraphAPI(profile.fb_token)
        user = graph.get_object("me")
    except facebook.GraphAPIError, e:
        profile.fb_token = ''
        profile.fb_uid = ''
        profile.fb_auth = False
        profile.put()

    #bd_end_user = EndUser(end_user_login=profile.uid)
    bd_end_user = return_fake_end_user(profile)
    return render('profile/edit.html', {'bd_end_user':bd_end_user})

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

@login_required
def service_feed(request, service_name):
    profile = request.profile

    if request.method == 'POST':
        message = request.POST.get('message',None)
        image_url = request.POST.get('image_url',None)
        caption = request.POST.get('caption',None)

        if not message and not image:
            return HttpResponse(status=400)

        if service_name == 'facebook':

            fb_user = FacebookUser(profile)
            fb_user.post_to_feed(message,image_url,caption)
            params = {'message':message,'image':image_url,'caption':caption}
            return render('profile/post.html', {'params':params})

        elif service_name == 'twitter':
            tw_user = TwitterUser(profile)
            tw_user.post_to_feed(message,image_url,caption)
            params = {'message':message,'image':image_url,'caption':caption}
            return render('profile/post.html', {'params':params})

    raise NotImplementedError, 'may not be used'

def facebook_auth(request):
    verification_code = request.GET.get('code')
    redirect_uri = request.build_absolute_uri()
    redirect_uri = redirect_uri.split("?")[0]
    args = dict(client_id=settings.FACEBOOK_API_KEY,
                redirect_uri=redirect_uri)
    if verification_code:
        args['client_secret'] = settings.FACEBOOK_SECRET_KEY
        args['code'] = verification_code
        access_token_url = "https://graph.facebook.com/oauth/access_token?"
        resp = urlfetch.fetch(access_token_url +
                              urllib.urlencode(args))
        resp = cgi.parse_qs(resp.content)

        profile = request.profile
        profile.fb_token = resp["access_token"][-1]

        graph = facebook.GraphAPI(profile.fb_token)
        user = graph.get_object("me")
        profile.fb_uid = user['id']
        profile.fb_auth = True

        profile.put()

        auth_response = HttpResponse()
        auth_response.content = return_self_closing_page()

        return auth_response
    else:
        auth_url = "https://graph.facebook.com/oauth/authorize?%s"
        args['scope'] = "offline_access,publish_stream,read_friendlists"
        return HttpResponseRedirect(auth_url % urllib.urlencode(args))

def twitter_auth(request):
    profile = request.profile

    if profile.tw_token and profile.tw_token_secret:
        # We have already authorized user
        auth_response = HttpResponse()
        auth_response.content = return_self_closing_page()

        return auth_response

    auth_token = request.GET.get("oauth_token",None)

    # Check if we're operating as callback
    if auth_token:
        oauth_consumer = oauth.Consumer(key=getattr(settings, 'TWITTER_API_KEY'),
                                        secret=getattr(settings, 'TWITTER_SECRET_KEY'))
        oauth_client = oauth.Client(oauth_consumer)
        resp, content = oauth_client.request('https://api.twitter.com/oauth/access_token',
                                             method='POST',
                                             body='oauth_token=%s' % (auth_token))

        content = dict(cgi.parse_qsl(content))

        profile.tw_token = content['oauth_token']
        profile.tw_token_secret = content['oauth_token_secret']
        profile.tw_auth = True
        profile.put()

        auth_response = HttpResponse()
        auth_response.content = return_self_closing_page()

        return auth_response


    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    oauth_consumer = oauth.Consumer(key=getattr(settings, 'TWITTER_API_KEY'),
                                    secret=getattr(settings, 'TWITTER_SECRET_KEY'))
    oauth_client = oauth.Client(oauth_consumer)
    resp, content = oauth_client.request('https://api.twitter.com/oauth/request_token', 'GET')

    content = dict(cgi.parse_qsl(content))
    redirect_uri = request.build_absolute_uri()
    redirect_uri = redirect_uri.split("?")[0]

    auth_url = '%s?oauth_token=%s&oauth_callback=%s' % ('https://api.twitter.com/oauth/authorize',
                                                        content['oauth_token'],
                                                        redirect_uri)

    return HttpResponseRedirect(auth_url)

def return_self_closing_page():
    ret_val = """
        <html>
            <head>
                <title>Auth Success</title>
                <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js"></script>
            </head>
            <body>
                <script type="text/javascript">
                    $(document).ready(function() {
                        self.close()});
                </script>
                <h1>Auth Success</h1>
                <p>You have authenticated successfully, you may now close this window</p>
            </body>
        </html>"""
    return ret_val

def return_fake_end_user(profile):
    level_list = list()
    tmp_dict = {"end_user_title":"The Cookie Monster Badge",
                "end_user_description":"You eat 'em like a pro!",
                "url":"http://media.moddb.com/images/downloads/1/17/16213/cookie-monster_with_text.jpg"}
    level_list.append(tmp_dict)

    tmp_dict = {"end_user_title":"Fraggle Rockin'",
                "end_user_description":"Dummy badges are hard to describe!",
                "url":"http://tribeofdad.net/wp-content/uploads/2009/03/fraggle_rock.jpg"}
    level_list.append(tmp_dict)

    tmp_dict = {"end_user_title":"Ch**in' the Chicken",
                "end_user_description":"Bork!",
                "url":"http://www.rufkm.net/wp-content/uploads/2009/10/SwedishChef_muppet1.jpg"}
    level_list.append(tmp_dict)

    ret_dict = {'end_user_login':profile.uid,
                'levels':level_list}

    return ret_dict
