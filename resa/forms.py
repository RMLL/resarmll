# -*- coding: utf-8 -*-
"""
Formulaires de l'application
"""
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from resarmll import settings
from models import Article, ArticleLabel, ArticleLongLabel, Country, CountryLabel
from resarmll.compta.models import PaymentMethod

# construction dynamique des classes de formulaires
bases = (forms.ModelForm,)

def base__init__(self, *args, **keys):
    """
    Alimentation du formulaire en modification
    """
    if 'instance' in keys and keys['instance']:
        instance = keys['instance']
        property_dct = {}
        if self.label_model:
            labels = self.label_model.objects.filter(parent=instance)
            for label in labels:
                property_dct['label_%s_%d' % (label.language,
                                              label.label_number)] = label.value
        if self.long_label_model:
            long_labels = self.long_label_model.objects.filter(parent=instance)
            for label in long_labels:
                property_dct['long_label_%s_%d' % (label.language,
                                                   label.label_number)] = label.value
        if 'initial' in keys:
            keys['initial'].update(property_dct)
        else:
            keys['initial'] = property_dct
    forms.ModelForm.__init__(self, *args, **keys)

def base_save(self, *args, **keys):
    """
    Sauvegarde du formulaire avec prise en compte du champ libellé
    """
    new_obj = forms.ModelForm.save(self, *args, **keys)
    new_obj.save()

    def save_labels(self, label_model, nb_labels, extra_id=''):
        if not label_model:
            return
        labels = label_model.objects.filter(parent=new_obj)
        old_languages = []
        for label in labels:
            if label.label_number >= nb_labels:
                label.delete()
                label.save()
                continue
            lbl = self.cleaned_data[extra_id+'label_%s_%d' % (label.language,
                                                         label.label_number)]
            old_languages.append((label.language, label.label_number))
            label.value = lbl
            label.save()
        # initialisation des labels non présents en base
        for idx in xrange(nb_labels):
            for language_id, language_label in settings.LANGUAGES:
                if (language_id, idx) not in old_languages:
                    lbl = self.cleaned_data[extra_id+'label_%s_%d' % (language_id, idx)]
                    label_model.objects.create(parent=new_obj, value=lbl,
                                        language=language_id, label_number=idx)
    save_labels(self, self.label_model, self.nb_labels)
    save_labels(self, self.long_label_model, self.nb_long_labels, 'long_')
    return new_obj

def get_attributes(base_class):
    labels, long_labels = base_class.labels, base_class.long_labels
    atts = {'nb_labels':len(labels), 'nb_long_labels':len(long_labels)}
    for idx in xrange(len(labels)):
        for language_id, language_label in settings.LANGUAGES:
            atts['label_%s_%d' % (language_id, idx)] = \
         forms.CharField(label=labels[idx][1] + u" (%s)" % language_label,
                         widget=forms.TextInput, required=False, max_length=256)
    for idx in xrange(len(long_labels)):
        for language_id, language_label in settings.LANGUAGES:
            atts['long_label_%s_%d' % (language_id, idx)] = \
         forms.CharField(label=long_labels[idx][1] + u" (%s)" % language_label,
                         widget=forms.Textarea, required=False, max_length=5000)
    atts['__init__'] = base__init__
    atts['save'] = base_save
    return atts

# formulaire des articles
atts = get_attributes(Article)
ArticleAdminFormBase = getattr(forms.ModelForm, '__metaclass__', type)\
                                ('ArticleAdminFormBase', bases, atts)
class ArticleAdminForm(ArticleAdminFormBase):
    label_model = ArticleLabel
    long_label_model = ArticleLongLabel
    class Meta:
        model = Article

# formulaire des pays
atts_country = get_attributes(Country)
CountryAdminFormBase = getattr(forms.ModelForm, '__metaclass__', type)\
                         ('CountryAdminFormBase', bases, atts_country)
class CountryAdminForm(CountryAdminFormBase):
    label_model = CountryLabel
    long_label_model = None
    class Meta:
        model = Country

class PayOrderForm(forms.Form):
    method = forms.ModelChoiceField(label=_(u"Payment Method:"),
        queryset=PaymentMethod.objects.filter(internal=False),
        widget=forms.Select(), empty_label=None)
    note = forms.CharField(label=_(u"Note:"), required=False)

class DelOrderForm(forms.Form):
    check = forms.BooleanField(label=_(u"Remove:"))
