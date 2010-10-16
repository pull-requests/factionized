from django.conf.urls.defaults import *

# Authentication
urlpatterns = patterns('app.views.auth',
    url('^login$', 'login', name='auth_login'),
    url(r'^logout$', 'logout', name='auth_logout'),
)

# User Profile
urlpatterns += patterns('app.views.user',
    url('^$', 'index', name='user_index'),
)
