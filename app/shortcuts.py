from django.shortcuts import render_to_response
from django.template import RequestContext
from app import context

def render(*args, **kw):
    kw['context_instance'] = kw.get('context_instance',
                                    RequestContext(context.request))
    return render_to_response(*args, **kw)
