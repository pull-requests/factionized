from google.appengine.ext import db

class Game(db.Model):

    name = db.StringProperty(required=True)


class Profile(db.Model):
    
    name = db.StringProperty(required=True)


class Role(db.Model):

    type_id = db.IntegerProperty(required=True)
    game = db.ReferenceProperty(Game, required=True)
    profile = db.ReferenceProperty(Profile, 
                                   required=True, 
                                   collection_name='roles')


class Round(db.Model):

    number = db.IntegerProperty(required=True)
    started = db.DateTimeProperty(auto_now_add=True, 
                                  required=True)


class Activity(db.Model):

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

