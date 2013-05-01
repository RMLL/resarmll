# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from resarmll import settings
from utils.decorators import auto_render, staff_required, manager_required

from resarmll.room.room import Room
from resarmll.room.forms import AccomodationSearchForm

@login_required
@manager_required
@auto_render
def room_list(request, tmpl):
    form = None
    if settings.__dict__.has_key('ROOMS') and type(settings.ROOMS).__name__=='dict':
        if request.method == 'POST':
            form = AccomodationSearchForm(request.POST)
            if form.is_valid():
                place = form.cleaned_data['place']
                url = '/room/list/%s' % (place)
                if form.cleaned_data['date']:
                    url += '/%s' % (form.cleaned_data['date'].strftime('%Y-%m-%d'))
                return HttpResponseRedirect(url)
        else:
            form = AccomodationSearchForm(request.POST)
    return tmpl, locals()

@login_required
@manager_required
@auto_render
def room_detail(request, tmpl, printmode=False, place=None, date=None):
    printurl = fromdate = None
    if not printmode:
        if place:
            printurl = '/room/print/%s' % (place)
        if printurl and date:
            printurl = '%s/%s' % (printurl, date)
    if date:
        try:
            fromdate = datetime.strptime(date, '%Y-%m-%d')
        except:
            fromdate = None
    acclist = None
    if place != None and settings.__dict__.has_key('ROOMS') and type(settings.ROOMS).__name__=='dict':
        acclist = Room(place).list(fromdate)
    return tmpl, locals()