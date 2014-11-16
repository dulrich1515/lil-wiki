from django.contrib.admin import *
from django.forms import ModelForm

from models import *

class PageAdmin(ModelAdmin):
    # list_filter = []
    list_display = ['long_title', 'pg']
    # fields = []
    # readonly_fields = ['parent']
    
site.register(Page, PageAdmin)