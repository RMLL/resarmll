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
    url(r'^cart/(?P<action>update|add|invalid)/$', cart_list,
        {'tmpl': 'resa/cart_list.html'}),
    url(r'^cart/(?P<action>del)/(?P<product_id>\d+)$', cart_list,
        {'tmpl': 'resa/cart_list.html'}),

    (r'^orders/$', redirect_to, {'url': 'list'}),
    url(r'^orders/list/$', orders_list,
        {'tmpl': 'resa/orders_list.html'}),
    url(r'^orders/validate/$', orders_list,
        {'tmpl': 'resa/orders_list.html', 'action': 'validate'}),
    url(r'^orders/details/(?P<order_id>\d+)$', orders_details,
        {'tmpl': 'resa/orders_details.html'}),
    url(r'^orders/delete/(?P<order_id>\d+)$', orders_delete),
    url(r'^orders/pdf/(?P<order_id>\d+)$', orders_pdf,
        {'tmpl': 'resa/orders_pdf.xml'}),
    url(r'^orders/search/$', orders_search, {'tmpl': 'resa/orders_search.html'}),
    url(r'^orders/notpaid/$', orders_notpaid, {'tmpl': 'resa/orders_notpaid.html'}),
    url(r'^stats/$', stats, {'tmpl': 'resa/stats.html'}),
    url(r'^sales/$', sales, {'tmpl': 'resa/sales.html'}),
    url(r'^sales/export/(?P<product_id>\w+)$', sales_export),
    url(r'^documents/$', documents, {'tmpl': 'resa/documents.html'}),
    url(r'^documents/(?P<docid>\w+)/$', documents_view),

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

    url(r'^orders/paypal/cancel$', orders_paypal_cancel,
        {'tmpl': 'resa/orders_paypal_return.html'}),
    url(r'^orders/paypal/return$', orders_paypal_return,
        {'tmpl': 'resa/orders_paypal_return.html'}),
    url(r'^orders/paypal/notify$', orders_paypal_notify),

    url(r'^orders/cyberplus/return$', orders_bank_return,
        {'tmpl': 'resa/orders_cyberplus_return.html'}),
    url(r'^orders/cyberplus/notify$', orders_bank_notify),

    url(r'^orders/etransactions/go/(?P<order_id>\d+)$', orders_etransactions_go),
    url(r'^orders/etransactions/return$', orders_bank_return,
        {'tmpl': 'resa/orders_bank_return.html'}),
    url(r'^orders/etransactions/notify$', orders_bank_notify),

    url(r'^orders/cmcic/return(/(?P<status>ok|err))?(/(?P<order_id>\d+))?$', orders_bank_return,
        {'tmpl': 'resa/orders_bank_return.html'}),
    url(r'^orders/cmcic/notify$', orders_bank_notify),

    url(r'^orders/ogone/return(/(?P<status>accept|decline|exception|cancel))$', orders_bank_return,
    {'tmpl': 'resa/orders_bank_return.html'}),
    url(r'^orders/ogone/notify$', orders_bank_notify),
)
