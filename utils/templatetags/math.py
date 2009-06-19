# -*- coding: utf-8 -*-
from django import template
register = template.Library()

@register.filter("mult")
def mult(value, arg):
    return int(value) * int(arg)

@register.filter("sub")
def sub(value, arg):
    return int(value) - int(arg)

@register.filter("div")
def div(value, arg):
    return int(value) / int(arg)

@register.filter("dadd")
def dadd(value, arg):
    return float(value) + float(arg)

@register.filter("dmult")
def dmult(value, arg):
    return float(value) * float(arg)

@register.filter("dsub")
def dsub(value, arg):
    return float(value) - float(arg)

@register.filter("ddiv")
def ddiv(value, arg):
    return float(value) / float(arg)