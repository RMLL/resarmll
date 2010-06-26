# -*- coding: utf-8 -*-
from django import template
register = template.Library()

@register.filter("is_staff_order")
def is_staff_order(order_id, user_obj):
    return user_obj.get_profile().is_order_orga(order_id)

