# -*- coding: utf-8 -*-
import unicodedata
from django import template
register = template.Library()

@register.filter('unicode_filter')
def unicode_filter(value):
    return unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')