from __future__ import division
from __future__ import unicode_literals

import os

from django.contrib.auth import logout as logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect

from config import wiki_pages_path
from utils import render_to_response

from models import *


def wiki_logout(request):
    logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('wiki_root')


def list_by_name(request):
    template = 'wiki/list_by_name.html'
    context = {
        'root' : Page(''),
    }
    return render_to_response(request, template, context)


def show(request, pg=''):
    if not pg:
        return list_by_name(request)
    if pg[:1] == '/':
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


# @login_required(login_url=reverse('wiki_login')) # not sure why this doesn't work....
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
        old_pg = request.POST['old_pg']
        new_pg = request.POST['new_pg']
        new_pg = re.sub('[\/]+$', '', new_pg) # cut any trailing slashes off...
        new_pg = re.sub('[^\w^\/]+', '', new_pg) # poor man's validation attempt
        content = request.POST['content']
        content = content.replace('\r\n','\n')

        page = Page(new_pg)

        if 'cancel' in request.POST:
            return redirect('wiki_show', old_pg)

        elif 'delete' in request.POST:
            if os.path.isfile(page.fp): # error check --- it should exist (create before you annhilate)
                os.remove(page.fp)

            while page.parent: # check if the directory is now empty --- if so, demote the directory
                path, dirs, files = next(os.walk(page.parent.fp))
                if dirs: # don't delete if there are subdirectories
                    break
                else: # there are no subdirectories
                    if files and files != ['_']: # don't delete if there are other files
                        break
                    else: # the directory is effectively empty
                        fp = page.parent.fp
                        if files == ['_']: # capture this special content if it is there
                            os.rename(fp + '/_', fp + '__')
                        os.rmdir(fp) # delete the directory
                        if os.path.isfile(fp + '__'): # remove the special content tag
                            os.rename(fp + '__', fp)
                page = page.parent

            return redirect('wiki_show', page)

        elif 'update' in request.POST or 'submit' in request.POST:
            page.save(content)

            if new_pg.lower() != old_pg.lower(): # case-sensitivity issue here?
            # then pg was changed ... need to delete old file
                fp = os.path.join(wiki_pages_path, old_pg)
                if os.path.isfile(fp):
                    os.remove(fp)

            if 'update' in request.POST:
                return redirect('wiki_edit', new_pg)
            else:
                return redirect('wiki_show', new_pg)

    # nothing should get here...
    return redirect('wiki_root')
