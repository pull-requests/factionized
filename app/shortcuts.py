try:
    import json as json_mod
except:
    import simplejson as json_mod
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from google.appengine.ext import db
from google.appengine.api import users
from app import context

def render(*args, **kw):
    kw['context_instance'] = kw.get('context_instance',
                                    RequestContext(context.request))
    return render_to_response(*args, **kw)

class ModelEncoder(json_mod.JSONEncoder):
    def default(self, obj):
        if callable(getattr(obj, '__json__', None)):
            return obj.__json__()
        elif issubclass(obj.__class__, db.Model):
            model_data = dict(key=str(obj.key()), kind=obj.kind())
            for field_name in obj.fields().keys():
                model_data[field_name] = getattr(obj, field_name)
            return model_data
        elif isinstance(obj, users.User):
            return dict(email=obj.email)
        else:
            return super(ModelEncoder, self).default(obj)

def json(data):
    json_data = json_mod(data, cls=ModelEncoder)
    return HttpResponse(json_data, 'application/json')
