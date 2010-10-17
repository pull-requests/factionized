from django.http import Http404
from django.shortcuts import redirect
from app.decorators import login_required
from app.shortcuts import render
from app.models import Game, Round, Thread
from datetime import datetime, timedelta

@login_required
def index(request):
    if request.method == 'GET':
        games = Game.all()
        return render('game/list.html',
                      dict(games=games))

    elif request.method == 'POST':
        values = request.POST
        game = Game()
        game.name = values.get('name', 'Unnamed game')
        game.game_starter = request.profile
        game.signup_deadline = datetime.now() + timedelta(7)
        game.put()

        # create round 0
        r = Round()
        r.game = game
        r.number = 0
        r.put()

        # create pre-game thread
        t = Thread()
        t.round = r
        t.is_public = True
        t.put()

        # redirect to the game
        return redirect('/games/%s' % game.uid)

def view(request, game_id):
    game = Game.get_by_uid(game_id)
    if game is None:
        raise Http404

    current_round = game.get_current_round()
    rounds = game.get_rounds()
    threads = current_round.get_threads(request.profile)
    return render('game/view.html',
                  dict(current_round=current_round,
                       rounds=rounds,
                       threads=threads))

@login_required
def join(request, game_id):
    game = Game.get_by_uid(game_id)
    if game is None:
        raise Http404

    game.signups.append(request.profile)
    game.put()
    return redirect('/game/%s' % game.uid)
