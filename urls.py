from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to

import views

urlpatterns = patterns('',
    url(r'^wiki/$', views.show, name='wiki_root'),
    url(r'^wiki/show/([-\w\/]{2,})/$', views.show, name='wiki_show'),
    url(r'^wiki/edit/([-\w\/]{2,})/$', views.edit, name='wiki_edit'),

    url(r'^wiki/list/$', views.list_by_name, name='wiki_list'),
    url(r'^wiki/post/$', views.post, name='wiki_post'),
    url(r'^wiki/edit/$', views.edit, name='wiki_edit_new'),    

    url(r'^wiki/login/$', 'django.contrib.auth.views.login', {'template_name': 'wiki/login.html'}, name='wiki_login'),
    url(r'^wiki/logout/$', views.wiki_logout, name='wiki_logout'),
    
    url(r'^wiki/.*/$', redirect_to, {'url': '/wiki/'}),
)
