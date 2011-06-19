# -*- coding: utf-8 -*-
from datetime import datetime as date
from decimal import Decimal as dec

from django.db.models import Count, Sum
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from models import Article, Country
from forms import PayOrderForm, DelOrderForm
from orders import Order, OrderDetail
from cart import Cart
from stock import Stock
from bank.cyberplus import CyberPlus
from bank.etransactions import eTransactions
from bank.cmcic import cmcic
from bank.paypal import Paypal
from resarmll import settings
from resarmll.utils.decorators import auto_render, staff_required, manager_required, reception_required
from resarmll.utils.pdf import gen_pdf
from resarmll.compta.models import Operation

@login_required
@auto_render
def catalog_list(request, tmpl):
    products = Article.objects.filter(enabled=True).order_by('order')
    return tmpl, locals()

@login_required
@auto_render
def cart_list(request, tmpl, action=None, product_id=None):
    cart = Cart(request)
    msg_ok = msg_err = None
    if action == 'del':
        if cart.delete(int(product_id)):
            msg_ok = _(u"Product successfully removed from cart")
        else:
            msg_err = _(u"Error while removing product from cart")
    elif action == 'add' or action == 'update':
        statusok = False
        if len(request.POST)>0:
            statusok = True
            for k,v  in request.POST.iteritems():
                product_id = 0
                try:
                    quantity = int(v)
                except:
                    quantity = 0
                if k.startswith('product_'):
                    product_id = int(k[8:])
                    if action == 'add':
                        statusok = statusok and cart.add(product_id, quantity)
                    else:
                        statusok = statusok and cart.update(product_id, quantity)
        if statusok:
            msg_ok = _(u"Product(s) successfully added") if action == 'add' else _(u"Product(s) successfully updated")
        else:
            msg_err = _(u"Error while adding product(s)") if action == 'add' else _(u"Error while updating product(s)")
    elif action == 'invalid':
        msg_err = _(u"Unable to confirm your order, one (or more) product(s) in your cart exceed the available quantity")
    cart.save(request)
    return tmpl, {'cart': cart, 'msg_err': msg_err, 'msg_ok': msg_ok}

@login_required
@auto_render
def orders_list(request, tmpl, action=None):
    msg_ok = msg_err = None
    if action == 'validate':
        cart = Cart(request)
        if not cart.is_valid():
            return HttpResponseRedirect('/resa/cart/invalid/')
        elif not cart.empty():
            order = Order(user=request.user, creation_date=date.now())
            order.save_confirm(cart)
            cart.clear()
            cart.save(request)
            msg_ok = _(u"Order successfully confirmed")

    pending_orders = request.user.order_set.filter(payment_date__isnull=True)
    validated_orders = request.user.order_set.filter(payment_date__isnull=False)
    return tmpl, {'pending_orders': pending_orders, 'validated_orders': validated_orders,
        'msg_err': msg_err, 'msg_ok': msg_ok, 'user_obj': request.user}

@login_required
@auto_render
def orders_details(request, tmpl, order_id=0):
    try:
        order = Order.objects.get(user=request.user, id=int(order_id))
    except:
        order = None

    # only allowed to see its own orders
    if order and order.user.id != request.user.id:
        order = None

    protocol = request.is_secure() and 'https' or 'http'
    url = "%s://%s" % (protocol, request.get_host())
    paypal_settings = settings.PAYPAL_SETTINGS
    treasurer_address = settings.TREASURER_ADDRESS
    treasurer_name = settings.TREASURER_NAME
    treasurer_email = settings.TREASURER_EMAIL
    check_payable_to = settings.CHECK_PAYABLE_TO
    iban = settings.BANK_IBAN
    bic = settings.BANK_BIC
    ip_addr = request.META['REMOTE_ADDR']
    if order:
        if settings.BANK_DRIVER.upper() == 'CYBERPLUS':
            bp_tmpl = 'resa/orders_details_cyberplus.html'
            bp = CyberPlus(request)
            bp_err, bp_code, bp_form = bp.form(order, request.user, request.LANGUAGE_CODE, ip_addr, url)
        elif settings.BANK_DRIVER.upper() == 'ETRANSACTIONS':
            bp_tmpl = 'resa/orders_details_etransactions.html'
        elif settings.BANK_DRIVER.upper() == 'CMCIC':
            bp_tmpl = 'resa/orders_details_cmcic.html'
            bp = cmcic(request)
            bp_form = bp.form(order, request.user, request.LANGUAGE_CODE, url)

    return tmpl, locals()

@login_required
def orders_pdf(request, tmpl, order_id=0):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except:
        order = None

    # only allowed to see its own orders
    if not order or (order and order.user.id != request.user.id):
        return HttpResponseRedirect('/resa/orders/details/%d' % order_id)

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=billing_order_%d.pdf' % order_id
    response.write(gen_pdf(tmpl, {'user': request.user, 'order': order,
                        'address_lines': settings.FULL_ADDRESS.strip().split("\n"),
                        'tva': settings.TVA}))
    return response

