# -*- coding: utf-8 -*-

def user(request):
    ret = {}
    if hasattr(request, 'user'):
        ret['user'] = request.user
    return ret
