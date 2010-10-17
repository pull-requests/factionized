from django.http import HttpResponse
from app.decorators import login_required
from app.models import Game, Round, Thread, Activity, Message, Vote
from app.shortcuts import json

def get_activities(cls, user, thread_id):
    thread = Thread.get_by_id(thread_id)
    if not thread:
        return HttpResponse('Not Found', status=404)
    if not thread.user_can_view(user):
        return HttpResponse('Unauthorized', status=401)
    return json([activity.to_dict() for activity in
                 cls.all().
                     filter('thread =', thread).
                     order('created')])
    

@login_required
def activities(request, game_id, round_id, thread_id):
    return get_activities(Activity, reqeust.user, thread_id)

@login_required
def votes(request, game_id, round_id, thread_id):
    if reqeust.method == 'GET':
        return get_activities(Vote, reqeust.user, thread_id)

@login_required
def messages(request, game_id, round_id, thread_id):
    pass
