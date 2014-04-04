from __future__ import division
from __future__ import unicode_literals

import os

wiki_pages_path = os.path.join('..', '_', 'wiki-pages')
wiki_pages_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), wiki_pages_path)

if not os.path.exists(wiki_pages_path):
    os.makedirs(wiki_pages_path)
