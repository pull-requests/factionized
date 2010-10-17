from app.decorators import login_required
from app.shortcuts import render, redirect, render_to_response
from app.models import Game, Round, Thread
from datetime import datetime, timedelta

@login_required
def details(request):
    return render('game/details.html')

@login_required
def index(request):
    if request.method == 'GET':
        context = {}
        games = Game.all()
        context['games'] = games
        return render_to_response('game/list.html',
                                  context)

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
