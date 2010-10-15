from django.http import Http404
from django.shortcuts import render_to_response

def dashboard_view(request):
    if request.method == 'GET':
        return render_to_response('index.html')
    else:
        raise Http404