@login_required
@manager_required
@auto_render
def orders_search(request, tmpl):
    noresults = False
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=int(request.POST['pattern']))
        except:
            order = None
        if order:
            return HttpResponseRedirect('/resa/manage_orders/'+str(order.user_id))
        else:
            noresults = True
    return tmpl, locals()

@login_required
@staff_required
@auto_render
def orders_notpaid(request, tmpl):
    results = User.objects.filter(order__payment_date__isnull=True).annotate(num_orders=Count('order')).filter(num_orders__gt=0).order_by('last_name')
    results_orga = [u for u in results if u.get_profile().badge_type.section == 'orga']
    results_speakers = [u for u in results if u.get_profile().badge_type.section == 'speakers']
    results_others = [u for u in results if u.get_profile().badge_type.section != 'orga' and u.get_profile().badge_type.section != 'speakers']
    return tmpl, locals()

@login_required
@manager_required
@auto_render
def manage_orders(request, tmpl, user_id=None):
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None

    params = {'user_obj': user, 'msg_ok': None, 'msg_err': None}
    if user:
        form = form_del = None
        if request.method == 'POST':
            try:
                order = Order.objects.get(id=int(request.POST['order_id']))
            except:
                order = None

            # mark order as paid
            form = PayOrderForm(request.POST)
            if form.is_valid() and order:
                    order.save_paid(form.cleaned_data['method'], form.cleaned_data['note'])
                    params['msg_ok'] = _(u"Order sucessfully marked as paid")
                    form = None

            # remove order definitly
            form_del = DelOrderForm(request.POST)
            if form_del.is_valid() and order:
                    order.remove()
                    params['msg_ok'] = _(u"Order sucessfully removed")
                    form_del = None

            # change quantities distributed
            if request.POST.get('distribution') == '1' and order:
                for k,v  in request.POST.iteritems():
                    if k.startswith('orderdetail_'):
                        orderdetail_id = int(k[12:])
                        od = OrderDetail.objects.get(id=orderdetail_id)
                        od.distributed = int(request.POST[k])
                        od.save()
                params['msg_ok'] = _(u"Order sucessfully updated")

        if not form:
            form = PayOrderForm()
        if not form_del:
            form_del = DelOrderForm()

        params['form'] = form
        params['form_del'] = form_del
        params['pending_orders'] = user.order_set.filter(payment_date__isnull=True)
        params['validated_orders'] = user.order_set.filter(payment_date__isnull=False)
    return tmpl, params

@login_required
@manager_required
def manage_orders_pdf(request, tmpl, order_id=0):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except:
        order = None

    if not order:
        return HttpResponseRedirect('/')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=billing_order_%d.pdf' % order_id
    response.write(gen_pdf(tmpl, {'user': order.user, 'order': order,
                        'address_lines': settings.FULL_ADDRESS.strip().split("\n"),
                        'tva': settings.TVA}))
    return response

@login_required
@manager_required
@auto_render
def manage_cart(request, tmpl, user_id=None, action=None, product_id=None):
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None
    msg_ok = msg_err = products = cart = None
    products = None
    if user:
        cart = Cart(request, user.id)
        if request.user.is_staff:
            products = Article.objects.all().order_by('order')
        else:
            products = Article.objects.filter(enabled=True).order_by('order')
        if action == 'add':
            product_id = int(request.POST.get('cart_add'))
            if cart.add(product_id, 1):
                msg_ok = _(u"Product successfully added to cart")
            else:
                msg_err = _(u"Error while adding product to cart")
        elif action == 'del':
            if cart.delete(int(product_id)):
                msg_ok = _(u"Product successfully removed from cart")
            else:
                msg_err = _(u"Error while removing product from cart")
        elif action == 'update':
            update = True
            for k,v  in request.POST.iteritems():
                product_id = 0
                try:
                    quantity = int(v)
                except:
                    quantity = 0
                if k.startswith('product_'):
                    product_id = int(k[8:])
                    update = update and cart.update(product_id, quantity)
            if update:
                msg_ok = _(u"Product(s) successfully updated")
            else:
                msg_err = _(u"Error while updating product(s)")
        elif action == 'validate':
            valid = cart.is_valid()
            if not valid and request.user.is_staff:
                valid = request.POST.get('force') == '1'
            if not valid:
                msg_err = _(u"Unable to confirm this order, one (or more) product(s) in the cart exceed the available quantity")
            else:
                order = Order(user=user, creation_date=date.now())
                order.save_confirm(cart)
                cart.clear()
                msg_ok = _(u"Order successfully confirmed")
        cart.save(request)
    return tmpl, {'user_obj': user, 'products': products, 'cart': cart,
                    'msg_err': msg_err, 'msg_ok': msg_ok, 'is_admin': request.user.is_staff}

@login_required
@staff_required
@auto_render
def manage_compta(request, tmpl, user_id=None):
    operations = user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            user = None
    if user:
        operations = Operation.objects.filter(user=user).order_by('order', 'id')
        solde = dec(0)
        for i,op in enumerate(operations):
            if op.date_payment:
                solde -= op.amount
            else:
                solde += op.amount
            operations[i].set_solde(solde)
    return tmpl, {'user_obj': user, 'operations': operations}

