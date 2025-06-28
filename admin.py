from django.contrib.admin import *
from django.forms import ModelForm

from models import *

class PageAdmin(ModelAdmin):
    # list_filter = []
    list_display = ['pg', 'raw_title', 'update_date']
    # fields = []
    readonly_fields = ['parent', 'raw_title', 'subtitle', 'author']
    
site.register(Page, PageAdmin)
