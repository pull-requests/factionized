from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'app.views.user.index'),
    (r'^login$', 'app.views.auth.login'),
    (r'^logout$', 'app.views.auth.logout'),
)
