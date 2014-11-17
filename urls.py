from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to

import views

urlpatterns = patterns('',
    url(r'^wiki/$', views.show, name='wiki_root'),

    url(r'^wiki/show(?P<pg>(/[\w\-/]*))$', views.show, name='wiki_show'),
    url(r'^wiki/edit(?P<pg>(/[\w\-/]*))$', views.edit, name='wiki_edit'),
    url(r'^wiki/ppdf(?P<pg>(/[\w\-/]*))$', views.ppdf, name='wiki_ppdf'),

    url(r'^wiki/post/$', views.post, name='wiki_post'),

    url(r'^wiki/login/$', 'django.contrib.auth.views.login', {'template_name': 'wiki/login.html'}, name='wiki_login'),
    url(r'^wiki/logout/$', views.wiki_logout, name='wiki_logout'),
)
