from datetime import datetime

from google.appengine.api.labs import taskqueue

from django.core.urlresolvers import reverse

from app.exc import FactionizeTaskException
from app.models import (Round, VoteSummary, Save, DeathByVote, Reveal, 
                        role_vanillager, role_sheriff, role_doctor, 
                        role_mafia, roles)

import random

def get_thread_highest_vote(thread):
    vote_summary = thread.votesummary_set.order('-total')
    results = filter(lambda x: x.count == vote_summary[0].count,
                     vote_summary)
    results = random.shuffle(results)
    if len(results):
        return results[0].role
    else:
        # we will randomly kill someone now
        return random.shuffle(thread.members)[0].get()

def kill_in_threads(role, threads):
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
            

def end(request, game_id, round_id):
    
    round = Round.all().filter('uid', round_id).get()
    game = round.game

    if not round == game.current_round():
        raise FactionizeTaskException, 'Round argument is not the current round. Check if task has been repeated'

    village_thread = round.get_thread(role_vanillager)
    vote_death_role = get_thread_highest_vote(village_thread)
    
    sheriff_thread = round.get_thread(role_sheriff)
    doctor_thread = round.get_thread(role_doctor)
        
    if vote_death_role.name in [role_sheriff, role_doctor]:
        kill_in_threads(vote_death_role, [doctor_thread, sheriff_thread])
    vote_death_role.kill()
    death = DeathByVote(actor=vote_death_role,
                        vote_thread=village_thread,
                        thread=village_thread)

    doctor_saves = [x.role for x in filter(lambda x: x.count, 
                                           doctor_thread.votesummary_set) \
                    if x.total]
    sheriff_reveals = [x.role for x in filter(lambda x: x.count,
                                              sheriff_thread.votesummary_set) if
                       x.total]

    sherif_reveals = filter(lambda x: x.uid != vote_death_role.uid,
                            sheriff_reveals)

    if len(sheriff_reveals):
        # we know a reveal is valid and who should be revealed, but
        # not who did it, so figure that out
        revealers = filter_invalidated(sheriff_thread.vote_set)
        for r in revealers:
            reveal = Reveal(actor=r.actor,
                            target=r.target,
                            thread=r.thread)
            reveal.put()

    mafia_thread = round.get_thread(role_mafia)
    mafia_vote_death = get_thread_highest_vote(mafia_thread)

    if mafia_vote_death.uid in [ds.uid for ds in doctor_saves]:
        # we know that somebody successfully saved, but not who yet
        # figure that out here
        saviours = filter_invalidated(doctor_thread.vote_set)
        for s in saviours.filter(lambda x: \
                                    x.target.uid == mafia_vote_death.uid,
                                 saviours):
            save = Save(actor=s.actor,
                        target=s.target,
                        thread=village_thread)
            save.put()
    else:
        mafia_vote_death.kill()
        death = DeathByVote(actor=mafia_vote_death,
                            vote_thread=mafia_thread,
                            thread=village_thread)
        death.put()
        
    r = game.start_next_round()
    assert r.number == round.number + 1 # sanity check
    taskqueue.add(url=reverse('round_end', kw_args={'game_id':game.uid,
                                                    'round_id':r.uid}),
                  method='POST',
                  countdown=r.length())
                  
