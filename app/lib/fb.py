import facebook
import json

from app.models import Profile
FACTIONIZE_URL = 'http://www.factionize.com'

FACEBOOK_APP_ID = '6977d97b393a2181f5d1cd8fd76f643b'
FACEBOOK_APP_SECRET = 'abca90b7623f2d0c6b83e2809dbe6345'

class FacebookUser(object)
    def __init__(self,profile):
        pass

    def post_to_wall(self,message,image_url):
        """Post message/image_url to profile.fb_user's wall

        {"name": "Link name",
        "link": "http://www.example.com/",
        "caption": "{*actor*} posted a new review",
        "description": "This is a longer description of the attachment",
        "picture": "http://www.example.com/thumbnail.jpg"}
        """
        post_data = {"message":message,
                     "picture":image_url,
                     "link":FACTIONIZE_URL}
