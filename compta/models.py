# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from resarmll.resa.orders import Order
from resarmll import settings

class PlanComptable(models.Model):
    code = models.IntegerField(_(u"Code"))
    label = models.CharField(_(u"Label"), max_length=256)

    def __unicode__(self):
        return u"%d - %s" % (self.code, self.label)

    class Meta:
        verbose_name = _(u"Accounting plan")
        verbose_name_plural = _(u"Accounting plans")

    @classmethod
    def get_client_account(_self_):
        return _self_.objects.filter(code=settings.COMPTA_PLAN_CLIENT_CODE)[0]

class PaymentMethod(models.Model):
    code = models.CharField(_(u"Code"), max_length=6)
    label = models.CharField(_(u"Label"), max_length=32)
    account = models.ForeignKey('BankAccount', null=True, blank=True)
    internal = models.BooleanField(_(u"Internal"))

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _(u"Payment method")
        verbose_name_plural = _(u"Payment methods")

    @classmethod
    def get_internal_method(_self_):
        return _self_.objects.filter(code=settings.COMPTA_METHOD_CODE_INTERNAL)[0]

class FinanceAccount(models.Model):
    label = models.CharField(_(u"Label"), max_length=256)
    plan = models.ForeignKey('PlanComptable')
    user = models.ForeignKey(User, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(FinanceAccount, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _(u"Finance account")
        verbose_name_plural = _(u"Finance accounts")

class Operation(models.Model):
    debit = models.ForeignKey('FinanceAccount', related_name='debited_account')
    credit = models.ForeignKey('FinanceAccount', related_name='credited_account')
    label = models.CharField(_(u"Label"), max_length=256)
    comment = models.TextField(_(u"Comment(s)"), blank=True)
    amount = models.DecimalField(_(u"Amount"), max_digits=10, decimal_places=2)
    payment = models.ForeignKey('PaymentMethod')
    date = models.DateField(_(u"Date"))
    date_payment = models.DateField(_(u"Payment date"), null=True)
    order = models.ForeignKey(Order)
    user = models.ForeignKey(User, null=True)

    def set_solde(self, value=0.0):
        self.solde = value
        return self.solde

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _(u"Operation")
        verbose_name_plural = _(u"Operations")


class BankAccount(FinanceAccount):
    class Meta:
        proxy = True
        verbose_name = _(u"Bank account")
        verbose_name_plural = _(u"Bank accounts")

class SupplierAccount(FinanceAccount):
    class Meta:
        proxy = True
        verbose_name = _(u"Supplier account")
        verbose_name_plural = _(u"Suppliers accounts")

class ClientAccount(FinanceAccount):
    class Meta:
        proxy = True
        verbose_name = _(u"Client account")
        verbose_name_plural = _(u"Clients accounts")


class ProductAccount(FinanceAccount):
    class Meta:
        proxy = True
        verbose_name = _(u"Product account")
        verbose_name_plural = _(u"Products accounts")

class ChargeAccount(FinanceAccount):
    class Meta:
        proxy = True
        verbose_name = _(u"Charge account")
        verbose_name_plural = _(u"Charges accounts")
