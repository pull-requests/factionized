from app.lib import facebook
import json
from django.conf import settings

from app.models import Profile
FACTIONIZE_URL = 'http://www.factionize.com'

class FacebookUser(object):

    def __init__(self,profile):
        self.graph = facebook.GraphAPI(profile.fb_token)
        #user = self.graph.get_object("me")

    def post_to_wall(self,message,image_url,link,caption=None):
        """Post message/image_url to profile.fb_user's wall

        {"name": "Link name",
        "link": "http://www.example.com/",
        "caption": "{*actor*} posted a new review",
        "description": "This is a longer description of the attachment",
        "picture": "http://www.example.com/thumbnail.jpg"}
        """
        put_data = {"picture":image_url,
                    "caption":caption,
                    "link":link}
        self.graph.put_wall_post(message,attachment=put_data,profile_id="me")
