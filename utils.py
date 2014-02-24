from __future__ import division
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader

def render_to_response(request, template, context):
    c = RequestContext(request, context)
    t = loader.get_template(template)
    return HttpResponse(t.render(c))