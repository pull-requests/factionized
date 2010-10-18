from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from app.lib.uid import new_uid

from app.exc import FactionizeError, NoAvailableGameSlotsError

from math import ceil, floor
from random import random

role_vanillager = 'vanillager'
role_doctor = 'doctor'
role_sheriff = 'sheriff'
role_mafia = 'mafia'

roles = [role_vanillager, role_doctor, role_sheriff, role_mafia]

thread_pregame = 'pregame'
thread_ghosts = 'ghosts'
threads = [role_vanillager, role_doctor, role_sheriff, role_mafia,
           thread_pregame, thread_ghosts]
public_threads = [thread_pregame, role_vanillager]


def member_selector(game, alive=True, role=None):
    q = game.role_set
    if alive is not None:
        q = q.filter('is_dead', not alive)
    if role:
        q = q.filter('name', role)

    return [r.player.key() for r in q]

vanillager_selector = lambda game : member_selector(game)
mafia_selector = lambda game: member_selector(game, role=role_mafia)
sheriff_selector = lambda game: member_selector(game, role=role_sheriff)
doctor_selector = lambda game: member_selector(game, role=role_doctor)
dead_selector = lambda game: member_selector(game, alive=False)

thread_profile_selectors = {role_vanillager: vanillager_selector,
                           role_mafia: mafia_selector,
                           role_sheriff: sheriff_selector,
                           role_doctor: doctor_selector,
                           thread_ghosts: dead_selector}

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

class Profile(UIDModel):
    user = db.UserProperty(required=True)
    name = db.StringProperty(required=False)

class Game(UIDModel):
    name = db.StringProperty(required=True)
    game_starter = db.ReferenceProperty(Profile)
    created_date = db.DateTimeProperty(auto_now_add=True)
    min_players = db.IntegerProperty(default=12)
    max_players = db.IntegerProperty(default=30)
    mafia_ratio = db.FloatProperty(default=0.33)
    modified_date = db.DateTimeProperty(auto_now=True)
    signup_deadline = db.DateTimeProperty(required=True)
    signups = db.ListProperty(db.Key)
    started = db.DateTimeProperty()

    def create_roles(self):
        # find out how many players there are
        player_count = len(self.signups)
        if player_count > self.max_players:
            player_count = self.max_players

        # work out the ratio of different roles
        mafia_count = player_count * self.mafia_ratio
        if mafia_count < 1:
            mafia_count = int(ceil(mafia_count))
        else:
            mafia_count = int(floor(mafia_count))

        # create the roles
        for i in range(mafia_count):
            r = Role(game=self,
                     name=role_mafia,
                     player=self.signups.pop(0))
            r.put()

        r = Role(game=self,
                 name=role_doctor,
                 player=self.signups.pop(0))
        r.put()

        r = Role(game=self,
                 name=role_sheriff,
                 player=self.signups.pop(0))
        r.put()
        self.put()

    def add_random_profile(self, profile):
        avail_roles = self.role_set.filter('player =', None)
        if avail_roles:
            r = random.shuffle(avail_roles)[0]
            r.player = profile
            r.put()
            return r
        else:
            raise NoAvailableGameSlotsError, 'player count reached'

    def get_current_round(self):
        r = self.get_rounds()
        try:
            return r[0]
        except IndexError, e:
            return None

    def get_rounds(self):
        r = Round.all().filter('game =', self)
        return r.order('-number')

    
    def create_game_threads(self, round):
        # create threads for each of the game threads and 
        # add members to them
        return [Thread(round=round,
                       name=k,
                       members=v(round.game)) for k,v in \
                thread_profile_selectors.iteritems()]


    def start_next_game_round(self):
        last_round = self.get_rounds()
        if last_round:
            last_round = last_round[0]
            r = Round(game=self, number=last_round.number+1)
            threads = self.create_game_threads(r)
            for t in threads:
                t.put()
            r.put()
            return r
        else:
            raise FactionizeError, 'start_next_round called on a game has no rounds'


class Role(polymodel.PolyModel):

    def __init__(self, *args, **kw):
        if not 'key_name' in kw and not '_from_entity' in kw:
            kw['key_name'] = new_uid()

        super(Role, self).__init__(*args, **kw)

        if not '_from_entity' in kw:
            self.uid = kw['key_name']

    uid = db.StringProperty()
    name = db.StringProperty(choices=roles, required=True)
    game = db.ReferenceProperty(Game, required=True)
    player = db.ReferenceProperty(Profile, default=None, required=True)
    is_dead = db.BooleanProperty(default=False, required=True)

    @classmethod
    def get_by_uid(cls, uid):
        return cls.get_by_key_name(uid)

    @classmethod
    def get_by_profile(cls, game, profile):
        r = cls.all().filter("player", profile)
        r = r.filter("game", game)
        try:
            return r[0]
        except IndexError, e:
            return None

    def kill(self):
        self.is_dead = True

class Round(UIDModel):
    game = db.ReferenceProperty(Game, required=True)
    number = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True,
                                  required=True)

    def get_threads(self, profile):
        return list(self.thread_set.filter('members', profile))

    def get_thead(self, name):
        return self.thread_set.filter('name', name).get()

class Thread(UIDModel):
    round = db.ReferenceProperty(Round, required=True)
    name = db.StringProperty(choices=threads)
    members = db.ListProperty(db.Key)

    def is_public(self):
        return self.name in public_threads

    def profile_can_view(self, profile):
        if self.is_public() or profile in self.members:
            return True
        return False

    def profile_can_create(self, profile):
        if profile in self.members:
            return True
        return False

class VoteSummary(db.Model):
    thread = db.ReferenceProperty(Thread, required=True)
    role = db.ReferenceProperty(Role, required=True)
    total = db.IntegerProperty(default=0)

class Activity(polymodel.PolyModel):
    actor = db.ReferenceProperty(Role,
                                 required=True,
                                 collection_name='initiated_actions')
    created = db.DateTimeProperty(auto_now_add=True,
                                  required=True)
    thread = db.ReferenceProperty(Thread, required=True)

    @classmethod
    def get_activities(cls, user, thread):
        if isinstance(thread, basestring):
            thread = Thread.get_by_uid(thread)
        acts = cls.all().filter('thread', thread)
        acts = acts.order('created')
        return acts


class Message(Activity):
    content = db.TextProperty(required=True)

class Kill(Activity):
    target = db.ReferenceProperty(Role,
                                  required=True,
                                  collection_name='received_kills')

class Vote(Activity):
    target = db.ReferenceProperty(Role,
                                  required=True,
                                  collection_name='received_votes')

    def increment(self):
        s = VoteSummary.all().filter("role", self.target)
        s = s.filter("thread", self.thread)
        try:
            s = s.order("-created")[0]
        except IndexError, e:
            s = VoteSummary(role=self.target,
                            thread=self.thread,
                            total=0)
        s.total += 1
        s.put()

    def decrement(self):
        s = VoteSummary.all().filter("role", self.target)
        s = s.filter("thread", self.thread)
        try:
            s = s.order("-created")[0]
        except IndexError, e:
            s = VoteSummary(role=self.target,
                            thread=self.thread,
                            total=0)
        s.total -= 1
        s.put()


class RoundEnd(Activity):
    pass
