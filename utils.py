from __future__ import division
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader

def render_to_response(request, template, context):
    c = RequestContext(request, context)
    t = loader.get_template(template)
    return HttpResponse(t.render(c))

## -------------------------------------------------------------------------- ##

import os
import sys

from models import Page
from config import wiki_pages_path

def loaddata():
    '''
    Designed to be run from shell. 
    Will wipe DB and load data from file system.
    
    .. ::
    
        python manage.py shell
        >>> import apps.wiki.utils as utils
        >>> utils.loaddata()
    '''
    pg_list = []
    for root, dirs, files in os.walk(wiki_pages_path):
        head = root.replace(wiki_pages_path, '')
        path = head.split(os.sep)
        for file in files:
            pg = '/'.join(path + [file])
            if pg[-1:] == '_':
                pg = pg[:-1]
            else:
                pg = pg + '/'
            print pg
            pg_list.append(pg)

    confirm = raw_input('About to create {} pages. Ready to wipe DB ([y]/n)? '.format(len(pg_list)))
    if confirm and confirm.upper() != 'Y':
        print 'Aborting...'
        sys.exit()
        
    print 'Deleting all Page data'
    Page.objects.all().delete()

    for pg in sorted(pg_list):
        print 'Creating: ', pg
        page = Page(pg=pg)
        page.update(pull_docinfo=False)
