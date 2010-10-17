from app.exc import FactionizeTaskException

def end(self, game, round):
    
    if not round == game.current_round(round):
        raise FactionizeTaskException, 'Round argument is not the current round. Check if task has been repeated'

    results = round.reduce_stream()
    # resolve specials
    round.kill(vote_kill)
    nurse_sa
    # resolve mafia

    
