from __future__ import division
from __future__ import unicode_literals

import codecs
import hashlib
import json
import os
import posixpath
import random
import re
import shutil
import sys
import yaml

from subprocess import Popen, PIPE
from PIL import Image

from django.conf import settings
from django.utils.safestring import mark_safe

from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers import rst

# System-specific commands/locations
LATEX_PATH = settings.TEX_PATH
GS_COMMAND = settings.GS_CMD
PYTHON_CMD = settings.PYTHON_CMD
FFMPEG_CMD = settings.FFMPEG_CMD

# Directory within docutils_extensions to find working folders
WORK_PATH = ''
WORK_PATH = os.path.join(os.path.dirname(os.path.abspath( __file__ )), WORK_PATH)

# Directory within MEDIA_ROOT where wiki images are
WIKI_IMAGE_FOLDER = 'wiki'

# Directory within WIKI_IMAGE_FOLDER where system-generated images will go
SYSGEN_FOLDER = 'sysgen'

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

## -------------------------------------------------------------------------- ##

def sci_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------
    Docutils role: ``sci``
    ----------------------

    Displays scientific notation in the form :math:`a \times 10^{b}`.

    Example
    -------

   ::

        :sci:`4.5E+6`
        :sci:`450e-6`

    Notes
    -----

    * An abscissa of 1 is dropped: e.g., 1E10 => :math:`10^{10}`.
    * Upon error, the original text is returned.
    * Works only for ``latex`` and ``html`` writers ...
    """

    try:
        n = text.lower().split('e')
        a = float(n[0]) # just want to make sure it's a legit number
        a = n[0]        # make sure to take the abscissa as given
        b = int(n[1])   # must be an integer, this will drop the plus sign
        if a == '1':
            text = r'\(10^{%s}\)' % b
        else:
            text = r'\(%s \times 10^{%s}\)' % (a, b)
    except:
        pass

    node_list = [
        nodes.raw(text=text, format='latex'),
        nodes.raw(text=text, format='html'), # this pushes the work to MathJax
    ]

    return node_list, []

## -------------------------------------------------------------------------- ##

def atm_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------
    Docutils role: ``atm``
    ----------------------

    Displays pretty atomic symbols.

    Example
    -------

    ::

        :atm:`U-235`

    Notes
    -----

    * Upon error, the original text is returned.
    * Works only for ``latex`` and ``html`` writers ...
    """

    atomic_numbers = {
        'H'  :   1, # Hydrogen
        'He' :   2, # Helium
        'Li' :   3, # Lithium
        'Be' :   4, # Beryllium
        'B'  :   5, # Boron
        'C'  :   6, # Carbon
        'N'  :   7, # Nitrogen
        'O'  :   8, # Oxygen
        'F'  :   9, # Fluorine
        'Ne' :  10, # Neon
        'Na' :  11, # Sodium
        'Mg' :  12, # Magnesium
        'Al' :  13, # Aluminium
        'Si' :  14, # Silicon
        'P'  :  15, # Phosphorus
        'S'  :  16, # Sulfur
        'Cl' :  17, # Chlorine
        'Ar' :  18, # Argon
        'K'  :  19, # Potassium
        'Ca' :  20, # Calcium
        'Sc' :  21, # Scandium
        'Ti' :  22, # Titanium
        'V'  :  23, # Vanadium
        'Cr' :  24, # Chromium
        'Mn' :  25, # Manganese
        'Fe' :  26, # Iron
        'Co' :  27, # Cobalt
        'Ni' :  28, # Nickel
        'Cu' :  29, # Copper
        'Zn' :  30, # Zinc
        'Ga' :  31, # Gallium
        'Ge' :  32, # Germanium
        'As' :  33, # Arsenic
        'Se' :  34, # Selenium
        'Br' :  35, # Bromine
        'Kr' :  36, # Krypton
        'Rb' :  37, # Rubidium
        'Sr' :  38, # Strontium
        'Y'  :  39, # Yttrium
        'Zr' :  40, # Zirconium
        'Nb' :  41, # Niobium
        'Mo' :  42, # Molybdenum
        'Tc' :  43, # Technetium
        'Ru' :  44, # Ruthenium
        'Rh' :  45, # Rhodium
        'Pd' :  46, # Palladium
        'Ag' :  47, # Silver
        'Cd' :  48, # Cadmium
        'In' :  49, # Indium
        'Sn' :  50, # Tin
        'Sb' :  51, # Antimony
        'Te' :  52, # Tellurium
        'I'  :  53, # Iodine
        'Xe' :  54, # Xenon
        'Cs' :  55, # Cesium
        'Ba' :  56, # Barium
        'La' :  57, # Lanthanum
        'Ce' :  58, # Cerium
        'Pr' :  59, # Praseodymium
        'Nd' :  60, # Neodymium
        'Pm' :  61, # Promethium
        'Sm' :  62, # Samarium
        'Eu' :  63, # Europium
        'Gd' :  64, # Gadolinium
        'Tb' :  65, # Terbium
        'Dy' :  66, # Dysprosium
        'Ho' :  67, # Holmium
        'Er' :  68, # Erbium
        'Tm' :  69, # Thulium
        'Yb' :  70, # Ytterbium
        'Lu' :  71, # Lutetium
        'Hf' :  72, # Hafnium
        'Ta' :  73, # Tantalum
        'W'  :  74, # Tungsten
        'Re' :  75, # Rhenium
        'Os' :  76, # Osmium
        'Ir' :  77, # Iridium
        'Pt' :  78, # Platinum
        'Au' :  79, # Gold
        'Hg' :  80, # Mercury
        'Tl' :  81, # Thallium
        'Pb' :  82, # Lead
        'Bi' :  83, # Bismuth
        'Po' :  84, # Polonium
        'At' :  85, # Astatine
        'Rn' :  86, # Radon
        'Fr' :  87, # Francium
        'Ra' :  88, # Radium
        'Ac' :  89, # Actinium
        'Th' :  90, # Thorium
        'Pa' :  91, # Protactinium
        'U'  :  92, # Uranium
        'Np' :  93, # Neptunium
        'Pu' :  94, # Plutonium
        'Am' :  95, # Americium
        'Cm' :  96, # Curium
        'Bk' :  97, # Berkelium
        'Cf' :  98, # Californium
        'Es' :  99, # Einsteinium
        'Fm' : 100, # Fermium
        'Md' : 101, # Mendelevium
        'No' : 102, # Nobelium
        'Lr' : 103, # Lawrencium
        'Rf' : 104, # Rutherfordium
        'Db' : 105, # Dubnium
        'Sg' : 106, # Seaborgium
        'Bh' : 107, # Bohrium
        'Hs' : 108, # Hassium
        'Mt' : 109, # Meitnerium
        'Ds' : 110, # Darmstadtium
        'Rg' : 111, # Roentgenium
        'Cn' : 112, # Copernicium
        'Uut': 113, # Ununtrium
        'Fl' : 114, # Flerovium
        'Uup': 115, # Ununpentium
        'Lv' : 116, # Livermorium
        'Uus': 117, # Ununseptium
        'Uuo': 118, # Ununoctium
    }
    specials = {
        'neutron'   : ('n', 1, 0),
        'proton'    : ('p', 1, 1),
        'electron'  : ('e', 0, -1),
    }

    try:
        if text in specials:
            symbol, a, z = specials[text]
        else:
            symbol, nbr = text.split('-')
            a = int(nbr)
            z = atomic_numbers[symbol.title()]

        offset = len(str(a)) - len(str(z))
        if offset > 0:
            text = r'\({}^{%s}_{\phantom{%s}%s}\text{%s}\)' % (a, offset, z, symbol)
        elif offset < 0:
            text = r'\({}^{\phantom{%s}%s}_{%s}\text{%s}\)' % (-offset, a, z, symbol)
        else:
            text = r'\({}^{%s}_{%s}\text{%s}\)' % (a, z, symbol)
    except:
        pass

    node_list = [
        nodes.raw(text=text, format='latex'),
        nodes.raw(text=text, format='html'), # this pushes the work to MathJax
    ]

    return node_list, []

