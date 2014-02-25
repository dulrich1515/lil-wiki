from __future__ import division
from __future__ import unicode_literals

import os

pg_path = os.path.join('..', 'wiki-pages')
pg_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), pg_path)

if not os.path.exists(pg_path):
    os.mkdir(pg_path)