from app.decorators import login_required
from app.shortcuts import render

@login_required
def index(request):
    return render('user/index.html')
