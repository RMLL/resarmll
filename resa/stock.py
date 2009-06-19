# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

class Stock(models.Model):
    label = models.CharField(_(u"Label"), max_length=250)
    quantity = models.PositiveIntegerField(_(u"Quantity total"))
    quantity_ordered = models.PositiveIntegerField(_(u"Quantity ordered"))
    quantity_paid = models.PositiveIntegerField(_(u"Quantity paid"))
    order = models.PositiveIntegerField(_(u"Sorting"))

    class Meta:
        verbose_name = _(u"Stock")

    def __unicode__(self):
        return self.label

    def count_products_confirmed_related(self):
        from orders import OrderDetail
        r = OrderDetail.objects.filter(order__payment_date__isnull=True, product__stock=self).aggregate(Sum('quantity'))['quantity__sum']
        if r is None:
            r = 0
        return r

    def count_products_paid_related(self):
        from orders import OrderDetail
        r = OrderDetail.objects.filter(order__payment_date__isnull=False, product__stock=self).aggregate(Sum('quantity'))['quantity__sum']
        if r is None:
            r = 0
        return r
