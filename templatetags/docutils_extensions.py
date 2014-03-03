from __future__ import division
from __future__ import unicode_literals

import os

from docutils import nodes
from docutils.parsers import rst

from PIL import Image

from restructuredtext_tags import rst2html

from .. import config

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

def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------
    Docutils role: ``ref``
    ----------------------

    Inserts a hyperlink reference to a figure or table with a custom label.

    Example
    -------

    ::

        :ref:`image-filename.png`

    This will hyperlink to::

        .. fig:: Some image here
            :image: image-filename.png
            :scale: 0.75

    or

    ::

        :fig:`trapezoid`

    This will hyperlink to::

        .. fig:: Sample Trapezoid
            :position: side
            :label: trapezoid

            \begin{tikzpicture}
            \draw [fill=black!10] (-1,0.7) -- (1,0.7)
            -- (0.7,-0.7) -- (-0.7,-0.7) -- cycle;
            \end{tikzpicture}

    Notes
    -----

    * Works only for ``latex`` writer
    * Partial support for ``html`` writer
    """

    ref = nodes.make_id(text)
    if role in ['fig', 'tbl']:
        ref = role + ':' + ref

    t = dict()

    t['latex'] = r'\hyperref[%s]{\ref*{%s}}' % (ref, ref)
    t['html']  = r'<a href="#%s">[link]</a>' % (ref,)

    node_list = [
        nodes.raw(text=t['latex'], format='latex'),
        nodes.raw(text=t['html'], format='html')
    ]

    return node_list, []

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
            text += '<div{} class="my-docutils tbl">\n'.format(divid)
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

    Inserts a figure. 
    
    Example
    -------

    ::

        .. fig:: Some image here
            :image: image-filename.png
            :scale: 0.75

    Options
    -------

    :image:     Used to insert images. Any content will be ignored. A label
                will be inserted with the image's filename.
    :scale:     Used to scale the image.
    :label:     Used for hyperlinks references. See ``fig`` role.

    Notes
    -----

    * Argument used for figure caption (optional).
    * Label defaults to image name.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'image'     : rst.directives.unchanged,
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
    }
    has_content = True

    def run(self):

        # self.assert_has_content()
        node_list = []

        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00

        image = self.options['image']

        check_path = os.path.join(config.wiki_files_dir, image)
        check_path = os.path.normpath(check_path)

        if not os.path.exists(check_path):
            figtext = '\n<p class="warning">Missing image : {}</p>\n'.format(image)
        else:
            img_width, img_height = Image.open(check_path).size
            fig_width = int(img_width*scale*0.50)

            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
            else:
                label = nodes.make_id(image)

            figtext = '\n'
            figtext += '<div id="fig:{0}" class="my-docutils fig">\n'
            figtext = figtext.format(label)

            html_path = '/'.join([config.wiki_files_url, image])
            figtext += '<a href="{0}"><img src="{0}"></a>\n'.format(html_path)

            if self.arguments:
                figtext += rst2html(self.arguments[0])

            figtext += '</div>\n'

        text = figtext

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        return node_list

## -------------------------------------------------------------------------- ##

class plt_directive(rst.Directive):

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

class tog_directive(rst.Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}
    has_content = True

    def run(self):

        self.assert_has_content()
        node_list = []

        return node_list



