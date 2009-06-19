# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from resarmll.resa.views import *

urlpatterns = patterns ('',
    (r'^$', redirect_to, {'url': 'catalog/'}),

    (r'^catalog/$', redirect_to, {'url': 'list'}),
    url(r'^catalog/list/$', catalog_list, {'tmpl': 'resa/catalog_list.html'}),

    (r'^cart/$', redirect_to, {'url': 'list'}),
    url(r'^cart/list/$', cart_list, {'tmpl': 'resa/cart_list.html'}),
    url(r'^cart/(?P<action>update|invalid)/$', cart_list,
        {'tmpl': 'resa/cart_list.html'}),
    url(r'^cart/(?P<action>add|del)/(?P<product_id>\d+)$', cart_list,
        {'tmpl': 'resa/cart_list.html'}),
    url(r'^cart/(?P<action>addxjx)/(?P<product_id>\d+)$', cart_list,
        {'tmpl': 'resa/cart_addxjx.html'}),

    (r'^orders/$', redirect_to, {'url': 'list'}),
    url(r'^orders/list/$', orders_list,
        {'tmpl': 'resa/orders_list.html'}),
    url(r'^orders/validate/$', orders_list,
        {'tmpl': 'resa/orders_list.html', 'action': 'validate'}),
    url(r'^orders/details/(?P<order_id>\d+)$', orders_details,
        {'tmpl': 'resa/orders_details.html'}),
    url(r'^orders/pdf/(?P<order_id>\d+)$', orders_pdf,
        {'tmpl': 'resa/orders_pdf.xml'}),

    url(r'^manage_orders/(?P<user_id>\d+)$', manage_orders,
        {'tmpl': 'resa/manage_orders.html'}),
    url(r'^manage_orders/pdf/(?P<order_id>\d+)$', manage_orders_pdf,
        {'tmpl': 'resa/orders_pdf.xml'}),

    url(r'^manage_cart/(?P<user_id>\d+)$', manage_cart,
        {'tmpl': 'resa/manage_cart.html'}),
    url(r'^manage_cart/(?P<user_id>\d+)/(?P<action>add|update|validate|invalid)/$', manage_cart,
        {'tmpl': 'resa/manage_cart.html'}),
    url(r'^manage_cart/(?P<user_id>\d+)/(?P<action>del)/(?P<product_id>\d+)$',
        manage_cart, {'tmpl': 'resa/manage_cart.html'}),
    url(r'^manage_compta/(?P<user_id>\d+)$',
        manage_compta, {'tmpl': 'resa/manage_compta.html'}),

    url(r'^stocks/$', stocks, {'tmpl': 'resa/stocks.html'}),

    url(r'^orders/paypal/return$', orders_paypal_return,
        {'tmpl': 'resa/orders_paypal_return.html'}),
    url(r'^orders/paypal/notify$', orders_paypal_notify),

    url(r'^orders/cyberplus/return$', orders_cyberplus_return,
        {'tmpl': 'resa/orders_cyberplus_return.html'}),
    url(r'^orders/cyberplus/notify$', orders_cyberplus_notify),
)