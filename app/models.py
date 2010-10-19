from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from app.lib.uid import new_uid

from app.exc import FactionizeError, NoAvailableGameSlotsError

from datetime import datetime
from math import ceil, floor
from random import random

from django.conf import settings
from bigdoorkit import Client

role_vanillager = 'Vanillager'
role_doctor = 'Doctor'
role_sheriff = 'Sheriff'
role_mafia = 'Mafia'
role_bystander = 'Bystander'

roles = [role_vanillager,
         role_doctor,
         role_sheriff,
         role_mafia,
         role_bystander]

thread_pregame = 'Pre-Game'
thread_ghosts = 'Ghost'
threads = [role_vanillager, role_doctor, role_sheriff, role_mafia,
           role_bystander, thread_pregame, thread_ghosts]
public_threads = [thread_pregame, role_vanillager, role_bystander]

# Target is the first dict, killer is the second.
kill_txn_ids = {role_vanillager: {role_vanillager: 613293,
                                  role_mafia: 613294},
                role_mafia: {role_vanillager: 613295,
                             role_mafia: 613296},
               }

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
    fb_token = db.StringProperty(required=False)
    fb_uid = db.StringProperty(required=False)
    fb_auth = db.BooleanProperty(default=False)

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
    is_complete = db.BooleanProperty(default=False, required=True)

    def get_active_roles(self):
        role_query = self.role_set.filter('name !=', role_bystander)
        role_query = role_query.filter('is_dead', False)
        return role_query

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
        innocent_count = player_count - (mafia_count + 2) # to include specials

        self.create_role(role_mafia, count=mafia_count)
        self.create_role(role_doctor)
        self.create_role(role_sheriff)

        self.create_role(role_vanillager, count=innocent_count)
        
        self.put()

    def create_role(self, name, count=1):
        for i in range(count):
            r = Role(name=name,
                     player=self.signups.pop(0),
                     game=self)
            r.put()

    def add_to_waitlist(self, profile):

        pregame_round = self.get_rounds()
        if not pregame_round.count() or pregame_round[0].number != 0:
            raise FactionizeError, 'game is not in state to add bystander'
        pregame_round = pregame_round[0]

        if profile.key() in self.signups:
            raise FactionizeError, 'profile is already in the waitlist'

        role = Role(name=role_bystander,
                    player=profile,
                    game=self)
        role.put()

        thread = pregame_round.thread_set.filter('name', thread_pregame).get()
        thread.members.append(profile.key())
        thread.put()
        self.signups.append(profile.key())
        self.put()

        join_activity = PlayerJoin(actor=role,
                                  thread=thread)
        join_activity.put()

    def get_current_round(self):
        r = self.get_rounds()
        try:
            return r[0]
        except IndexError, e:
            return None

    def get_rounds(self):
        return self.round_set.order('-number')
    
    def create_game_threads(self, round):
        # create threads for each of the game threads and 
        # add members to them
        threads = [Thread(round=round,
                       name=k,
                       members=v(round.game)) for k,v in \
                thread_profile_selectors.iteritems()]

        for t in threads:
            t.put()

        return threads

    def start_next_round(self):
        if self.is_over():
            raise FactionizeError, 'can not start new round as game is over'

        last_round = self.get_rounds()
        if last_round.count():
            last_round = last_round[0]
            r = Round(game=self, number=last_round.number+1)
            self.create_game_threads(r)
            r.put()
            return r
        else:
            raise FactionizeError, 'start_next_round called on a game that has no rounds'

    def start_pregame(self):
        last_round = self.get_rounds()
        if last_round.count():
            raise FactionizeError, 'start_pregame called on a game that is already in or past pregame'

        pregame_round = Round(game=self,
                              number=0)
        pregame_round.put()
        pregame_thread = Thread(name=thread_pregame,
                                round=pregame_round,
                                members=[])
        pregame_thread.put()

    def start_game(self):
        if len(self.signups) < self.min_players:
            raise FactionizeError, 'not enough players to start game'

        last_round = self.get_rounds()
        if last_round.count() and last_round[0].number != 0:
            raise FactionizeError, 'start_game called on a game that is in progress'
        elif not last_round.count():
            raise FactionizeError, 'start_game called on a game that has no round zero (pregame)'

        self.create_roles()
        round = self.start_next_round()
        
        gs = GameStart(thread=round.get_thread(role_vanillager))
        gs.put()

        self.started = datetime.now()
        self.put()

    def is_over(self):
        return self.is_innocent_victory() or self.is_mafia_victory()

    def is_innocent_victory(self):
        remaining_counts = self.remaining_counts()
        return remaining_counts['mafia'] == 0

    def is_mafia_victor(self):
        remaining_counts = self.remaining_counts()
        return remaining_counts['innocent'] < remaining_counts['mafia']

    def remaining_counts(self):
        roles = self.get_active_roles()
        innocent_roles = [role_vanillager, role_sheriff, role_doctor]
        innocent_count = len(filter(lambda x: x['name'] in innocent_roles,
                                    roles))
        mafia_count = len(filter(lambda x: x['name'] == role_mafia, roles))

        
class Role(UIDModel):
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

    def kill(self, killed_by_role, round_number):
        self.is_dead = True
        self.put()

        # TODO: these should be moved to tasks
        # at this point, we don't care if the response is good or not.
        c = Client(settings.BDM_SECRET, settings.BDM_KEY)

        txn_id = kill_txn_ids[self.name][killed_by_role]
        eul = "profile:%s" % self.player.uid

        endpoint = "named_transaction_group/%d/execute/%s"
        endpoint = endpoint % (txn_id, eul)
        resp = c.post(endpoint)

        if round_number == 1 and killed_by_role == role_vanillager:
            # Bandwagoned. <Nelson>Ha ha!</Nelson>
            endpoint = "named_transaction_group/613292/execute/%s" % eul
            resp = c.post(endpoint)


class Round(UIDModel):
    game = db.ReferenceProperty(Game, required=True)
    number = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True,
                                  required=True)

    def get_threads(self, profile):
        return list(self.thread_set.filter('members', profile))

    def get_thread(self, name):
        return self.thread_set.filter('name', name).get()

    def length(self):
        return 60*60*5 # five minutes


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


class BaseActivity(polymodel.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True,
                                  required=True)
    thread = db.ReferenceProperty(Thread, required=True)

    @classmethod
    def get_activities(cls, user, thread, since=None):
        if isinstance(thread, basestring):
            thread = Thread.get_by_uid(thread)

        acts = cls.all().filter('thread', thread)

        if since:
            last = cls.get_by_uid(since)
            if last and last.thread == thread:
                acts.filter('created >', last.created)
            else:
                return []
        return acts.order('created')

class SystemActivity(BaseActivity):
    pass

class GameStart(SystemActivity):
    pass

class RoundEnd(SystemActivity):
    pass

class Activity(BaseActivity):
    actor = db.ReferenceProperty(Role,
                                 required=True,
                                 collection_name='initiated_actions')

class Message(Activity):
    content = db.TextProperty(required=True)


class DeathByVote(Activity):
    vote_thread = db.ReferenceProperty(Thread,
                                       required=True,
                                       collection_name='vote_deaths')


class Save(Activity):
    target = db.ReferenceProperty(Role,
                                  required=True,
                                  collection_name='received_saves')


class Reveal(Activity):
    target = db.ReferenceProperty(Role, 
                                  required=True,
                                  collection_name='received_reveals')


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


class PlayerJoin(Activity):
    pass

class MafiaWin(SystemActivity):
    pass

class InnocentWin(SystemActivity):
    pass
