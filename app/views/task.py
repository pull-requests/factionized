from app.models import Activity, FactionizeError

class FactionizeTaskException(FactionizeError):
    # base exception of task level errors
    pass


def total_round_stream(activity_stream):

    mafia_channel_events = { 'vanillager': ['vote', 'nurse', 'sheriff'],
                            'mafia': ['vote'] }

    filtered_stream =  filter(lambda x: \
        activity.channel in mafia_channel_events and \
        activity.name in mafia_channel_events[activity_channel],
                              mafia_channel_events)

    totaled_events = mafia
    

def end(self, game, round):
    
    if not round == game.current_round(round):
        raise FacitonizeTaskException, 'Round argument is not the current round. Check if task has been repeated'

    results = round.reduce_stream()
    # resolve specials
    round.kill(vote_kill)
    nurse_sa
    # resolve mafia

    
