# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from resarmll import settings
from resarmll.resa.models import Country, Badge
from resarmll.resa.widgets import TranslatedLabelField
from resarmll.resa.utils.BadgeGenerator import BadgeGenerator

GENDER_CHOICES = (('', '----------'), ('F', _('Female')), ('M', _('Male')),)

class NetworkAccess(models.Model):
    username = models.CharField(_(u"Username"), max_length=128)
    password = models.CharField(_(u"Password"), max_length=128)

    def __unicode__(self):
        return self.username

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    is_manager = models.BooleanField(_(u"Is manager"), null=False)
    gender = models.CharField(_(u"Gender"), max_length=1,
                                choices=GENDER_CHOICES, blank=True)
    address = models.TextField(_(u"Address"), blank=True)
    language =  models.CharField(_(u"Language"), max_length=2,
                                 choices=settings.LANGUAGES)
    country = models.ForeignKey(Country)
    badge_text = models.CharField(_(u"Badge text"), max_length=32, blank=True)
    fingerprint = models.CharField(_(u"PGP/GPG Fingerprint"), max_length=56, blank=True)
    notes = models.TextField(_(u"Note(s)"), blank=True)
    badge_type = models.ForeignKey(Badge)
    payment_later = models.BooleanField(_(u"Payment later"))
    network = models.ForeignKey(NetworkAccess, unique=True, null=True, blank=True)

    def save(self):
        models.Model.save(self)
        self.update_badge()

    def update_badge(self):
        b = BadgeGenerator(self.user.id, self.user.first_name+' '+self.user.last_name,
            self.badge_type.name, self.badge_type.alt_name,
            self.badge_type.color, self.badge_text, self.render_fingerprint(),
            self.user.email)
        b.create_all()

    def render_fingerprint(self):
        r = ''
        if self.fingerprint != '':
            parts = self.fingerprint.split(':')
            el = []
            for x in range(0,10):
                el.append(parts[1][x*4:(x+1)*4])
            r = parts[0] + ' - ' + ' '.join(el)
        return r

    def get_order_orga(self):
        ret = None
        notes = self.notes.strip().split("\n")
        if notes:
            for n in notes:
                if n.strip().startswith('COMMANDE_ORGA:'):
                    try:
                        ret = int(n.strip()[14:])
                    except:
                        ret = 0
        return ret

    class Meta:
        verbose_name = _(u"User profile")
        verbose_name_plural = _(u"Users Profiles")

    def get_attributes(self):
        attr = self.__dict__
        del attr['user']
        return attr
