from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to

import views

urlpatterns = patterns('',
    url(r'^wiki/$', views.show, name='wiki_root'),
    url(r'^wiki/list/$', views.list_by_name, name='wiki_list'),
    
    url(r'^wiki/([-\w\/]{2,})/$', views.show, name='wiki_show'),

    url(r'^wiki/.*/$', redirect_to, {'url': '/wiki/'}),
)
