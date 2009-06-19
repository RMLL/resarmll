#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.forms import widgets, forms, fields
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from resarmll import settings

class TranslatedLabel(models.Model):
    language = models.CharField(_(u"Language"), max_length=2,
                                choices=settings.LANGUAGES)
    value = models.CharField(max_length=250)
    def __unicode__(self):
        return u"%s (%s)" % (self.value, self.language)

class TranslatedFieldWidget(forms.TextInput):

    def render(self, name, value, attrs=None):
        '''
        Render as many field as the languages are availables
        '''
        labels = {}
        if value:
            query = TranslatedLabel.objects.extra(where=['id IN (%s)' % \
                                         ",".join([str(val) for val in value])])
            for label in list(query):
                labels[label.language] = (label.id, label.value)
        tpl = u""
        for language_id, language_label in settings.LANGUAGES:
            default = u''
            tpl += u"<p>"
            name_id = name + u"_" + language_id
            if language_id in labels:
                c_id, default= labels[language_id]
                tpl += "<input type='hidden' name='%s_id' value='%d'/>" % (
                                                                  name_id, c_id)
            tpl += widgets.TextInput().render(name_id, default)
            tpl += u" (%s)</p>" % language_label
        return mark_safe(tpl)

    def value_from_datadict(self, data, files, name):
        res = []
        for language_id, language_label in settings.LANGUAGES:
            tl = None
            name_id = name + u"_" + language_id
            c_id = data.get(name_id + '_id')
            value = data.get(name + '_' + language_id)
            if c_id:
                tl = TranslatedLabel.objects.get(id=c_id)
                tl.value = value
                tl.save()
            else:
                tl = TranslatedLabel.objects.create(language=language_id,
                                                    value=value)
            res.append(tl.id)
        return res

class TranslatedLabelField(models.ManyToManyField):
    '''
    Set the widget for the form field
    '''
    def __init__(self, **keys):
        return super(TranslatedLabelField, self).__init__(TranslatedLabel,
                                                          **keys)

    def formfield(self, **keys):
        defaults = {'widget': TranslatedFieldWidget}
        keys.update(defaults)
        return super(TranslatedLabelField, self).formfield(**keys)


