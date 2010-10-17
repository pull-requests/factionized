import json
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from app import context

def render(*args, **kw):
    kw['context_instance'] = kw.get('context_instance',
                                    RequestContext(context.request))
    return render_to_response(*args, **kw)

def json(dicts):
    return HttpResponse(json.dumps(dicts), 'application/json')
