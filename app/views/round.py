from app.decorators import login_required

@login_required
def list(request, game_id):
    pass

@login_required
def details(request, game_id, round_id):
    pass
