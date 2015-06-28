from __future__ import division
from __future__ import unicode_literals

import codecs
import os
from datetime import datetime

from django.contrib.auth import logout as logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, Context, loader
from django.template.defaultfilters import slugify

from config import wiki_pages_path

from utils import render_to_response
from templatetags.docutils_extensions.utils import make_pdf
from templatetags.docutils_extensions.utils import rst2latex

from models import *


def wiki_logout(request):
    logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('wiki_root')


def show(request, pg='/'):            
    try:        
        page = Page.objects.get(pg=pg)
        page.update()
        template = 'wiki/show.html'
    except:
        if request.user.is_authenticated:
            return redirect('wiki_edit', pg)
        else:
            template = 'wiki/404.html'

    context = {
        'page' : page,
    }
    return render_to_response(request, template, context)


# @login_required(login_url=reverse('wiki_login')) # not sure why this doesn't work....
@login_required(login_url='/wiki/login/')
def edit(request, pg='/'):
    try:
        page = Page.objects.get(pg=pg)
    except: # we still have to pass 'pg' to the template...
        page = { 'pg': pg }

    template = 'wiki/edit.html'
    context = {
        'page' : page,
    }
    return render_to_response(request, template, context)


def post(request):
    if request.user.is_staff and request.method == 'POST':
        pg = request.POST['pg'] + '/'
        pg = pg.replace('//', '/')
        
        if 'cancel' in request.POST:
            return redirect('wiki_show', pg)

        try:
            page = Page.objects.get(pg=pg)
        except:
            page = Page(pg=pg)
            page.save()
            
        if 'delete' in request.POST:
            parent = page.parent
            page.delete()
            if parent:
                return redirect('wiki_show', parent.pg)
            else:
                return redirect('wiki_root')
        
        new_pg = request.POST['new_pg'] + '/'
        new_pg = new_pg.replace('//', '/')
        # new_pg = re.sub('[^\w^\/]+', '', new_pg) # poor man's validation attempt
        content = request.POST['content']
        content = content.replace('\r\n','\n')

        if 'update' in request.POST or 'submit' in request.POST:
            page.pg = new_pg
            page.raw_content = content
            page.save()
            if 'update' in request.POST:
                return redirect('wiki_edit', page.pg)
            else:
                return redirect('wiki_show', page.pg)

    # nothing should ever get here...
    return redirect('wiki_root')
    
    
def ppdf(request, pg=''):
    try:        
        page = Page.objects.get(pg=pg)
    except:
        return redirect('wiki_show', pg)

    context = {
        'page' : page,
    }
    template = 'wiki/ppdf.tex'

    c = Context(context,autoescape=False)
    t = loader.get_template(template)
    latex = t.render(c)

    pdfname = make_pdf(latex, repeat=2)
    pdffile = open(pdfname, 'rb')
    outfile = '%s.pdf' % slugify(page.title)
    response = HttpResponse(pdffile.read(), mimetype='application/pdf')
    # response['Content-disposition'] = 'attachment; filename=%s' % outfile

    return response
