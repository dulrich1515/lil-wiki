from __future__ import division
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

from docutils.core import publish_parts

## -------------------------------------------------------------------------- ##

register = template.Library()

@register.filter(is_safe=True)
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
