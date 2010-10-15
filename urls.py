from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'app.views.root.dashboard_view'),
    (r'^/games$', 'app.views.game.index'),
    (r'^/games/(?P<game_id>[^/]+)$', 'app.views.game.game_view'),
    # Example:
    # (r'^factionized/', include('factionized.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
