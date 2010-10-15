#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys

# Uninstall Django 0.96
for k in [k for k in sys.modules if k.startswith('django')]:
    del sys.modules[k]

# Add Django 1.2 archive to the path
django_path = 'django.zip'
sys.path.insert(0, django_path)

import django.core.handlers.wsgi
from google.appengine.ext.webapp import util
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

def main():
    application = django.core.handlers.wsgi.WSGIHandler()
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
