from django.conf.urls.defaults import *

# Front Page Marketing
urlpatterns = patterns('app.views.root',
    url(r'^$', 'index', name='root_index'),
)

# Authentication
urlpatterns += patterns('app.views.auth',
    url(r'^login$', 'login', name='auth_login'),
    url(r'^logout$', 'logout', name='auth_logout'),
)

# User Profile
urlpatterns += patterns('app.views.profile',
    url(r'^profile$', 'index', name='profile_index'),
    url(r'^profile/edit$', 'edit', name='profile_edit'),
    url(r'^profile/(?P<profile_id>\w+)/edit$', 'edit', name='profile_edit'),
    url(r'^profile/(?P<profile_id>\w+)$', 'show', name='profile_show')
)

# Games
urlpatterns += patterns('app.views.game',
    url(r'^games$', 'index', name='game_index'),
    url(r'^games/(?P<game_id>\w+)$', 'view', name='game_view'),
)

# Activities
urlpatterns += patterns('app.views.activity',
    url(r'^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)/activities$', 'activities', name='activity_list'),
    url(r'^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)/votes$', 'votes', name='vote_list'),
    url(r'^games/(?P<game_id>\w+)/rounds/(?P<round_id>\w+)/threads/(?P<thread_id>\w+)/messages$', 'messages', name='message_list'),
)

# Round End Task
urlpatterns += patterns('app.views.task',
    url(r'^/tasks/round_end/games/(?P<game>\w+)/rounds/(?P<round>\w+)/$',
        'end',
       name='end_round'),
)
