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

    def get_subpages(self, page, remove=[]):
        subpages = {'dirs': [], 'files': []}
        if os.path.isdir(page.fp):
            for path, dirs, files in os.walk(page.fp):
                if '_' in files:
                    files.remove('_')
                for pg in sorted(dirs):
                    if page.pg:
                        pg = page.pg + '/' + pg
                    subpages['dirs'].append(Page(pg))
                for pg in sorted(files):
                    if page.pg:
                        pg = page.pg + '/' + pg
                    subpages['files'].append(Page(pg))
                break
        if not subpages['dirs'] and not subpages['files']:
            subpages = {}
        return subpages

    @property
    def children(self):
        return self.get_subpages(self)

    @property
    def siblings(self):
        siblings = self.get_subpages(self.parent, remove=[self])
        # for page in siblings['dirs']:
            # if page.pg == self.pg:
                # siblings['dirs'].remove(page)
                # break
        # for page in siblings['files']:
            # if page.pg == self.pg:
                # siblings['files'].remove(page)
                # break
        return siblings

    def save(self, content):
        fp = self.fp
        if not os.path.isfile(self.fp): # then will have to do something unusual
            if os.path.isdir(self.fp): # then save the content in a special file
                fp = fp + '/_'
            else: # the page doesn't exist --- before we build it, we need to 
                  # make sure the directory structure is compatible
                dirs = self.pg.split('/')
                fp = pg_path
                for d in dirs[:-1]: # these directories should all exist
                    fp = os.path.join(fp, d)
                    if os.path.isfile(fp): # then we need to prepare to push this content into a new directory
                        os.rename(fp, fp + '__')
                    if not os.path.isdir(fp): # then we need to create it
                        os.mkdir(fp)
                    if os.path.isfile(fp + '__'): # then pull this special content into the new directory
                        os.rename(fp + '__', fp + '/_')
                fp = self.fp # reset in order to prepare to save the content
                
        f = codecs.open(fp, 'w+', 'utf-8')
        f.write(content.strip())
        f.close
        
    def delete(self):
        pass

    def __unicode__(self):
        return self.pg

