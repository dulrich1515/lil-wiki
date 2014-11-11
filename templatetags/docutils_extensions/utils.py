from __future__ import division
from __future__ import unicode_literals

import codecs
import os

from subprocess import Popen, PIPE

from django.utils.safestring import mark_safe

from docutils.core import publish_parts
from docutils.writers import latex2e

from . import config

# System-specific commands/locations
LATEX_PATH = config.LATEX_PATH

# Directory to find working folder
TEMP_PATH = os.path.join(config.WORK_PATH, 'latex', '_')

## -------------------------------------------------------------------------- ##

class MyLatexWriter(latex2e.Writer):

    def __init__(self, initial_header_level=1):
        latex2e.Writer.__init__(self)
        if initial_header_level == 2:
            self.translator_class = MyLatexTranslator2
        elif initial_header_level == 1:
            self.translator_class = MyLatexTranslator1
        else:
            self.translator_class = MyLatexTranslator0

class MyLatexTranslator2(latex2e.LaTeXTranslator):
    section_level = 2

    def __init__(self, node):
        latex2e.LaTeXTranslator.__init__(self, node)
        self._section_number = self.section_level*[0]

class MyLatexTranslator1(latex2e.LaTeXTranslator):
    section_level = 1

    def __init__(self, node):
        latex2e.LaTeXTranslator.__init__(self, node)
        self._section_number = self.section_level*[0]

class MyLatexTranslator0(latex2e.LaTeXTranslator):
    section_level = 0

    def __init__(self, node):
        latex2e.LaTeXTranslator.__init__(self, node)
        self._section_number = self.section_level*[0]

## -------------------------------------------------------------------------- ##

def rst2html(source, initial_header_level=2, inline=False):
    if source:
        source = '.. default-role:: math\n\n' + source
        writer_name = 'html'
        
        settings_overrides = {
            'compact_lists' : True,
            'footnote_references' : 'superscript',
            'math_output' : 'MathJax',
            'stylesheet_path' : None,
            'initial_header_level' : initial_header_level,
            'doctitle_xform' : 0,
        }

        html = publish_parts(
            source=source,
            writer_name=writer_name,
            settings_overrides=settings_overrides,
        )['body'].strip()

        if inline:
            if html[:3] == '<p>' and html[-4:] == '</p>':
                html = html[3:-4]
            
        html = html.replace('...','&hellip;')
        html = html.replace('---','&mdash;')
        html = html.replace('--','&ndash;')
        # oops ... need to reverse these back
        html = html.replace('<!&ndash;','<!--')
        html = html.replace('&ndash;>','-->')
    else:
        html = ''

    return mark_safe(html)
    
def rst2latex(source, initial_header_level=-1):
    if source:
        source = '.. default-role:: math\n\n' + source
        writer = MyLatexWriter(initial_header_level)
        
        settings_overrides = {}
        latex = publish_parts(
            source=source,
            writer=writer,
            settings_overrides=settings_overrides,
        )['body']
        latex = latex.replace('-{}','-') # unwind this manipulation from docutils
    else:
        latex = ''

    return latex.strip()

## -------------------------------------------------------------------------- ##
    
def make_pdf(latex, repeat=1):

    curdir = os.getcwd()
    os.chdir(TEMP_PATH)

    basename = 'temp'

    for ext in ['idx','ind','ilg','aux','log','out','toc','tex','pdf','png']:
        try:
            os.remove('{}.{}'.format(basename, ext))
        except:
            pass

    texname = '{}.tex'.format(basename)
    idxname = '{}.idx'.format(basename)
    pdfname = '{}.pdf'.format(basename)

    texfile = codecs.open(texname, 'w', 'utf-8')
    texfile.write(latex)
    texfile.close()

    for i in range(repeat):
        cmd = os.path.join(LATEX_PATH, 'pdflatex')
        cmd = [cmd, '--interaction=nonstopmode', texname]
        p = Popen(cmd,stdout=PIPE,stderr=PIPE)
        out, err = p.communicate()

    try:
        open(idxname)
        if os.path.getsize(idxname):

            cmd = os.path.join(LATEX_PATH, 'makeindex')
            cmd = [cmd,  idxname]
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()

            cmd = os.path.join(LATEX_PATH, 'pdflatex')
            cmd = [cmd, '--interaction=nonstopmode', texname]
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
    except:
        pass

    os.chdir(curdir)

    # assert False
    
    return os.path.join(TEMP_PATH, pdfname)