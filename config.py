from __future__ import division
from __future__ import unicode_literals

import os

from django.conf import settings

pg_path = os.path.join('..', 'wiki-pages')
pg_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), pg_path)

if not os.path.exists(pg_path):
    os.mkdir(pg_path)
    
wiki_files_dir = os.path.join('..', 'wiki-files')
wiki_files_dir = os.path.join(os.path.dirname(os.path.abspath( __file__ )), wiki_files_dir)

wiki_files_url = '/wiki-files/'