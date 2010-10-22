try:
    import json
except:
    from django.utils import simplejson as json
import urllib

from django.conf import settings
from google.appengine.api import urlfetch

from app.lib import oauth2 as oauth
#from app.lib import twitter
from app.lib.oauthtwitter import OAuthApi as Api

from app.models import Profile
FACTIONIZE_URL = 'http://factionized.appspot.com'

class TwitterUser(object):

    def __init__(self,profile):
        self.auth_token = profile.tw_token
        self.auth_token_secret = profile.tw_token_secret
        self.api_key = getattr(settings, 'TWITTER_API_KEY')
        self.api_secret = getattr(settings, 'TWITTER_SECRET_KEY')

        signing_key = '&'.join([self.api_key, self.auth_token_secret])

        oauth_consumer = oauth.Consumer(key=self.api_secret,
                                        secret=signing_key)
        self.client = oauth.Client(oauth_consumer)

    def post_to_feed(self,message,image_url,caption=None):
        link = FACTIONIZE_URL
        short_image_url = self.shorten_url(image_url)

        if caption:
            message = '%s %s: %s' % (short_image_url,
                                     caption,
                                     message)
        else:
            message = '%s: %s' % (short_image_url,
                                  message)

        api = Api(consumer_key=self.api_key, consumer_secret=self.api_secret,
                  access_token_key=self.auth_token, access_token_secret=self.auth_token_secret)
        status = api.PostUpdate(message)

    def shorten_url(self,url):
        format = 'json'
        version = '2.0.1'
        api_key = getattr(settings, 'BITLY_API_KEY')
        api_user = getattr(settings, 'BITLY_API_USER')
        args = {'version':version,
                'format':format,
                'apiKey':api_key,
                'login':api_user,
                'longUrl':url}

        short_req_url = 'http://api.bit.ly/shorten?'
        resp = urlfetch.fetch(short_req_url + urllib.urlencode(args))
        result = json.loads(resp.content)

        return result['results'][url]['shortUrl']
