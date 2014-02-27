from __future__ import division
from __future__ import unicode_literals

import os

from django.contrib.auth import logout as logout
from django.contrib.auth.decorators import login_required
# from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect

from config import pg_path
from utils import render_to_response

from models import *


def wiki_logout(request):
    logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('wiki_root')


def list_by_name(request):
    pg_walk = next(os.walk(pg_path))
    
    template = 'wiki/list_by_name.html'
    context = {
        'dirs': sorted(pg_walk[1]),
        'files': sorted(pg_walk[2]),
    }
    return render_to_response(request, template, context)


def show(request, pg=''):
    if not pg:
        return list_by_name(request)
    if pg[:1] = '/':
        return redirect('wiki_show', pg[:1])

    # page = Page.objects.get(pg)
    page = Page(pg)

    if not page.exists:
        template = 'wiki/404.html'
    else:
        template = 'wiki/show.html'
    context = {
        'page' : page,
    }
    return render_to_response(request, template, context)


@login_required(login_url='/wiki/login/')    
def edit(request, pg=''): 
# blank will create a *new* page, but how to edit WikiRoot page?
    if not request.user.is_staff:
        return redirect('wiki_root')
 
    # page = Page.objects.get(pg)
    page = Page(pg)

    template = 'wiki/edit.html'
    context = {
        'page' : page,
    }
    return render_to_response(request, template, context)
    
    
def post(request): 
    if request.user.is_staff and request.method == 'POST':
        pg = request.POST['pg']
        title = request.POST['title']
        title = re.sub('[\/]+$', '', title) # cut any trailing slashes off...
        title = re.sub('[^\w^\/]+', '', title) # poor man's validation attempt
        content = request.POST['content']
        content = content.replace('\r\n','\n')

        # page = Page.objects.get(title)
        page = Page(title)

        if 'cancel' in request.POST:
            return redirect('wiki_show', pg)

        elif 'delete' in request.POST:
            if os.path.isfile(page.fp): # delete only files for now...
                os.remove(page.fp)
            return redirect('wiki_root')
        
        elif 'update' in request.POST or 'submit' in request.POST:
            if '/' in title:
                check_path(title) 
            page.save(content) # shouldn't check_path be in page.save?
            
            if title.lower() != pg.lower(): # case-sensitivity issue here?
            # then title was changed ... need to delete old file
                fp = os.path.join(pg_path, pg)
                if os.path.isfile(fp):
                    os.remove(fp)
                    
            if 'update' in request.POST:
                return redirect('wiki_edit', title)
            else:
                return redirect('wiki_show', title)

    # nothing should get here...
    return redirect('wiki_root')

    
def check_path(title):
    dirs = title.split('/')[:-1]
    if not os.path.isdir(os.path.join(pg_path, *dirs)):
        dir = pg_path
        for d in dirs:
            dir = os.path.join(dir, d)
            if not os.path.isdir(dir):
                if os.path.isfile(dir):
                    os.rename(dir, dir + '_')
                    os.mkdir(dir)
                    os.rename(dir + '_', os.path.join(dir, '_'))
                else:
                    os.mkdir(dir)

