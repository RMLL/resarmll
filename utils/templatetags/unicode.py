# -*- coding: utf-8 -*-
import unicodedata
from django import template
register = template.Library()

@register.filter('unicode_filter')
def unicode_filter(value):
    ret = ""
    for i, c in enumerate(value):
        if unicodedata.category(c) in ['Ll', 'Lu', 'Po', 'Zs']:
            ret += c
    return ret