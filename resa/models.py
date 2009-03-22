# -*- coding: utf-8 -*-

from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _

from resarmll import settings
from resarmll.resa.widgets import TranslatedLabelField

class LabelClass:
    """
    Classe de base pour un modèle disposant d'un libellé localisé.
    Une classe surchargeant cette classe doit spécifier la classe adéquate pour
    label_class et définir le ou les libellés présents
    """
    label_class = None
    labels = []
    def label(self, name=None, lang=None):
        """
        Affichage de base en fonction de la langue (si son identifiant est passé
        en paramètre)
        """
        if not self.label_class:
            return u""
        label_number = 1
        if name:
            label_number = 1 + [lbl_id for lbl_id, lbl_name in self.labels]
        if not lang or len(lang) < 2:
            lang = settings.LANGUAGES[0][0]
        default = u"Pas de libellé"
        try:
            lbl = self.label_class.objects.get(language=lang[:2],
                                               label_number=0, parent=self)
            if lbl and lbl.value:
                return lbl.value
            # langue par d�faut si la langue n'est pas disponible
            lbl = self.label_class.objects.get(
               language=settings.LANGUAGES[0][0], label_number=0, parent=self)
            if lbl and lbl.value:
                return lbl.value
            return default
        except:
            return default

class BaseLabel(models.Model):
    """
    Classe abstraite de libellé
    """
    value = models.CharField(_(u"Valeur"), max_length=250)
    language = models.CharField(_(u"Langue"), max_length=2,
                                choices=settings.LANGUAGES)
    label_number = models.IntegerField()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.value

class ArticleLabel(BaseLabel):
    """
    Libellés des articles
    """
    parent = models.ForeignKey('Article')

class Article(models.Model, LabelClass):
    label_class = ArticleLabel
    labels = (('lbl_simple', _(u"Libellé simple")),
              ('lbl_compose', _(u"Libellé composé")))
    class Meta:
        verbose_name = _(u"Article")
    
    def __unicode__(self):
        return self.label()

class CountryLabel(BaseLabel):
    """
    Libellés ds pays
    """
    parent = models.ForeignKey('Country')

class Country(models.Model, LabelClass):
    label_class = CountryLabel
    labels = (('lbl_name', _(u"Nom")),)
    def __unicode__(self):
        return self.label()

    class Meta:
        verbose_name = _(u"Pays")
        verbose_name_plural = _(u"Pays")

class Badge(models.Model):
    name = models.CharField(_(u"nom"), max_length=64)
    color = models.CharField(_(u"couleur"), max_length=16)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Badge")
