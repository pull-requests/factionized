from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from google.appengine.api import users
from app.decorators import login_required
from app.shortcuts import render
from app.models import Game, Round, Thread
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
                    signup_deadline=datetime.now() + timedelta(7))
        game.put()

        # create round 0
        r = Round(game=game,
                  number=0)
        r.put()

        # create pre-game thread
        t = Thread(round=r, is_public=True)
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

    now = datetime.now()
    if game.started < now or game.signup_deadline < now:
        return HttpResponse(status=401)

    if request.profile.key() not in game.signups:
        game.signups.append(request.profile)
        game.put()
    return redirect('/game/%s' % game.uid)
