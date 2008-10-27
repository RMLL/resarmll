# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from resa.models import Language, Country

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    lang = models.ForeignKey(Language)
    country = models.ForeignKey(Country)
#    badge = models.ForeignKey(Badge)
    address = models.TextField(_("adresse"))
    note = models.TextField(_("note"))
    pgpkey = models.CharField(_("Clé gpg"), max_length=128)
    resethash = models.CharField(_("Clé de remise à zéro du mot de passe"), max_length=128)
    
    class Meta:
        verbose_name = _("Profil utilisateur")
        verbose_name_plural = _("Profils utilisateurs")
