from django.db.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import os
import re

from config import wiki_pages_path
from config import wiki_image_path

## -------------------------------------------------------------------------- ##

class Page(Model):
    pg = CharField(max_length=1024, blank=True, unique=True)
    title = CharField(max_length=256, blank=True)
    subtitle = CharField(max_length=256, blank=True)
    author = CharField(max_length=256, blank=True)
    body_content = TextField(blank=True)
    parent = ForeignKey('Page', null=True, blank=True, editable=False)
    
    create_date = DateTimeField(auto_now_add=True)
    update_date = DateTimeField(auto_now=True)
    
    @property
    def fp(self):
        return os.path.abspath(os.path.join(wiki_pages_path, self.pg))
        
    @property
    def slug(self):
        if self.pg != '/':
            slug = self.pg.split('/')[-1]
        else:
            slug = 'WikiRoot'
        return slug

    @property
    def long_title(self):
        if self.title:
            return '[{self.slug}] {self.title}'.format(self=self)
        else:
            return '[{self.slug}]'.format(self=self)

    @property
    def title2(self):
        return self.title.replace('_', '-')
        
    @property
    def raw_content(self):
        raw_content = ''
        if self.title:
            raw_content += '{}\n'.format('=' * len(self.title))
            raw_content += '{}\n'.format(self.title)
            raw_content += '{}\n'.format('=' * len(self.title))
        if self.subtitle:
            raw_content += '{}\n'.format(self.subtitle)
            raw_content += '{}\n'.format('~' * len(self.subtitle))
            raw_content += '\n'
        if self.author:
            raw_content += ':author: {}\n'.format(self.author)
            raw_content += '\n'
        raw_content += self.body_content
        return raw_content
        
    # CAN I PULL IN TITLES TO THIS AUTO-LINKS ???
    @property
    def content(self):
        # These MUST go in this order...
        # (is this really the best way to do this?)
        content = self.raw_content

        # 1a. Prepend parent to named child wiki-links
        pattern = r'`(.*) <<([\-\w]+)>>`_'
        repl = r'`\1 <</{}/\2>>`_'.format(self.pg)
        content = re.sub(pattern, repl, content)

        # 2a. Prepend parent to remaining child wiki-links
        pattern = r'<<([\-\w]+)>>'
        repl = r'`\1 <</{}/\1>>`_'.format(self.pg)
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
        repl = r'`\1 <{}show/\2>`_'.format(reverse('wiki_root')) # need to fix this ugly reversal !!!
        content = re.sub(pattern, repl, content)

        # Prepend image directory for docutils_extensions

        pattern = r'\\includegraphics(.*){(.*)}'
        repl = r'\\includegraphics\1{{{0}/\2}}'.format(wiki_image_path)
        content = re.sub(pattern, repl, content)

        return content
        
    @property
    def children(self):
        return Page.objects.find(parent=self)
        
    @property
    def siblings(self):
        return Page.objects.find(parent=self.parent).exclude(self)
        
    @property
    def series(self):
        series = []
        m = re.match('([\w\/]*)_(\d\d\d)$', self.pg)
        if m: # this page is part of a series
            for s in Page.objects.find(parent=self.parent):
                m1 = re.match('([\w\/]*)_(\d\d\d)$', s.pg)
                if m1:
                    if m1.group(1) == m.group(1):
                        series.append(s)
        series = sorted(series, key=lambda page: page.pg)
        return series
        
    def save(self, *args, **kwargs):
        if self.pg != '/':
            parent_pg = self.pg.split('/')[:-1]
            try:
                parent = Page.objects.get(pg=parent_pg)
            except:
                parent = Page(pg=parent_pg)
                parent.save()
        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.pg    

    class Meta:
        ordering = ['pg']

## -------------------------------------------------------------------------- ##

import codecs

from templatetags.docutils_extensions.utils import rst2xml

