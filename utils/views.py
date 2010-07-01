# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from resarmll import settings
from resarmll.utils.decorators import logged_in_or_global_basicauth

@logged_in_or_global_basicauth(settings.global_httpauth_username, settings.global_httpauth_password)
def sync(request):
    content = ''
    users = User.objects.all()
    if users:
        for u in users:
            datas = u.password.split('$')
            content += '"%s";"%s";"%s";"%s"\n' % (u.username, datas[1], datas[2], int(u.is_active))
    return HttpResponse(content, mimetype="text/html")