## -------------------------------------------------------------------------- ##

# def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    # """
    # ----------------------
    # Docutils role: ``ref``
    # ----------------------

    # Inserts a hyperlink reference to a figure or table with a custom label.

    # Example
    # -------

    # ::

        # :ref:`image-filename.png`

    # This will hyperlink to::

        # .. fig:: Some image here
            # :image: image-filename.png
            # :scale: 0.75

    # or

    # ::

        # :fig:`trapezoid`

    # This will hyperlink to::

        # .. fig:: Sample Trapezoid
            # :position: side
            # :label: trapezoid

            # \begin{tikzpicture}
            # \draw [fill=black!10] (-1,0.7) -- (1,0.7)
            # -- (0.7,-0.7) -- (-0.7,-0.7) -- cycle;
            # \end{tikzpicture}

    # Notes
    # -----

    # * Works only for ``latex`` writer
    # * Partial support for ``html`` writer
    # """

    # ref = nodes.make_id(text)
    # if role in ['fig', 'tbl']:
        # ref = role + ':' + ref

    # t = dict()

    # t['latex'] = r'\hyperref[%s]{\ref*{%s}}' % (ref, ref)
    # t['html']  = r'<a href="#%s">[link]</a>' % (ref,)

    # node_list = [
        # nodes.raw(text=t['latex'], format='latex'),
        # nodes.raw(text=t['html'], format='html')
    # ]

    # return node_list, []

