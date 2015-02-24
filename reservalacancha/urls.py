from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #site urls
    url(r'^$', 'website.views.index'),
    url(r'^register/$', 'website.views.register'),
    url(r'^search/$', 'website.views.search'),
    url(r'^cancha/$', 'website.views.detail'),
    url(r'^reservar/$', 'website.views.reserve'),
    url(r'^reservas/$', 'website.views.my_reserves_client'),
    url(r'^reservaspropietario/$' , 'website.views.my_reserves_propietary'),
    url(r'^moderar/$', 'website.views.moderate_reserve'),
    url(r'^miscanchas/$', 'website.views.mis_canchas'),
    url(r'^cancha/eliminar/$', 'website.views.eliminar_cancha'),
    url(r'^cancha/crearcancha/$', 'website.views.crear_cancha'),
    url(r'^cancha/modificar/(?P<id_cancha>\d+)$', 'website.views.modificar_cancha'),
    #admin urls
    url(r'^admin/', include(admin.site.urls)),
    #auth urls
    url(r'^login/$', login),
	url(r'^logout/$', logout, {'next_page': '/'}),


)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT,}),
    )