from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #admin urls
    url(r'^admin/', include(admin.site.urls)),
    #auth urls
    url(r'^login/$', login),
	url(r'^logout/$', logout, {'next_page': '/'}),
    #site urls
    url(r'^$', 'website.views.index'),
    url(r'^list/$', 'website.views.list'),
    url(r'^detail/$', 'website.views.detail'),
    url(r'^reservas/$', 'website.views.mis_res'),
    url(r'^login/$', 'website.views.login'),
)
