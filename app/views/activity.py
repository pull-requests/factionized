from app.decorators import login_required

@login_required
def activities(request, game_id, round_id, thread_id):
    pass

@login_required
def votes(request, game_id, round_id, thread_id):
    pass

@login_required
def messages(request, game_id, round_id, thread_id):
    pass
