from django.db.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import codecs
import os
import re

from config import pg_path

class Page(object):
    def __init__(self, pg):
        self.pg = pg
        
        if pg:
            self.title = pg.split('/')[-1]
        else:
            self.title = 'WikiRoot'

        self.fp = os.path.join(pg_path, self.pg)
        if os.path.isdir(self.fp):
            self.fp = os.path.join(self.fp, '_')

    @property
    def exists(self):
        return os.path.exists(self.fp)
            
    @property
    def raw_content(self):
        raw_content = ''
        if os.path.isfile(self.fp):
            f = codecs.open(self.fp, 'r', 'utf-8')
            raw_content = f.read()
            f.close()
        return raw_content
    
            
    @property
    def content(self, toc=False):    
        content = self.raw_content

        # Allows renaming of auto-links to wiki pages
        pattern = r'`(.+) <<([\w\/]+)>>`_'
        repl = r'`\1 <{}\2/>`_'.format(reverse('wiki_root'))
        content = re.sub(pattern, repl, content)

        # Auto-link to wiki pages (must happen last)
        pattern = r'<<([\w\/]+)>>'
        repl = r'`\1 <{}\1/>`_'.format(reverse('wiki_root'))
        content = re.sub(pattern, repl, content)
    
        if content:
            if toc:
                content = '.. contents:: Table of contents\n\n' + content
                
            content = '.. default-role:: math\n\n' + content
            
        return content
    
    @property
    def parent(self):
        dirs = self.pg.split('/')[:-1]
        return '/'.join(dirs)
        
    @property
    def children(self):
        return ['eldest', 'middle', 'youngest']
        
    @property
    def siblings(self):
        return ['sister', 'brother']
        
    def save(self, content):
        f = codecs.open(self.fp, 'w+', 'utf-8')
        f.write(content.strip())
        f.close

        