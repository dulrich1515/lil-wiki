from __future__ import division
from __future__ import unicode_literals

import os

# from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from config import pg_path
from utils import render_to_response

from models import *


def list_by_name(request):
    pg_walk = next(os.walk(pg_path))
    
    context = {
        'pg_walk': pg_walk,
    }
    template = 'wiki/list_by_name.html'
    return render_to_response(request, template, context)


def show(request, pg='_'):
    page = Page(pg)
    if pg == '_' and not page.content:
        return list_by_name(request)
    
        
    context = {
        'page' : page,
    }
    template = 'wiki/show.html'
    return render_to_response(request, template, context)
