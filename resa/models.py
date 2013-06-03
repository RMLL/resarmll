# -*- coding: utf-8 -*-
from datetime import datetime as date

from django.db import models
from django.db.models import Sum
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from resarmll import settings
from compta.models import ProductAccount
from stock import Stock
from widgets import TranslatedLabelField
from utils.BadgeGenerator import COLORS as BadgeColors
from resautils.currency import currency_alt

from django.utils.translation import get_language

BADGE_PROFILES = (('orga', _('Organization')), ('speakers', _('Speakers')), ('village', _('Village')), ('visitors', _('Visitors')),)

class LabelClass:
    """
    Classe de base pour un modèle disposant d'n libellé localisé
    Une classe surchargeant cette classe doit spécifier la classe adéquate pour
    label_class et définir le ou les libelés présents
    """
    label_class, long_label_class = None, None
    labels, long_labels = [], []

    def get_label_number(self, name, long=None):
        if not name:
            return 0
        labels = self.labels
        if long:
            labels = self.long_labels
        idx = 0
        for label_name, lbl in labels:
            idx += 1
        return idx

    def label(self, name=None, long=None, lang=None):
        """
        Affichage de base en fonction de la langue (si son identifiant est passé
        en paramètre)
        """
        label_class, labels = self.label_class, self.labels
        if long:
            label_class, labels = self.long_label_class, self.long_labels
        if not label_class:
            return u""
        label_number = self.get_label_number(name)
        if not lang or len(lang) < 2:
            lang = settings.LANGUAGES[0][0]
        default = u""
        try:
            lbl = label_class.objects.get(language=lang[:2],
                                  label_number=label_number, parent__id=self.id)
            if lbl and lbl.value:
                return lbl.value
            # langue par défaut si la langue n'est pas disponible
            lbl = label_class.objects.get(language=settings.LANGUAGES[0][0],
                                  label_number=label_number, parent__id=self.id)
            if lbl and lbl.value:
                return lbl.value
            return default
        except:
            return default

    def set_label(self, value, name=None, long=None, lang=None):
        """
        Update or create the label
        """
        label_class, labels = self.label_class, self.labels
        if long:
            label_class, labels = self.long_label_class, self.long_labels
        label_number = self.get_label_number(name)
        if not lang or len(lang) < 2:
            lang = settings.LANGUAGES[0][0]
        # try update
        try:
            lbl = label_class.objects.get(language=lang[:2],
                                  label_number=label_number, parent__id=self.id)
            lbl.value = value
            lbl.save()
        except ObjectDoesNotExist:
            label_class.objects.create(language=lang[:2], value=value,
                                         label_number=label_number, parent=self)

class BaseLabel(models.Model):
    """
    Classe abstraite de libellé
    """
    language = models.CharField(_(u"Language"), max_length=2,
                                choices=settings.LANGUAGES)
    label_number = models.IntegerField()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.value

class BaseShortLabel(BaseLabel):
    value = models.CharField(_(u"Value"), max_length=250)
    class Meta:
        abstract = True

class BaseLongLabel(BaseLabel):
    value = models.CharField(_(u"Value"), max_length=5000)
    class Meta:
        abstract = True

class ArticleLabel(BaseShortLabel):
    """
    Libellés des articles
    """
    parent = models.ForeignKey('Article')

class ArticleLongLabel(BaseLongLabel):
    """
    Libellés longs des articles
    """
    parent = models.ForeignKey('Article')

class Article(models.Model, LabelClass):
    label_class, long_label_class = ArticleLabel, ArticleLongLabel
    labels = (('lbl_simple', _(u"Simple label")),)
    long_labels = (('lbl_compose', _(u"Extended label")),)
    price = models.DecimalField(_(u"Price"), max_digits=10, decimal_places=2)
    stock = models.ForeignKey('Stock')
    order = models.PositiveIntegerField(_(u"Sorting"))
    enabled = models.BooleanField(_(u"Enabled"))
    product_account = models.ForeignKey(ProductAccount)

    class Meta:
        verbose_name = _(u"Article")

    def __unicode__(self):
        return self.label()

    def title(self):
        return self.label(None, False, get_language())

    def description(self):
        return self.label(None, True, get_language())

    def quantity(self):
        return self.stock.quantity - self.stock.quantity_ordered - self.stock.quantity_paid

    def quantity_ajusted(self):
        q = self.quantity()
        return q if q >= 0 else 0

    def count_confirmed(self):
        r = self.orderdetail_set.filter(order__payment_date__isnull=True).aggregate(Sum('quantity'))['quantity__sum']
        if r is None:
            r = 0
        return r

    def count_paid(self):
        r = self.orderdetail_set.filter(order__payment_date__isnull=False).aggregate(Sum('quantity'))['quantity__sum']
        if r is None:
            r = 0
        return r

    def count_distributed(self):
        r = self.orderdetail_set.all().aggregate(Sum('distributed'))['distributed__sum']
        if r is None:
            r = 0
        return r

    def unavailable(self):
        return self.quantity() < 1

    def price_alt(self):
        return currency_alt(self.price)

class CountryLabel(BaseShortLabel):
    """
    Libellés des pays
    """
    parent = models.ForeignKey('Country')

class Country(models.Model, LabelClass):
    label_class = CountryLabel
    labels = (('lbl_name', _(u"Name")),)
    code = models.CharField(_(u"Code"), max_length=2)
    def __unicode__(self):
        return unicode(self.code) + u' - ' + unicode(self.label(lang=get_language()))

    class Meta:
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")

class Badge(models.Model):
    name = models.CharField(_(u"Name"), max_length=64)
    alt_name = models.CharField(_(u"Alternate name"), max_length=64)
    color = models.CharField(_(u"Color"), max_length=16, choices=BadgeColors)
    default = models.BooleanField(_(u"Default"))
    section = models.CharField(_(u"Section"), max_length=32,
                choices=BADGE_PROFILES, blank=True)
    userchoice = models.BooleanField(_(u"User can choose it"))

    def __unicode__(self):
        return "%s / %s" % (self.name, self.alt_name)

    def alt_name_cleaned(self):
        return self.alt_name.replace(u'♂', u'').replace(u'♀', u'')

    class Meta:
        verbose_name = _(u"Badge")
        verbose_name_plural = _(u"Badges")

class TransactionId(models.Model):
    label = models.CharField(_(u"Transaction"), max_length=64)

    def save(self):
        self.label = "Generated: %s" % (date.now().strftime("%Y-%m-%d %H:%M:%S"))
        models.Model.save(self)

    def __unicode__(self):
        return self.label

