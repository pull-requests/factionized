from app.exc import FactionizeTaskException

from app.models import Round

def end(request, round_id):
    
    round = Round.all().filter('uid =', round_id).get()
    game = round.game

    if not round == game.current_round():
        raise FactionizeTaskException, 'Round argument is not the current round. Check if task has been repeated'

