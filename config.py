from __future__ import division
from __future__ import unicode_literals

import os

from django.conf import settings

tex_path = settings.TEX_PATH
gs_command = settings.GS_CMD

wiki_pages_path = os.path.join('..', 'wiki-pages')
wiki_pages_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), wiki_pages_path)

if not os.path.exists(wiki_pages_path):
    os.makedirs(wiki_pages_path)

wiki_files_path = os.path.join('..', 'wiki-files')
wiki_files_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), wiki_files_path)

settings.STATICFILES_DIRS += (wiki_files_path,)

if not os.path.exists(wiki_files_path):
    os.makedirs(wiki_files_path)

latex_temp_path = os.path.join('_', 'latex')
latex_temp_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), latex_temp_path)

