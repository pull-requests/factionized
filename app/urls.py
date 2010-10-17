from django.conf.urls.defaults import *

# Front Page Marketing
urlpatterns = patterns('app.views.root',
    url('^$', 'index', name='root_index'),
)

# Authentication
urlpatterns += patterns('app.views.auth',
    url('^login$', 'login', name='auth_login'),
    url(r'^logout$', 'logout', name='auth_logout'),
)

# User Profile
urlpatterns += patterns('app.views.user',
    url('^user$', 'index', name='user_index'),
)

# Games
urlpatterns += patterns('app.views.game',
    url('^game$', 'list', name='game_list'),
    url('^game/(?P<game>\w+)$', 'list', name='game_details'),
)

# Round End Task
urlpattens += pattens('app.views.task',
    url('^/tasks/round_end/games/(?P<game>\d+)/rounds/(?P<round>\d+)/$'),
)
