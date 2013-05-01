# -*- coding: utf-8 -*-

import csv, time, unicodedata

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from resarmll import settings
from utils.decorators import http_basicauth

@http_basicauth(settings.global_httpauth_username, settings.global_httpauth_password)
def sync(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachement; filename=rmll_accounts_%s.csv' % (time.strftime('%Y%m%d-%H%M%S',  time.localtime()))
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
    users = User.objects.all().order_by('username')
    if users:
        for u in users:
            password_parts = u.password.split('$')
            fields = []
            fields.append(u.username.encode('utf-8'))
            fields.append(password_parts[1])
            fields.append(password_parts[2])
            fields.append(int(u.is_active))
            fields.append(u.email)
            writer.writerow(fields)
    return response

@http_basicauth(settings.global_httpauth_username, settings.global_httpauth_password)
def ksp(request):
    def unicode_translit(value):
        ret = ''
        for i, c in enumerate(value):
            if unicodedata.category(c) in ['Ll', 'Lu', 'Po', 'Zs']:
                ret += c
        return ret
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachement; filename=rmll_ksp_%s.csv' % (time.strftime('%Y%m%d-%H%M%S',  time.localtime()))
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
    users = User.objects.exclude(userprofile__fingerprint__exact = '').order_by('last_name', 'first_name')
    if users:
        for u in users:
            fields = []
            fields.append(unicode_translit(u.last_name).encode('utf-8'))
            fields.append(unicode_translit(u.first_name).encode('utf-8'))
            fields.append(u.email)
            fingerprint = u.get_profile().fingerprint
            fields.append('RSA' if fingerprint.split(':')[0].split('/')[1].upper() == 'R' else 'DSA')
            fields.append(fingerprint.split(':')[0].split('/')[0])
            fields.append(u.get_profile().render_fingerprint().split('-')[1].strip())
            writer.writerow(fields)
    return response
