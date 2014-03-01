from __future__ import division
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

from docutils.core import publish_parts
from docutils.parsers import rst

import docutils_extensions

rst.roles.register_local_role('sci', docutils_extensions.sci_role)
rst.roles.register_local_role('atm', docutils_extensions.atm_role)
rst.roles.register_local_role('jargon', docutils_extensions.jargon_role)

# rst.roles.register_local_role('ref', docutils_extensions.ref_role)
# rst.roles.register_local_role('eqn', docutils_extensions.ref_role)
# rst.roles.register_local_role('tbl', docutils_extensions.ref_role)
# rst.roles.register_local_role('fig', docutils_extensions.ref_role)
# rst.roles.register_local_role('plt', docutils_extensions.ref_role)
# rst.roles.register_local_role('ani', docutils_extensions.ref_role)

rst.directives.register_directive('tbl', docutils_extensions.tbl_directive)
rst.directives.register_directive('fig', docutils_extensions.fig_directive)
rst.directives.register_directive('plt', docutils_extensions.plt_directive)
rst.directives.register_directive('ani', docutils_extensions.plt_directive)

# rst.directives.register_directive('tog', docutils_extensions.tog_directive)

## -------------------------------------------------------------------------- ##

register = template.Library()

@register.filter(is_safe=True)
def rst2html(source,initial_header_level=2):
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
        )['body']
        
        html = html.replace('...','&hellip;')
        html = html.replace('---','&mdash;')
        html = html.replace('--','&ndash;')
        # oops ... need to reverse these back
        html = html.replace('<!&ndash;','<!--')
        html = html.replace('&ndash;>','-->')        
    else:
        html = ''

    return mark_safe(html.strip())
