from app.decorators import login_required
from app.shortcuts import render

@login_required
def list(request):
    return render('game/list.html')

@login_required
def details(request):
    return render('game/details.html')
