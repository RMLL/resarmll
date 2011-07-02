# -*- coding: utf-8 -*-

import csv, time

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from resarmll import settings
from resarmll.utils.decorators import http_basicauth

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

