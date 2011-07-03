# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from resarmll import settings

_attrs = { 'class': 'text', 'size': 30}

class AccomodationSearchForm(forms.Form):
    date = forms.DateField(label=_(u"From the date:"), required=False,
    input_formats = ('%d/%m/%Y',),
    help_text=_(u"If not empty, only orders created since this date (DD/MM/YYYY) will be displayed"))
    place = forms.ChoiceField(label=_(u"Place:"), required=False,
        choices= [(key, key) for key in settings.ROOMS.keys()])