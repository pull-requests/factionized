import time
from datetime import datetime

from django.http import Http404, HttpResponse
from django.conf import settings
from app.models import (Activity, Message, Vote, Thread, Role, Game,
                        Profile, role_vanillager)
from app.shortcuts import json
from bigdoorkit import Client

def activities(request, game_id, round_id, thread_id):
    thread = Thread.get_by_uid(thread_id)
    if thread is None:
        raise Http404

    if not thread.profile_can_view(request.profile):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        return json(list(Activity.get_activities(request.user, thread)))

    # no POSTs here, return 404
    raise Http404


def votes(request, game_id, round_id, thread_id):
    thread = Thread.get_by_uid(thread_id)
    game = Game.get_by_uid(game_id)
    if thread is None:
        raise Http404

    if not thread.profile_can_view(request.profile):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        since = request.GET.get('since', None)
        return json(Vote.get_activities(request.user, thread, since=since))

    if request.method == 'POST':
        if not thread.profile_can_create(request.profile):
            return HttpResponse('Unauthorized', status=401)

        # find the target
        target_id = request.POST.get('target_id', None)
        if target_id is None:
            raise Exception('No target')

        target_profile = Profile.get_by_uid(target_id)
        target = Role.all().filter('player', target_profile)
        target = target.filter('game', game)
        target = target.fetch(1)[0]

        # find the last vote this user made (if any)
        game = Game.get_by_uid(game_id)
        actor = Role.get_by_profile(game, request.profile)

        last_vote = Vote.all().filter("thread", thread)
        last_vote = last_vote.filter("actor", actor)
        last_vote = last_vote.order("-created")
        try:
            last_vote = last_vote.fetch(1)[0]
        except IndexError, e:
            last_vote = None

        # if we found a vote, decrement that vote's counter
        if last_vote is not None:
            last_vote.decrement()

        # create the new vote
        vote = Vote(actor=actor,
                    target=target,
                    thread=thread)
        vote.put()

        # increment the counter
        vote.increment()

        if thread.name == role_vanillager:
            vote_count = Vote.all().filter('thread', thread).count()
            if not vote_count:
                # First vote in round
                c = Client(settings.BDM_SECRET, settings.BDM_KEY)
                eul = "profile:%s" % request.profile.uid
                c.post("/named_transaction_group/613301/execute/%s" % eul)
                if thread.round.number == 1:
                    # First vote in game
                    c.post("/named_transaction_group/613302/execute/%s" % eul)

        return json(vote)

def messages(request, game_id, round_id, thread_id):
    thread = Thread.get_by_uid(thread_id)
    if thread is None:
        raise Http404

    if not thread.profile_can_view(request.profile):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        since = request.GET.get('since', None)
        return json(Message.get_activities(request.user,
                                           thread,
                                           since=since))

    if request.method == 'POST':

        if not thread.profile_can_create(request.profile):
            return HttpResponse('Unauthorized', status=401)

        content = request.POST.get('content', None)
        if not content:
            return HttpResponse('Method Not Allowed - A message is required', status=405)

        # create the new message
        game = Game.get_by_uid(game_id)
        actor = Role.get_by_profile(game, request.profile)
        message = Message(actor=actor,
                          content=content,
                          thread=thread)
        message.put()
        return json(message)

    return HttpResponse('Method Not Allowed', status=405)

def long_poll_query(query):
    while 1:
        if query.count() > 1:
            return list(query.run())
        time.sleep(500)

def stream(request, game_id, round_id, thread_id, timestamp):
    thread = Thread.get_by_uid(thread_id)
    dt = datetime.utcfromtimestamp(float(timestamp)/1000)

    print dt

    if thread is None:
        raise Http404

    if not thread.profile_can_view(request.profile):
        return HttpResponse('Unauthorized', status=401)

    if request.method != 'GET':
        return HttpResponse('Method Not Allowed', status=405)

    activities = Activity.get_activities(request.user,
                                         thread,
                                         since=dt)
    if hasattr(settings, 'DEV') and settings.DEV:
        return json(list(activities.run()))
    else:
        return json(long_poll_query(activities))
