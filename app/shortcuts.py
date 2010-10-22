try:
    import json as json_mod
except:
    #import simplejson as json_mod
    from django.utils import simplejson as json_mod

import time
from datetime import datetime
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
        if isinstance(obj, datetime):
            return time.mktime(obj.timetuple())
        if isinstance(obj, db.Key):
            return obj.name()
        if isinstance(obj, db.Query):
            obj = obj.get() or []
        if isinstance(obj, list) and len(obj) < 1:
            return obj
        if callable(getattr(obj, '__json__', None)):
            return obj.__json__()
        elif issubclass(obj.__class__, db.Model):
            model_data = dict()
            model_data['class'] = obj.__class__.__name__
            for field_name in obj.fields().keys():
                if field_name != '_class':
                    model_data[field_name] = getattr(obj, field_name)
            return model_data
        elif isinstance(obj, users.User):
            return dict(email=obj.email())
        else:
            return super(ModelEncoder, self).default(obj)

def json_encode(data):
    return json_mod.dumps(data, cls=ModelEncoder)

def json(data):
    return HttpResponse(json_encode(data), 'application/json')
