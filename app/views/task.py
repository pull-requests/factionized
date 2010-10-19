import logging

from datetime import datetime

from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django.core.urlresolvers import reverse

from app.exc import FactionizeTaskException
from app.models import (Round, VoteSummary, Save, DeathByVote, Reveal, 
                        Profile, Game, MafiaWin, InnocentWin,
                        role_bystander, role_vanillager, 
                        role_sheriff, role_doctor, role_mafia, roles)

import random

def get_thread_highest_vote(thread):
    """
    Gets the results of a thread's votes and returns the
    voted role.
    """

    vote_summary = thread.votesummary_set.order('-total')
    results = filter(lambda x: x.count == vote_summary[0].count,
                     vote_summary)
    random.shuffle(results)
    if len(results):
        return results[0].role
    else:
        # we will randomly choose someone in the thread now
        # NOTE: for mafia, sheriff, nurse this will not work 
        #  because we always return a member of the thread,
        #  but for now it is their fault for not voting
        random_members = [i for i in thread.members]
        random.shuffle(random_members)
        unlucky_player = db.get(random_members[0])
        return thread.round.game.role_set.filter('name !=', role_bystander).get()

def kill_in_threads(role, threads):
    """
    Removes any activity of that given role from the thread.
    Used when a role is killed before their action is resolved
    """
    for t in threads:
        votes = role.vote_set.filter('thread', t).order('-created')
        if votes and len(votes):
            votes[0].decrement()

def filter_invalidated(activity_stream):
    """
    Return only actions that actually took place having filtered out
    any that were invalidated by the user taking a new action later
    """

    temp = {}
    for a in activity_stream:
        if a.thread.name not in temp:
            temp[a.thread.name] = {}
        temp[a.thread.name][a.actor.uid] = \
                max([a, temp[a.thread.name].get(a.actor.uid, 
                                                {'created':datetime.min})],
                    key = lambda x: x['created'])
    filtered = []
    for k,v in temp.iteritems():
        for x,y in v.iteritems():
            filtered.append(y)

    return filtered
            

def end_round(request, game_id, round_id):
    t = datetime.now()

    logging.debug('task end round started on game:%s round:%s' % \
                  (game_id, round_id))
    
    round = Round.all().filter('uid', round_id).get()
    game = round.game

    if not round.uid == game.get_current_round().uid:
        raise FactionizeTaskException, 'Round argument is not the current round. Check if task has been repeated'

    village_thread = round.get_thread(role_vanillager)
    sheriff_thread = round.get_thread(role_sheriff)
    doctor_thread = round.get_thread(role_doctor)
    mafia_thread = round.get_thread(role_mafia)

    vote_death_role = get_thread_highest_vote(village_thread)
    logging.debug(('game:%s round:%s vote kill role_id:%s (%s) ' + \
                  'profile_name:%s google_id:%s') % \
                    (game.uid,
                     round.uid,
                     vote_death_role.uid, 
                     vote_death_role.name, 
                     vote_death_role.player.name,
                     vote_death_role.player.user.user_id()))

    if vote_death_role.name in [role_sheriff, role_doctor]:
        kill_in_threads(vote_death_role, [doctor_thread, sheriff_thread])
    vote_death_role.kill(role_vanillager, round.number)
    death = DeathByVote(actor=vote_death_role,
                        vote_thread=village_thread,
                        thread=village_thread)

    doctor_saves = [x.role for x in filter(lambda x: x.count, 
                                           doctor_thread.votesummary_set) \
                    if x.total]
    sheriff_reveals = [x.role for x in filter(lambda x: x.count,
                                              sheriff_thread.votesummary_set) \
                       if x.total]

    sheriff_reveals = filter(lambda x: x.uid != vote_death_role.uid,
                            sheriff_reveals)

    if len(sheriff_reveals):
        # we know a reveal is valid and who should be revealed, but
        # not who did it, so figure that out
        revealers = filter_invalidated(sheriff_thread.vote_set)
        for r in revealers:

            logging.debug(('game:%s round:%s sheriff reveal actor:%s ' + \
                          'target:%s role:%s') % \
                            (game.uid, 
                             round.uid,
                             r.actor.uid,
                             r.target.uid,
                             r.target.name))

            reveal = Reveal(actor=r.actor,
                            target=r.target,
                            thread=r.thread)
            reveal.put()

    mafia_vote_death = get_thread_highest_vote(mafia_thread)

    if mafia_vote_death.uid in [ds.uid for ds in doctor_saves]:
        # we know that somebody successfully saved, but not who yet
        # figure that out here
        saviours = filter_invalidated(doctor_thread.vote_set)
        for s in saviours.filter(lambda x: \
                                    x.target.uid == mafia_vote_death.uid,
                                 saviours):

            logging.debug('game:%s round:%s nurse save actor:%s target:%s' % \
                          (game.uid,
                           round.uid,
                           r.actor.uid,
                           r.target.uid,
                           r.target.name))

            save = Save(actor=s.actor,
                        target=s.target,
                        thread=village_thread)
            save.put()
    else:
        logging.debug(('game:%s round:%s mafia kill role_id:%s (%s) ' + \
                      'profile_name:%s google_id:%s') % \
                      (game.uid,
                       round.uid,
                       mafia_vote_death.uid, 
                       mafia_vote_death.name, 
                       mafia_vote_death.player.name,
                       mafia_vote_death.player.user.user_id()))

        mafia_vote_death.kill(role_mafia, round.number)
        death = DeathByVote(actor=mafia_vote_death,
                            vote_thread=mafia_thread,
                            thread=village_thread)
        death.put()
    
    if not game.is_over():
        logging.debug('game:%s round:%s starting next round' % \
                      (game.uid, round.uid))
        r = game.start_next_round()
        logging.debug('game:%s started new round:%s' % (game.uid, r.uid))
        assert r.number == round.number + 1 # sanity check
        taskqueue.add(url=reverse('end_round', kwargs={'game_id':game.uid,
                                                        'round_id':r.uid}),
                      method='POST',
                      countdown=r.length())
    else:
        logging.debug('game:%s round:%s has hit the end game condition' %  \
                      (game.uid, round.uid))
        taskqueue.add(url=reverse('end_game', kwargs={'game_id':game.uid}),
                      method='POST')

    logging.debug('game:%s round:%s end round total_time:%s' % \
                  (game.uid, round.uid, (datetime.now() - t).seconds))
                 
def end_game(request, game_id):
   
    t = datetime.now()

    game = Game.get_by_uid(game_id)
    last_round = game.get_current_round()
    
    if not game.is_over():
        logging.critical('game:%s game end task called but game is not over' % \
                         game.uid)
        raise FactionizeTaskException, 'game not yet in a completed state'

    if game.is_complete:
        logging.warning('game:%s game end task called on a game that is ' + \
                        'has already marked as complete. possibly a ' + \
                        'repeated message' % game.uid)
        raise FactionizeTaskException, 'game is already marked as complete'

    # do lots of processing here to assign various awards
    if game.is_innocent_victory():
        win = InnocentWin(thread=last_round.get_thread(role_vanillager))
    else:
        win = MafiaWin(thread=last_round.get_thread(role_vanillager))
    win.put()
    
    game.is_complete = True
    game.put()
    