## -------------------------------------------------------------------------- ##

def jargon_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    -------------------------
    Docutils role: ``jargon``
    -------------------------

    Creates an index entry then bolds the term in the main text.

    Example
    -------

   ::

        We use a :jargon:`vector` to capture both direction and magnitude.
        An important tool in QED is the :jargon:`Feynman diagram`.
        :jargon:`~Energy` is the ability to do work.

    Notes
    -----

    * Force a conversion to lower case in the index with a tilde ``~``.  Useful
      when the term starts a sentence.
    * Works only for ``latex`` and ``html`` writers ...
    """

    t = dict()

    if text[0] == '~':
        text = text[1:]
        t['latex'] = r'\textbf{%s}\index{%s}' % (text,text.lower())
        t['html'] = '<strong>%s</strong>' % text
    else:
        t['latex'] = r'\textbf{%s}\index{%s}' % (text,text)
        t['html'] = '<strong>%s</strong>' % text

    node_list = [
        nodes.raw(text=t['latex'], format='latex'),
        nodes.raw(text=t['html'], format='html')
    ]

    return node_list, []

## -------------------------------------------------------------------------- ##

# class toggle_directive(rst.Directive):

    # required_arguments = 0
    # optional_arguments = 1
    # final_argument_whitespace = True
    # option_spec = {
        # 'access'     : rst.directives.unchanged,
    # }
    # has_content = True

    # def run(self):

        # self.assert_has_content()
        # content = '\n'.join(self.content).replace('\\\\','\\')

        # button_text = ''
        # if self.arguments:
            # button_text = self.arguments[0]

        # if 'access' in self.options.keys():
            # access = self.options['access']

        # text = ''
        # text += '<div class="docutils-extensions toggle">\n'
        # text += '<p><input class="toggler" type="button" value="{0}"></p>\n'.format(button_text)
        # text += '<div class="togglee" style="display:none">\n'
        # text += rst2html(content) + '\n'
        # text += '</div>\n'
        # text += '</div>\n'

        # node = nodes.raw(text=text, format='html', **self.options)
        # node_list = [node]

        # return node_list

## -------------------------------------------------------------------------- ##

class tbl_directive(rst.Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'label'     : rst.directives.unchanged,
        'cols'      : rst.directives.unchanged,
    }
    has_content = True

    def run(self):

        self.assert_has_content()
        try:
            parser = rst.tableparser.GridTableParser()
            tbl = parser.parse(self.content)
        except:
            try:
                parser = rst.tableparser.SimpleTableParser()
                tbl = parser.parse(self.content)
            except:
                tbl = None

        text = ''
        if tbl:
            # parser.parse() returns a list of three items
            #
            # 1. A list of column widths
            # 2. A list of head rows
            # 3. A list of body rows

            colspecs = tbl[0]
            headrows = tbl[1] # tbl[1][i] is the ith column head
            bodyrows = tbl[2]

            # Each row contains a list of cells
            #
            # Each cell is either
            #
            # - None (for a cell unused because of another cell's span), or
            # - A tuple with four items:
            #
            #   1. The number of extra rows used by the cell in a vertical span
            #   2. The number of extra columns used by the cell in a horizontal span
            #   3. The line offset of the first line of the cell contents
            #   4. The cell contents --- a list of lines of text

            divid = ''
            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
                divid = ' id="tbl:{0}"'.format(label)

            caption = ''
            if self.arguments: # use as caption
                caption = rst2html(self.arguments[0], inline=True)

            colspec = len(tbl[0]) * 'c'
            if 'cols' in self.options.keys():
                colspec = self.options['cols']
            align = {'l': 'left', 'c': 'center', 'r': 'right'}

            text = ''
            text += '<div{} class="docutils-extensions tbl">\n'.format(divid)
            text += '<table>\n'

            for tag, rows in [('th', tbl[1]), ('td', tbl[2])]:
                for row in rows:
                    text += '<tr>\n'
                    for cell in row:
                        if cell:
                            rowspan = ''
                            if cell[0]:
                                rowspan = ' rowspan="{}"'.format(cell[0] + 1)
                            colspan = ''
                            if cell[1]:
                                colspan = ' colspan="{}"'.format(cell[1] + 1)
                            cellalign = align[colspec[row.index(cell)]]
                            celltext = rst2html('\n'.join(cell[3]), inline=True)

                            text += '<{}{}{} style="text-align:{}">\n'.format(
                                tag, rowspan, colspan, cellalign)
                            text += '{}\n'.format(celltext)
                            text += '</{}>\n'.format(tag)
                    text += '</tr>\n'
            if caption:
                text += '<caption>{}</caption>\n'.format(caption)
            text += '</table>\n'
            text += '</div>\n'

        node = nodes.raw(text=text, format='html', **self.options)
        node_list = [node]

        return node_list
## -------------------------------------------------------------------------- ##

class fig_directive(rst.Directive):

    """
    ---------------------------
    Docutils directive: ``fig``
    ---------------------------

    Inserts a figure. Creates it if necessary.

    Example
    -------

    ::

        .. fig:: Some image here
            :image: image-filename.png
            :scale: 0.75

        .. fig:: Sample Trapezoid
            :label: trapezoid

            \begin{tikzpicture}
            \draw [fill=black!10] (-1,0.7) -- (1,0.7)
            -- (0.7,-0.7) -- (-0.7,-0.7) -- cycle;
            \end{tikzpicture}

        .. fig:: Some numbers
            :template: matplotlib-pyplot

            plt.plot([1,2,3,4], [1,4,9,16], 'ro')
            plt.axis([0, 6, 0, 20])
            plt.ylabel('some numbers')
            
    Options
    -------

    :image:     Used to insert images. Any content will be ignored. A label
                will be inserted with the image's filename.
    :scale:     Used to scale the image.
    :label:     Used for hyperlinks references. See ``fig`` role.
    :template:  Used to point to proper templale when creating image. Default 
                is ``latex-preview``.

    Notes
    -----

    * Argument used for figure caption (optional).
    * If image option is used, label defaults to image name.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'image'     : rst.directives.unchanged,
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
        'template'  : rst.directives.unchanged,
    }
    has_content = True

    def run(self):

        node_list = []
        text = ''
        
        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00

        if 'image' in self.options:
            image_name = self.options['image']
            
            if '://' in image_name:
                image_path = ''
                image_url = image_name
            else:
                image_path = os.path.join(settings.MEDIA_ROOT, WIKI_IMAGE_FOLDER, image_name)
                image_url = settings.MEDIA_URL + '/'.join([WIKI_IMAGE_FOLDER, image_name])

                if not os.path.exists(image_path):
                    print '* ERROR: Missing: ' + image_path
                    text += '<p class="warning">'
                    text += 'Missing image : {}'.format(image_name)
                    text += '</p>\n'.format(image_name)
        else:
            # Unlike a normal image, our reference will come from the content...
            self.assert_has_content()
            content = '\n'.join(self.content).replace('\\\\','\\')
            image_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

            if 'template' in self.options:
                type, template = self.options['template'].split('-')
            else:
                type = 'latex'
                template = 'preview'

            if template == 'animation':
                image_name = '{}.mp4'.format(image_hash)
            else:
                image_name = '{}.png'.format(image_hash)

            image_path = os.path.join(settings.MEDIA_ROOT, WIKI_IMAGE_FOLDER, SYSGEN_FOLDER, image_name)
            image_url = settings.MEDIA_URL + '/'.join([WIKI_IMAGE_FOLDER, SYSGEN_FOLDER, image_name])
                
            if not os.path.exists(image_path):
                self.build_image(image_path, content, type, template)

            if not os.path.exists(image_path):
                print '* ERROR: Missing: ' + image_path
                text += '<div class="warning">\n'
                text += '<h4>File generation error:</h4>\n'
                text += '<pre><code>'
                text += '\n'.join(self.content) + '\n'
                text += '</code></pre>\n'
                text += '</div>\n\n'
                
        if not text:
            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
            else:
                label = nodes.make_id(image_name)

            text += '<div id="fig:{0}" class="docutils-extensions fig">\n'.format(label)

            text += '<a href="{0}">\n'.format(image_url)
            try:
                if image_path:
                    i = Image.open(image_path)
                    x = int(scale * i.size[0])
                    y = int(scale * i.size[1])
                    text += '<img width="{1}px" height="{2}"px src="{0}">\n'.format(image_url, x, y)
                else:
                    text += '<img src="{0}">\n'.format(image_url)
            except:
                ext = os.path.basename(image_path).rsplit('.')[1]
                if ext == 'mp4':
                    cmd = [FFMPEG_CMD, '-i', image_path]
                    p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                    out, err = p.communicate()
                    
                    m = re.search(r'Stream.*Video.*, (\d+)x(\d+)', err)
                    if m:
                        x = int(scale * float(m.group(1)))
                        y = int(scale * float(m.group(2)))
                        text += '<video width="{1}px" height="{2}px" controls><source src="{0}" type="video/mp4"></video>\n'.format(image_url, x, y)
                    else:
                        text += '<video controls><source src="{0}" type="video/mp4"></video>\n'.format(image_url)
            text += '</a>\n'            

            if self.arguments:
                text += rst2html(self.arguments[0])

            text += '</div>\n'            

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        return node_list
        
    def build_image(self, image_path, content, type, template):
        print '* Trying to build {}'.format(image_path)

        ext = os.path.basename(image_path).split('.')[1]
        tempfile = '.'.join(['temp', ext])
        
        try:
            # Let's remember where we came from...
            curdir = os.getcwd()
            newdir = os.path.join(WORK_PATH, type, '_')
            template_dir = os.path.normpath(os.path.join(newdir, '..'))

            # Move to proper working directory for this type of content
            os.chdir(newdir)
            print '* Moved to work directory at {}'.format(newdir)
            if os.path.isfile(tempfile):
                os.remove(tempfile)
                
            print '* Construction template = {}-{}'.format(type, template)
            if type == 'latex':
            
                # Load template to memory
                template += '.tex'
                template_path = os.path.join(template_dir, template)
                f = codecs.open(template_path, 'r', 'utf-8')
                template = f.read()
                f.close()
                print '* Template found at {}'.format(template_path)
                
                # Write the LaTeX file to the working folder
                f = codecs.open('temp.tex', 'w', 'utf-8')
                f.write(template % content)
                f.close()

                print '* Running LaTeX (temp.tex --> temp.pdf)'
                cmd = os.path.join(LATEX_PATH, 'pdflatex')
                cmd = [cmd, '--interaction=nonstopmode', 'temp.tex']
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()

                print '* Running Ghostscript (temp.pdf --> temp.png)'
                cmd = [GS_COMMAND,
                '-q',
                '-dBATCH',
                '-dNOPAUSE',
                '-sDEVICE=png16m',
                '-r600', # this number should be changed with img_scale below
                '-dTextAlphaBits=4',
                '-dGraphicsAlphaBits=4',
                '-sOutputFile=temp.png',
                'temp.pdf',
                ]
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()
                
                img_scale = 0.20 # not sure why, but this just "looks right"
                
            elif type == 'matplotlib':
                
                # Have to have some serious protection here....
                if '\nimport' in content:
                    assert False
                    
                # Load template to memory
                template += '.py'
                template_path = os.path.join(template_dir, template)
                f = codecs.open(template_path, 'r', 'utf-8')
                template = f.read()
                f.close()
                print '* Template found at {}'.format(template_path)

                # Write the matplotlib file to the working folder
                f = codecs.open('temp.py', 'w', 'utf-8')
                f.write(template % content)
                f.close()
                
                # Run matplotlib ...
                cmd = [PYTHON_CMD, 'temp.py']
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()

                img_scale = 0.70 # not sure why, but this just "looks right"
                
            else:
            
                type = None
                img_scale = 1.00

            if type: # then capture the file we just built            

                if ext == 'png':
                    print '* Resizing {}'.format(tempfile)
                    img = Image.open(tempfile)
                    x = int(img_scale * img.size[0])
                    y = int(img_scale * img.size[1])
                    img = img.resize((x, y), Image.ANTIALIAS)
                    img.save(tempfile, 'png')

                # Is the output folder even there?
                d = os.path.dirname(image_path)
                if not os.path.exists(d):
                    os.makedirs(d)

                # Finally, move the image file and clean up
                if os.path.exists(tempfile):
                    shutil.copyfile(tempfile, image_path)
                    os.remove(tempfile)

                print '* New file saved at {}'.format(image_path)
                os.chdir(curdir)
                
        except:
            pass

        return image_path
        
