# -*- coding: utf-8 -*-
from decimal import Decimal as dec
from datetime import datetime as date

from django.utils.translation import ugettext_lazy as _

from compta.models import Operation
from resa.models import TransactionId

class Bank(object):
    def __init__(self, req, usePost=False):
        self.errors = []
        if usePost:
            self.datas = req.POST
        else:
            self.datas = req.GET
        self.env = req.META
        self.set_order()

    def set_order(self):
        self.order_id = None

    def dump_datas(self):
        ret = ''
        for d in self.datas:
            ret += "%s = [%s]\n" % (d.upper(), self.datas[d])
        return ret

    def env_datas(self):
        ret = ''
        for d in self.env:
            ret += "%s = [%s]\n" % (d.upper(), self.env[d])
        return ret

    def add_error(self, msg):
        self.errors.append(msg)

    def has_errors(self):
        return self.errors != []

    def order_paid(self, order, fee, user, data):
        curdate = date.now()
        method = self.get_paiement_method()
        order.save_paid(method, data)
        if fee > 0:
            account = self.get_supplier_account()
            if account:
                op = Operation(
                    debit=account,
                    credit=method.account,
                    label=_("Commission (fee) order #%d") % (order.id),
                    comment='',
                    amount=dec(fee),
                    payment=method,
                    date=curdate,
                    date_payment=curdate,
                    order=order,
                    user=user)
                op.save()

    def get_transactionid(self):
        t = TransactionId()
        t.save()
        return t.id
