# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Article(models.Model):
    label = models.CharField(max_length=250)

class Language(models.Model):
    name = models.CharField(_("nom"), max_length=64)

    class Meta:
        verbose_name = _("Langue")
        verbose_name_plural = _("Langues")

    def __unicode__(self):
        return self.name
    
class Country(models.Model):
    name = models.CharField(_("nom"), max_length=64)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Pays")
        verbose_name_plural = _("Pays")

class Badge(models.Model):
    name = models.CharField(_("nom"), max_length=64)
    color = models.CharField(_("couleur"), max_length=16)
    
    def __unicode__(self):
        return self.name    

    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")