@login_required
@staff_required
@auto_render
def stats(request, tmpl):
    stats_countries = Country.objects.annotate(num_users=Count('userprofile')).filter(num_users__gt=0).order_by('-num_users')
    return tmpl, locals()

@login_required
@staff_required
@auto_render
def stocks(request, tmpl):
    stocks = Stock.objects.all().order_by('order')
    return tmpl, locals()

@login_required
@staff_required
@auto_render
def sales(request, tmpl):
    products = Article.objects.order_by('order')
    results_paid = results_notpaid = product = None
    if request.method == 'POST':
        try:
            product = Article.objects.get(id=int(request.POST['product']))
        except:
            product = None
        if product:
            results_paid = User.objects.filter(order__payment_date__isnull=False,order__orderdetail__product=product).annotate(num_products=Sum('order__orderdetail__quantity')).filter().order_by('last_name')
            results_notpaid = User.objects.filter(order__payment_date__isnull=True,order__orderdetail__product=product).annotate(num_products=Sum('order__orderdetail__quantity')).filter().order_by('last_name')
    return tmpl, locals()

@login_required
@auto_render
def orders_paypal_cancel(request, tmpl):
    msg_warn = _(u"Your payment has been canceled, you could resume it later.")
    return tmpl, locals()

@login_required
@auto_render
def orders_paypal_return(request, tmpl):
    msg_err = msg_ok = None
    try:
        order = Order.objects.get(id=int(request.POST.get('invoice')))
    except:
        order = None
    if order:
        if order.user.id != request.user.id:
            msg_err = _(u"This order is not yours.")
        else:
            if request.POST.get('payment_status') not in ['Completed', 'Pending']:
                msg_err = _(u"It seems that PayPal did not accept your payment (Code: %s).") % (request.POST.get('payment_status'))
            else:
                msg_ok = _(u"Your payment has been confirmed by PayPal, you should receive a notification by email in a few minutes.")
    else:
        msg_err = _(u"Unable to find the order related to this payment.")
    return tmpl, locals()

@auto_render
def orders_paypal_notify(request, order_id=0):
    p = Paypal(request)
    r = 'OK'
    if p.confirm():
        p.process_order()
    else:
        r = 'KO'
    return HttpResponse(r, mimetype="text/html")

@login_required
@auto_render
def orders_bank_return(request, tmpl, status=None, order_id=None):
    msg_err = msg_ok = msg_warn = None
    if settings.BANK_DRIVER.upper() == 'CYBERPLUS':
        bp = CyberPlus(request)
        error, code, canceled, rejected, accepted, order_id = bp.getreturn()
    elif settings.BANK_DRIVER.upper() == 'ETRANSACTIONS':
        bp = eTransactions(request)
        error, canceled, rejected, accepted, order_id = bp.getreturn()
    elif settings.BANK_DRIVER.upper() == 'CMCIC':
        bp = cmcic(request)
        canceled, rejected, accepted, order_id = bp.getreturn(status, order_id)

    if canceled:
        msg_warn = _(u"Your payment has been canceled, you could resume it later.")
    elif rejected:
        msg_err = _(u"Your payment has been rejected by the bank, you should retry in few days or try another payment method.")
    elif accepted:
        try:
            order = Order.objects.get(id=int(order_id))
        except:
            order = None
        if order:
            if order.user.id != request.user.id:
                msg_err = _(u"This order is not yours.")
            else:
                msg_ok = _(u"Your payment has been confirmed by the bank, you should receive a notification by email in a few minutes.")
        else:
            msg_err = _(u"Unable to find the order related to this payment.")
    else:
        msg_err = _(u"Your payment has failed, you should retry in few days or try another payment method.")
    return tmpl, locals()

def orders_bank_notify(request):
    r = 'OK'
    if settings.BANK_DRIVER.upper() == 'CYBERPLUS':
        bp = CyberPlus(request)
        if request.method == 'POST':
            bp.process_order()
        else:
            r = 'KO'
    elif settings.BANK_DRIVER.upper() == 'ETRANSACTIONS':
        bp = eTransactions(request)
        bp.process_order()
    elif settings.BANK_DRIVER.upper() == 'CMCIC':
        bp = cmcic(request)
        r = bp.process_order()

    return HttpResponse(r, mimetype="text/html")

def orders_etransactions_go(request, order_id=0):
    try:
        order = Order.objects.get(user=request.user, id=int(order_id))
    except:
        order = None

    # only allowed to see its own orders
    if not order or (order and order.user.id != request.user.id):
        return HttpResponseRedirect("/resa/orders/details/%d" % (int(order_id)))

    protocol = request.is_secure() and 'https' or 'http'
    url = "%s://%s" % (protocol, request.get_host())
    ip_addr = request.META['REMOTE_ADDR']

    bp = eTransactions(request)
    r = HttpResponse(mimetype='text/html')
    r['Cache-Control'] = 'no-cache, no-store'
    r['Pragma'] = 'no-cache'
    r.write(bp.form(order, request.user, request.LANGUAGE_CODE, ip_addr, url))

    return r
