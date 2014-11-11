from __future__ import division
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

from docutils.core import publish_parts

import docutils_extensions

## -------------------------------------------------------------------------- ##

register = template.Library()

@register.filter(is_safe=True)
def rst2html(source, initial_header=2, inline=False):
    return docutils_extensions.rst2html(source, initial_header, inline)

@register.filter(is_safe=True)
def rst2latex(source, initial_header=2):
    return docutils_extensions.rst2latex(source, initial_header)
