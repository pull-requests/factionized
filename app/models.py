from google.appengine.ext import db
from app.lib.uid import new_uid

class UIDModel(db.Model):
    """Base class to give models a nicer, URL friendly ID.
    """
    def __init__(self, *args, **kw):
        if not 'key_name' in kw and not '_from_entity' in kw:
            kw['key_name'] = new_uid()

        super(UIDModel, self).__init__(*args, **kw)

        if not '_from_entity' in kw:
            self.uid = kw['key_name']

    uid = db.StringProperty()

    @classmethod
    def get_by_uid(cls, uid):
        return cls.get_by_key_name(uid)

class Game(UIDModel):
    name = db.StringProperty(required=True)
    game_starter = db.KeyProperty(required=True)

class Profile(UIDModel):
    name = db.StringProperty(required=True)

class Role(UIDModel):

    type_id = db.IntegerProperty(required=True)
    game = db.ReferenceProperty(Game, required=True)
    profile = db.ReferenceProperty(Profile,
                                   required=True,
                                   collection_name='roles')


class Slot(UIDModel):
    player = db.ReferenceProperty(Profile)
    game = db.ReferenceProperty(Game)
    role = db.ReferenceProperty(Role)
    in_play = db.BooleanProperty(default=True)

class Round(UIDModel):

    number = db.IntegerProperty(required=True)
    started = db.DateTimeProperty(auto_now_add=rue,
                                  required=True)


class Activity(UIDModel):

    type_id = db.IntegerProperty(required=True)
    actor = db.ReferenceProperty(Role,
                                 required=True, 
                                 collection_name='initiated_actions')
    target = db.ReferenceProperty(Role, 
                                  required=True, 
                                  collection_name='received_actions')
    occurred = db.DateTimeProperty(auto_now_add=True, 
                                   required=True)
    message = db.TextProperty()

