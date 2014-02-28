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
        self.fp = os.path.join(pg_path, self.pg)
        if pg:
            self.title = pg.split('/')[-1]
        else:
            self.title = 'WikiRoot'


    @property
    def exists(self):
        return os.path.exists(self.fp)

    @property
    def raw_content(self):
        raw_content = ''
        fp = self.fp
        if os.path.isdir(self.fp):
            fp = os.path.join(fp, '_')
        if os.path.isfile(fp):
            f = codecs.open(fp, 'r', 'utf-8')
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
        return Page('/'.join(dirs))

    def get_subpages(self, page):
        subpages = {'dirs': [], 'files': []}
        if os.path.isdir(page.fp):
            for path, dirs, files in os.walk(page.fp):
                if '_' in files:
                    files.remove('_')
                for d in sorted(dirs):
                    pg = d
                    if page.pg:
                        pg = page.pg + '/' + pg
                    subpages['dirs'].append(Page(pg))
                for f in sorted(files):
                    pg = f
                    if page.pg:
                        pg = page.pg + '/' + pg
                    subpages['files'].append(Page(pg))
                break
        if not subpages['dirs']:
            del subpages['dirs']
        if not subpages['files']:
            del subpages['files']
        return subpages

    @property
    def children(self):
        return self.get_subpages(self)

    @property
    def siblings(self):
        siblings = self.get_subpages(self.parent)
        for page in siblings['dirs']:
            if page.pg == self.pg:
                siblings['dirs'].remove(page)
                break
        for page in siblings['files']:
            if page.pg == self.pg:
                siblings['files'].remove(page)
                break
        return siblings

    def save(self, content):
        fp = self.fp
        if not os.path.isfile(self.fp):
            if os.path.isdir(self.fp):
                fp = fp + '/_'
            else:
                dirs = self.pg.split('/')
                fp = pg_path
                for d in dirs:
                    fp = os.path.join(fp, d)
                    if not os.path.isdir(fp):
                        if os.path.isfile(fp):
                            os.rename(fp, fp + '/_')
                            os.mkdir(fp)
                            os.rename(fp + '/_', os.path.join(fp, '/_'))
                        else:
                            os.mkdir(fp)
        f = codecs.open(fp, 'w+', 'utf-8')
        f.write(content.strip())
        f.close

    def __unicode__(self):
        return self.pg

