from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
#from app.models import Game

def index(request):
    if request.method == 'GET':
        games = []#Game.all()
        context = dict(games=games)
        return render_to_response('game/index.html',
                                  context)
    elif request.method == 'POST':
        # create a new game here
        raise NotImplementedError()
    else:
        raise Http404

