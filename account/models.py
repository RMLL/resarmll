# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from resarmll.resa.models import Country
from resarmll.resa.widgets import TranslatedLabelField

from resarmll import settings

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    address = models.TextField(_(u"Adresse"))
    language =  models.CharField(_(u"Langue"), max_length=2,
                                 choices=settings.LANGUAGES)
    country = models.ForeignKey(Country)
    badge_text = models.CharField(_(u"Texte du badge"),max_length=32)
    fingerprint = models.CharField(_(u"Empreinte PGP/GPG"), max_length=40)
    notes = models.TextField(_(u"Note(s)"))
    resethash = models.CharField(_(u"Reset hash"), max_length=32)

    class Meta:
        verbose_name = _(u"Profil utilisateur")
        verbose_name_plural = _(u"Profils utilisateurs")

    def get_attributes(self):
        attr = self.__dict__
        del attr['user']
        return attr