# -*- coding: utf-8 -*-
import urllib2
from decimal import Decimal as dec

from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.contrib.auth.models import User

from resarmll import settings
from bank import Bank
from resa.orders import Order
from resautils.mail import send_email, send_admins
from compta.models import PaymentMethod
from compta.models import SupplierAccount

class Paypal(Bank):
    def __init__(self, req):
        super(Paypal, self).__init__(req, True)

    def set_order(self):
        try:
            self.order_id = int(self.datas['invoice'])
        except:
            self.order_id = 0

    def confirm(self):
        qs = 'cmd=_notify-validate&'+self.datas.urlencode()
        uh = urllib2.urlopen(settings.PAYPAL_SETTINGS['url'], qs)
        check = uh.read().strip()
        uh.close()
        ret = check == 'VERIFIED'
        if not ret:
            send_admins(
                "PAYPAL FAIL - invalid code=[%s]" % (check),
                "resa/payment_fail_admin_email.txt",
                {'errors': '', 'env': self.env_datas(), 'dump': self.dump_datas()})
        return ret

    def get_paiement_method(self):
        try:
            method = PaymentMethod.objects.filter(code=settings.COMPTA_METHOD_CODE_PAYPAL)[0]
        except:
            method = None
        return method

    def get_supplier_account(self):
        try:
            account = SupplierAccount.objects.filter(label__startswith='PayPal')[0]
        except:
            account = None
        return account

    def process_order(self):
        order_id = self.order_id
        try:
            order = Order.objects.get(id=order_id)
        except:
            order = None

        if not order:
            self.add_error(_(u"Unable to find order with id: #%d") % (order_id))
        elif order.payment_date != None:
            self.add_error(_(u"Order with id: #%d has already been paid") % (order_id))
        else:
            status = self.datas.get('payment_status', '')
            email = self.datas.get('receiver_email', '')
            currency = self.datas.get('mc_currency', '')
            amount = dec(self.datas.get('mc_gross', 0))
            if status not in ['Completed', 'Pending']:
                self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                    {'arg1': 'payment_status', 'arg2': status, 'arg3': 'Completed] or [Pending'})
            if email != settings.PAYPAL_SETTINGS['id']:
                self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                    {'arg1': 'receiver_email', 'arg2': email, 'arg3': settings.PAYPAL_SETTINGS['id']})
            if currency != settings.PAYPAL_SETTINGS['currency']:
                self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                    {'arg1': 'mc_currency', 'arg2': currency, 'arg3': settings.PAYPAL_SETTINGS['currency']})
            if amount != order.totalamount():
                self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                    {'arg1': 'mc_gross', 'arg2': amount, 'arg3': order.totalamount()})

            if not self.has_errors():
                try:
                    user = User.objects.get(id=order.user_id)
                except:
                    user = None
                if not user:
                    self.add_error(_(u"Cannot find user associated to order no: #%d") % (order_id))
                else:
                    fee = dec(self.datas.get('mc_fee', 0))
                    # mark order as paid
                    self.order_paid(order, fee, user, 'ref:'+self.datas.get('txn_id', ''))

                    # mail info to admins
                    send_admins(
                        "PAYPAL OK - [order=%d] [amount=%.2f] [user=%s] [email=%s]" %
                            (order_id, order.totalamount(), user.id, user.email),
                        "resa/payment_ok_paypal_admin_email.txt",
                        {'order': order,
                        'currency': settings.CURRENCY, 'currency_alt': settings.CURRENCY_ALT,
                        'env': self.env_datas(), 'dump': self.dump_datas()})

                    # switch language before sending mail
                    translation.activate(user.get_profile().language)
                    # mail info to user
                    send_email([user.email], _(u"PayPal payment - order no #%d") % order_id,
                        "resa/payment_paypal_email.txt",
                        {'order': order, 'currency': settings.CURRENCY, 'currency_alt': settings.CURRENCY_ALT})

        if self.has_errors():
            send_admins(
                "PAYPAL FAIL",
                "resa/payment_fail_admin_email.txt",
                {'errors': "\n".join(self.errors),
                'env': self.env_datas(), 'dump': self.dump_datas()})