## -------------------------------------------------------------------------- ##

class plt_directive(rst.Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
    }
    has_content = True

    def run(self):

        node_list = []
        text = '\n'

        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00



        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        return node_list

## -------------------------------------------------------------------------- ##

class ani_directive(rst.Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}
    has_content = True

    def run(self):

        self.assert_has_content()
        node_list = []

        return node_list

## -------------------------------------------------------------------------- ##

class problem_set_directive(rst.Directive):
    """
    -----------------------------------
    Docutils directive: ``problem-set``
    -----------------------------------

    Inserts a list of word problems.

    Example
    -------

    ::

        .. problem-set:: Homework for Week 1
            :numbering: none
            :solutions: hide

            [
                {
                    "question": "What is the speed of light?",
                    "answer": ":sci:`2.998E8` m/s",
                    "solution": "Ask Google__. \n\n__ http://www.google.com"
                },
                {
                    "question": "The Great Question of Life, the Universe, and Everything.",
                    "answer": "42",
                    "solution": "What do you get if you multiply six by nine?"
                }
            ]
    
    Options
    -------

        :numbering:   [*default*, none, bullets] + [0,1,2,3,...]
        :answers:     [*show*, toggle, hide]
        :solutions:   [show, *toggle*, hide]
        :print-style: [*compact*, simple]

    Notes
    -----

    * Argument will be used as a subtitle.
    * Content required. 
    * Content may mix explicit problem dictionaries with slug references
    * Attempt to parse content as YAML then JSON. Malformed content will be returned.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'numbering'   : rst.directives.unchanged,
        'answers'     : rst.directives.unchanged,
        'solutions'   : rst.directives.unchanged,
        'print-style' : rst.directives.unchanged,
        }
    has_content = True

    def unpack(self, problem, format):
    
        question = problem.get('question','')
        answer = problem.get('answer','')
        solution = problem.get('solution','')

        if not question:
            question = 'Question not available'
        if not answer:
            answer = '[missing]'
        if not solution:
            solution = 'No solution available'
        
        if format == 'html':
            writer = rst2html
            kwargs = {'inline': True}
        # elif format == 'latex':
            # writer = rst2latex
            # kwargs = {}
        else:
            writer = None
            kwargs = {}

        def write_part(part, writer=None, kwargs={}):
            if writer:
                part = part.strip()
                if part[0] == '(': part = '\\' + part
                return writer(part, **kwargs)
            else:
                return part
            
        question = write_part(question, writer, kwargs)
        answer = write_part(answer, writer, kwargs)
        solution = write_part(solution, writer, kwargs)
            
        return question, answer, solution        
        
    def run(self):

        # Parse directive data

        self.assert_has_content()
        content = '\n'.join(self.content) # .replace('\\\\','\\')

        caption = ''
        if self.arguments: # use as caption
            caption = self.arguments[0]

        option_choices = ['default','none','bullets']
        numbering = self.options.get('numbering', option_choices[0])
        try:
            list_start = int(numbering)
        except:
            list_start = 1
            if numbering not in option_choices:
                numbering == option_choices[0]
            if numbering == 'none':
                numbering = ''
            
        option_choices = ['show','toggle','hide']
        answers = self.options.get('answers', option_choices[0])
        if answers not in option_choices:
            answers = option_choices[0]

        option_choices = ['toggle','hide','show']
        solutions = self.options.get('solutions', option_choices[0])
        if solutions not in option_choices:
            solutions = option_choices[0]

        option_choices = ['simple','compact']
        print_style = self.options.get('print-style', option_choices[0])
        if print_style not in option_choices:
            print_style = option_choices[0]

        # Begin output
            
        node_list = []

        for load in [yaml.load, json.loads]:
            try:
                problem_set = load(content)
            except:
                problem_set = []
            if problem_set: break
                
        # HTML writer specifics start...
        
        if problem_set:
            text = ''
            
            if caption:
                text += '<h4>{}</h4>\n'.format(rst2html(caption, inline=True))

            if numbering:
                if numbering == 'bullets':
                    text += '<ul class="inside-list">\n'
                else:
                    # ERROR: not sure why this markup does not seem to catch for list_start > 1 ...
                    text += '<ol start="{}" class="inside-list">\n'.format(list_start)

            n = list_start - 1
            for problem in problem_set:
                n += 1
                q, a, s = self.unpack(problem, format='html')
                toggle_id = '{:09}'.format(random.randrange(0,1e9))

                if numbering: 
                    text += '<li>\n'
                    
                text += '<p>{}</p>\n'.format(q)

                if answers == 'toggle':
                    text += '<input class="toggler" type="button" rel="a{}" value="Show Answer" onclick="buttonToggle(this,\'Show Answer\',\'Hide Answer\')">\n'.format(toggle_id)
                if solutions == 'toggle':
                    text += '<input class="toggler" type="button" rel="s{}" value="Show Solution" onclick="buttonToggle(this,\'Show Solution\',\'Hide Solution\')">\n'.format(toggle_id)
                
                if answers == 'show':
                    text += '<p id="a{}">\n<i>Answer:</i> {}\n</p>\n'.format(toggle_id, a)
                elif answers == 'toggle':
                    text += '<div id="a{}" class="togglee">\n<i>Answer:</i> {}\n</div>\n'.format(toggle_id, a)

                if solutions == 'show':
                    text += '<div id="s{}" class="solution" style="display:block">\n<p>{}</p>\n</div>\n'.format(toggle_id, s)
                elif solutions == 'toggle':
                    text += '<div id="s{}" class="solution togglee">\n<p>{}</p>\n</div>\n'.format(toggle_id, s)
                    
                if numbering: 
                    text += '</li>\n'
                
            if numbering:
                if numbering == 'bullets':
                    text += '</ul>\n'
                else:
                    text += '</ol>\n'
        else:
            text = '<pre>Malformed input\n\n{}</pre>'.format(content)

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        # # LaTeX writer specifics
        
        # text = ''
        # if problem_set:
            # if caption:
                # text += '\\subsubsection*{{{}}}\n\n'.format(rst2latex(caption))

            # n = list_start - 1
            # for problem in problem_set:
                # n += 1
                # q, a, s = self.unpack(problem, format='latex')
                
                # if print_style == 'simple':
                    # text += '\\textbf{{{0}.}}\n'.format(n)
                    # text += '\\quad \n{0}\n'.format(q)
                    # if answers in ['show','toggle']:
                        # text += '\\par \\textbf{{Answer:}} {0}\n'.format(a)
                    # if solutions in ['show','toggle']:
                        # text += '\\par \\textbf{{Solution:}}\n\\par {0}\n'.format(s)
                    # text += '\n'
                # else:
                    # text += '\\addtolength\\textwidth{-\\adjwidth}'
                    # text += '\\textbf{{{0}.}}\n'.format(n)
                    # if answers in ['show','toggle']:
                        # text += '\\marginpar{{\\footnotesize\\sf {0}}}\n'.format(a)
                    # text += '\\quad \n{0}\n'.format(q)
                    # if solutions in ['show','toggle']:
                        # text += '\\par \\textbf{{Solution:}}\n\\par {0}\n'.format(s)
                    # text += '\n'
        # else:
            # text += '\\emph{Malformed input}\n'
            # text += '\\begin{verbatim}\n'
            # text += '{}\n'.format(content)
            # text += '\\end{verbatim}\n'
            # text += '\n'
        
        # node = nodes.raw(text=text, format='latex', **self.options)
        # node_list += [node]
        
        return node_list
        
