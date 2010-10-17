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
    url('^games$', 'list', name='game_list'),
    url('^games/(?P<game_id>\w+)$', 'list', name='game_details'),
)

# Rounds
urlpatterns += patterns('app.views.round',
    url('^games/(?P<game_id>\w+)/rounds$', 'list', name='round_list'),
    url('^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)$', 'details', name='round_details'),
)

# Threads
urlpatterns += patterns('app.views.thread',
    url('^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads$', 'list', name='thread_list'),
    url('^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)$', 'details', name='thread_details'),
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
