from __future__ import division
from __future__ import unicode_literals

from django.db.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import codecs
import os
import re

from config import wiki_pages_path
from config import wiki_image_path

from templatetags.docutils_extensions.utils import rst2xml

## -------------------------------------------------------------------------- ##

class Page(Model):
    pg = CharField(max_length=1024, blank=True, unique=True)
    raw_content = TextField(blank=True)    
    
    raw_title = CharField(max_length=256, blank=True, editable=False)
    subtitle = CharField(max_length=256, blank=True, editable=False)
    author = CharField(max_length=256, blank=True, editable=False)
    parent = ForeignKey('Page', null=True, blank=True, editable=False)
    
    create_date = DateTimeField(auto_now_add=True)
    update_date = DateTimeField(auto_now=True)
    
    @property
    def fp(self):
        fp = os.path.abspath(os.path.join(wiki_pages_path, self.pg[1:]))
        if os.path.isdir(fp):
            fp = os.path.abspath(os.path.join(wiki_pages_path, self.pg[1:], '_'))
        return fp

    @property
    def slug(self):
        if self.pg != '/':
            slug = self.pg.split('/')[-2]
        else:
            slug = 'WikiRoot'
        return slug

    @property
    def title(self):
        if self.raw_title:
            return self.raw_title
        else:
            return self.slug

    @property
    def title2(self):
        return self.title.replace('_', '-')
    
    @property
    def long_title(self):
        if self.raw_title:
            return '[{self.slug}] {self.title}'.format(self=self)
        else:
            return '[{self.slug}]'.format(self=self)
        
    # CAN I PULL IN TITLES TO THIS AUTO-LINKS ???
    @property
    def content(self):
        # These MUST go in this order...
        # (is this really the best way to do this?)
        content = self.raw_content

        # 1a. Prepend parent to named child wiki-links
        pattern = r'`(.*) <<([\-\w]+)>>`_'
        repl = r'`\1 <<{}\2>>`_'.format(self.pg)
        content = re.sub(pattern, repl, content)

        # 2a. Prepend parent to remaining child wiki-links
        pattern = r'<<([\-\w]+)>>'
        repl = r'`\1 <<{}\1>>`_'.format(self.pg)
        content = re.sub(pattern, repl, content)
           
        if self.parent: # wiki_root has no parent...

            # 1b. Prepend parent to named sibling wiki-links
            pattern = r'`(.*) <<\.\/([\-\w]+)>>`_'
            repl = r'`\1 <</{}/\2>>`_'.format(self.parent.pg)
            content = re.sub(pattern, repl, content)

            # 2b. Prepend parent to remaining sibling wiki-links
            pattern = r'<<\.\/([\-\w]+)>>'
            repl = r'`\1 <</{}/\1>>`_'.format(self.parent.pg)
            content = re.sub(pattern, repl, content)

        # 3. Expand lone wiki-links (must start with slash)
        pattern = r'<</([\-\w\/]+)>>([^`])' # looking for back-tick to avoid converting the named links twice...
        repl = r'`\1 <</\1>>`_\2'
        content = re.sub(pattern, repl, content)

        # 4. Auto-link all wiki-pages
        pattern = r'`(.*) <<\/([\-\w\/]+)>>`_'
        repl = r'`\1 <{}show/\2/>`_'.format(reverse('wiki_root')) # need to fix this ugly reversal !!!
        content = re.sub(pattern, repl, content)

        # Prepend image directory for docutils_extensions

        pattern = r'\\includegraphics(.*){(.*)}'
        repl = r'\\includegraphics\1{{{0}/\2}}'.format(wiki_image_path)
        content = re.sub(pattern, repl, content)

        return content
        
    @property
    def children(self):
        return Page.objects.filter(parent=self)
        
    @property
    def siblings(self):
        return Page.objects.filter(parent=self.parent).exclude(page=self)
        
    @property
    def series(self):
        series = []
        m = re.match('([\w\/]*)_(\d\d\d)$', self.pg)
        if m: # this page is part of a series
            for s in Page.objects.filter(parent=self.parent):
                m1 = re.match('([\w\/]*)_(\d\d\d)$', s.pg)
                if m1:
                    if m1.group(1) == m.group(1):
                        series.append(s)
        series = sorted(series, key=lambda page: page.pg)
        return series
        
    def update(self, force_update=False, pull_docinfo=True): # check file system for updated version
        if os.path.isfile(self.fp):
            should_update = True
            if self.update_date:
                mod_timestamp = os.path.getmtime(self.fp)
                mod_datetime = datetime.datetime.fromtimestamp(mod_timestamp)
                if mod_datetime < self.update_date:
                    should_update = False
            if should_update or force_update:
                f = codecs.open(self.fp, 'r+', 'utf-8')
                raw_content = f.read()
                f.close
                self.raw_content = raw_content
        self.save(pull_docinfo=pull_docinfo)
        
    def save(self, pull_docinfo=True, args=[], kwargs={}):
        if pull_docinfo:
            try:
                root = rst2xml(self.raw_content)
                self.raw_title = root.find('title').text
                self.subtitle = root.find('subtitle').text
                self.author = root.find('docinfo').find('author').text
            except:
                pass
                
        if self.pg != '/':
            dirs = self.pg.split('/')
            parent_pg = '/'.join(dirs[:-2] + dirs[:1])
            try:
                parent = Page.objects.get(pg=parent_pg)
            except:
                parent = Page(pg=parent_pg)
                parent.save()
            self.parent = parent
            
        # save a copy to the file system

        fp = self.fp
        if not os.path.isfile(fp): # then will have to do something unusual
            if os.path.isdir(fp): # then save the content in a special file
                fp = fp + '/_'
            else: # the page doesn't exist --- before we build it, we need to
                  # make sure the directory structure is compatible
                dirs = self.pg.split('/')
                fp = wiki_pages_path
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
        f.write(self.raw_content.strip())
        f.close

        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.pg    

    class Meta:
        ordering = ['pg']