class TextPage(object):
    def __init__(self, pg):
        self.pg = pg
        self.fp = os.path.abspath(os.path.join(wiki_pages_path, self.pg))
        self.exists = os.path.exists(self.fp)        

    @property
    def slug(self):
        if self.pg:
            slug = self.pg.split('/')[-1]
        else:
            slug = 'WikiRoot'
        return slug
        
    @property
    def raw_content(self):
        print "Pulling raw_content for " + self.pg
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
    def docinfo(self):
        root = rst2xml(self.raw_content)        
        docinfo = {}
        if root.find('title') is not None:
            docinfo['title'] = root.find('title').text
        if root.find('subtitle') is not None:
            docinfo['subtitle'] = root.find('subtitle').text
        if root.find('docinfo') is not None:
            for child in root.find('docinfo'):
                docinfo[child.tag] = child.text
        return docinfo
        
    @property
    def title(self):
        if 'title' in self.docinfo:
            title = self.docinfo['title']
        else:
            title = self.slug
        return title
    
    @property
    def title2(self):
        title2 = self.title.replace('_', '-')
        return title2

    # CAN I PULL IN TITLES TO THIS AUTO-LINKS ???
    @property
    def content(self):
        # These MUST go in this order...
        # (is this really the best way to do this?)
        content = self.raw_content

        # 1a. Prepend parent to named child wiki-links
        pattern = r'`(.*) <<([\-\w]+)>>`_'
        repl = r'`\1 <</{}/\2>>`_'.format(self.pg)
        content = re.sub(pattern, repl, content)

        # 2a. Prepend parent to remaining child wiki-links
        pattern = r'<<([\-\w]+)>>'
        repl = r'`\1 <</{}/\1>>`_'.format(self.pg)
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
        repl = r'`\1 <{}show/\2>`_'.format(reverse('wiki_root')) # need to fix this ugly reversal !!!
        content = re.sub(pattern, repl, content)

        # Prepend image directory for docutils_extensions

        pattern = r'\\includegraphics(.*){(.*)}'
        repl = r'\\includegraphics\1{{{0}/\2}}'.format(wiki_image_path)
        content = re.sub(pattern, repl, content)

        return content
    
    @property
    def parent(self):
        if self.pg:
            dirs = self.pg.split('/')[:-1]
            parent = TextPage('/'.join(dirs))
        else:
            parent = None
        return parent
            
    @property
    def children(self):
        children = self.get_subpages(self, as_list=True)
        return children
        
    @property
    def siblings(self):
        siblings = self.get_subpages(self.parent, as_list=True, remove=[self])
        return siblings
        
    @property
    def series(self):
        series = []
        m = re.match('([\w\/]*)_(\d\d\d)$', self.pg)
        if m: # this page is part of a series
            for s in self.get_subpages(self.parent, as_list=True):
                m1 = re.match('([\w\/]*)_(\d\d\d)$', s.pg)
                if m1:
                    if m1.group(1) == m.group(1):
                        series.append(s)
        series = sorted(series, key=lambda page: page.pg)
        return series
        
    def get_subpages(self, page, as_list=False, remove=[]):
        subpages = {'dirs': [], 'files': []}

        if os.path.isdir(page.fp):
            for path, dirs, files in os.walk(page.fp):
                if '_' in files:
                    files.remove('_')
                for pg in sorted(dirs):
                    if page.pg:
                        pg = page.pg + '/' + pg
                    subpages['dirs'].append(TextPage(pg))
                for pg in sorted(files):
                    if page.pg:
                        pg = page.pg + '/' + pg
                    subpages['files'].append(TextPage(pg))
                break

        for page in subpages['files']:
            if page.pg in [p.pg for p in remove]:
                subpages['files'].remove(page)
        for page in subpages['dirs']:
            if page.pg in [p.pg for p in remove]:
                subpages['dirs'].remove(page)

        if not subpages['dirs'] and not subpages['files']:
            subpages = None
        
        if subpages and as_list:
            subpages = sorted(subpages['dirs'] + subpages['files'], key=lambda page: page.pg)

        return subpages

    def save(self, content):
        fp = self.fp
        if not os.path.isfile(self.fp): # then will have to do something unusual
            if os.path.isdir(self.fp): # then save the content in a special file
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
        f.write(content.strip())
        f.close

    def delete(self):
        pass

    def __unicode__(self):
        return self.pg