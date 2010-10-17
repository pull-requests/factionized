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
urlpatterns += patterns('app.views.profile',
    url('^profile$', 'index', name='profile_index'),
)

# Games
urlpatterns += patterns('app.views.game',
    url('^games$', 'index', name='game_index'),
    url('^games/(?P<game_id>\w+)$', 'view', name='game_view'),
)

# Activities
urlpatterns += patterns('app.views.activity',
    url('^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)/activities$', 'activities', name='activity_list'),
    url('^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)/votes$', 'votes', name='vote_list'),
    url('^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)/messages$', 'messages', name='message_list'),
)

# Round End Task
urlpatterns += patterns('app.views.task',
    url('^/tasks/round_end/games/(?P<game>\w+)/rounds/(?P<round>\w+)/$',
        'end',
       name='end_round'),
)
