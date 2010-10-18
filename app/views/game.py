from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
from app.decorators import login_required
from app.shortcuts import render, json_encode
from app.exc import FactionizeError
from app.models import (Game, Round, Thread, thread_pregame, Role,
                        role_bystander)
from datetime import datetime, timedelta

def index(request):
    if request.method == 'GET':
        games = Game.all()
        return render('game/list.html',
                      dict(games=games))

    elif request.method == 'POST':
        if not hasattr(request, 'user') or not request.user:
            login_url = users.create_login_url(request.get_full_path())
            return redirect(login_url)
        values = request.POST
        game = Game(name=values.get('name', 'Unnamed game'),
                    game_starter=request.profile,
                    signup_deadline=datetime.now() + timedelta(7),
                    signups=[])
        game.put()

        game.start_pregame()
        game.add_to_waitlist(request.profile)

        # redirect to the game
        return redirect('/games/%s' % game.uid)

def view(request, game_id):
    game = Game.get_by_uid(game_id)
    if game is None:
        raise Http404

    current_round = game.get_current_round()
    rounds = game.get_rounds()
    threads = current_round.get_threads(request.profile)
    context = dict(profile=request.profile,
                   game=game,
                   current_round=current_round,
                   rounds=rounds,
                   threads=threads)
    context['serialized'] = json_encode(context)
    return render('game/view.html', context)

@login_required
def join(request, game_id):
    game = Game.get_by_uid(game_id)
    if game is None:
        raise Http404

    now = datetime.now()
    if (game.started and game.started < now) or game.signup_deadline < now:
        return HttpResponse(status=401)

    if request.profile.key() not in game.signups:
        game.add_to_waitlist(request.profile)
    return redirect('/game/%s' % game.uid)

@login_required
def start(request, game_id):
    game = Game.get_by_uid(game_id)
    if game.game_starter.uid != request.profile.uid:
        return HttpResponse(status=403)

    now = datetime.now()
    if (game.started and game.started < now) or game.signup_deadline < now:
        return HttpResponse(status=401)

    try:
        game.start_game()
    except FactionizeError, e:
        return HttpResponse('Cannot start game', status=401)

    latest_round = game.get_current_round()
    taskqueue.add(url=reverse('end_round', 
                              kwargs={'game_id':game.uid,
                                      'round_id':latest_round.uid}),
                  countdown=latest_round.length())
