from __future__ import division
from __future__ import unicode_literals

import os

from django.conf import settings

wiki_pages_path = os.path.join('..', 'wiki-pages')
wiki_pages_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), wiki_pages_path)

if not os.path.exists(wiki_pages_path):
    os.mkdir(wiki_pages_path)
    
wiki_files_path = os.path.join('..', 'wiki-files')
wiki_files_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), wiki_files_path)

if not os.path.exists(wiki_files_path):
    os.mkdir(wiki_files_path)
    
settings.STATICFILES_DIRS += (
    wiki_files_path,
)
