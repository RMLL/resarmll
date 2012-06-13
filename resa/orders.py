# -*- coding: utf-8 -*-
from datetime import datetime as date
from decimal import Decimal

from django.db import models
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from stock import Stock
from resarmll import settings
from resarmll.utils.currency import currency_alt

class Order(models.Model):
    user = user = models.ForeignKey(User)
    creation_date = models.DateTimeField(_(u"Creation date"))
    payment_date = models.DateTimeField(_(u"Payment date"), null=True)

    class Meta:
        verbose_name = _(u"Order")
        verbose_name_plural = _(u"Orders")

    def __unicode__(self):
        return '#'+str(self.id)+' - '+self.user.get_full_name()

    def remove(self):
        from resarmll.compta.models import Operation
        for o in self.orderdetail_set.all():
            o.remove()
        Operation.objects.filter(order=self).delete()
        self.delete()

    def save_paid(self, method, comment=None):
        from resarmll.compta.models import Operation, ClientAccount
        curdate = date.now()
        self.payment_date = curdate
        self.save()
        for o in self.orderdetail_set.all():
            o.paid()

        user_account = None
        try:
            user_account = ClientAccount.objects.filter(user=self.user)[0]
        except:
            user_account = None
        if user_account:
            if comment is not None and comment != '':
                label = "Paiement '%s' (%s) commande #%d" % (method.label, comment, self.id)
            else:
                label = "Paiement '%s' commande #%d" % (method.label, self.id)
            op = Operation(
                    debit=user_account,
                    credit=method.account,
                    label=label,
                    comment='',
                    amount=self.totalamount(),
                    payment=method,
                    date=curdate,
                    date_payment=curdate,
                    order=self,
                    user=self.user)
            op.save()

    def save_compta(self):
        from resarmll.compta.models import Operation, PaymentMethod, ClientAccount, PlanComptable
        curdate = date.now()
        user_account = None
        try:
            user_account = ClientAccount.objects.filter(user=self.user)[0]
        except:
            user_account = None

        if not user_account:
            user_account = ClientAccount(
                    label="Client: %s #%d" % (self.user.get_full_name(), self.user.id),
                    plan=PlanComptable.get_client_account(),
                    user=self.user)
            user_account.save()

        method = PaymentMethod.get_internal_method()
        for o in self.orderdetail_set.all():
            for i in range(1, o.quantity+1):
                op = Operation(
                    debit=o.product.product_account,
                    credit=user_account,
                    label=o.product.label(),
                    comment='',
                    amount=o.price,
                    payment=method,
                    date=curdate,
                    order=self,
                    user=self.user)
                op.save()

    def save_confirm(self, cart):
        self.save()
        # Adding order details
        for p in cart:
            orderdetail = OrderDetail(order=self, product_id=p.id,
                        price=p.price, quantity=p.quantity, distributed=0)
            orderdetail.save_confirm()
        self.save_compta()

    def totalamount(self):
        ret = 0
        for o in self.orderdetail_set.all():
            ret += o.totalamount()
        return ret

    def totalamount_alt(self):
        ret = 0
        for o in self.orderdetail_set.all():
            ret += o.totalamount_alt()
        return ret
        
    def hors_taxes(self):
        return Decimal("%.02f" % (float(self.totalamount()) / (1.0 + (float(settings.TVA['value']) / 100.0))))

class OrderDetail(models.Model):
    order = models.ForeignKey('Order')
    product = models.ForeignKey('Article')
    price = models.DecimalField(_(u"Price"), max_digits=10, decimal_places=2)
    quantity = models.IntegerField(_(u"Quantity"))
    distributed = models.IntegerField(_(u"Distributed quantity"))

    class Meta:
        verbose_name = _(u"Order detail")
        verbose_name_plural = _(u"Orders details")

    def __unicode__(self):
        return self.product.label()+' - '+self.order.user.get_full_name()
    
    def remove(self):
        # Updating stocks
        Stock.objects.filter(id=self.product.stock.id).update(
            quantity_ordered=F('quantity_ordered')-self.quantity)
        self.delete()

    def save_confirm(self):
        # Updating stocks
        Stock.objects.filter(id=self.product.stock.id).update(
            quantity_ordered=F('quantity_ordered')+self.quantity)
        self.save()

    def totalamount(self):
        return self.price * self.quantity

    def totalamount_alt(self):
        return currency_alt(self.totalamount())
        
    def paid(self):
        Stock.objects.filter(id=self.product.stock.id).update(
            quantity_ordered=F('quantity_ordered')-self.quantity)
        Stock.objects.filter(id=self.product.stock.id).update(
            quantity_paid=F('quantity_paid')+self.quantity)

    def quantitydiff(self):
        return range(0, self.quantity+1)
