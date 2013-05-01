# -*- coding: utf-8 -*-

import sys, os, copy
from datetime import datetime

from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict
from django.utils.dateformat import DateFormat

from resarmll import settings
from resa.orders import Order

class Room:
    def __init__(self, place):
        self.place = place

    def init_data(self):
        data = None
        if settings.ROOMS.has_key(self.place):
            data = copy.deepcopy(settings.ROOMS[self.place])
            for d in data:
                data[d] = 0
        return data

    def find_date(self, article_id):
        date = None
        if settings.ROOMS.has_key(self.place):
            data = copy.deepcopy(settings.ROOMS[self.place])
            for d in data:
                if data[d] == article_id:
                    date = d
                    break
        return date

    def set_data_from_order(self, data, order):
        for d in order.orderdetail_set.all():
            date = self.find_date(d.product.id)
            if date != None:
                data[date] += d.quantity
        return data

    def empty_data(self, data):
        ret = True
        for d in data:
            if data[d] > 0:
                ret = False
                break
        return ret

    def data_to_listing(self, results, data, user):
        c = 0
        while not self.empty_data(data):
            c += 1
            namesuffix = " (%d)" % (c) if c > 1 else ''
            name = "%-20s %-20s%4s [#%d]" % (self.prepare_name(user.last_name), self.prepare_name(user.first_name), namesuffix, user.id)
            for d in data:
                if data[d] > 0:
                    if not results.has_key(name):
                        results[name] = []
                    results[name].append(d)
                    results[name] = sorted(results[name])
                    data[d] -= 1
        return results

    def ucfirst(self, s):
        return s[0].upper() + s[1:]

    def prepare_name(self, s):
        return self.ucfirst(s.strip())

    def fancy_date(self, datelist):
        fancydates = []
        for d in datelist:
            t = datetime.strptime(d, '%Y-%m-%d')
            date = self.ucfirst(DateFormat(t).format('l j'))
            fancydates.append(date)
        return ', '.join(fancydates)

    def list(self, fromdate = None):
        results = {}
        users = User.objects.filter(order__creation_date__isnull=False).distinct()
        for u in users:
            order_staff = int(u.get_profile().order_staff) if u.get_profile().order_staff != '' else 0
            data = self.init_data()
            if fromdate:
                orders = u.order_set.filter(creation_date__gte=fromdate)
            else:
                orders = u.order_set.all()
            for o in orders:
                if u.get_profile().payment_later or order_staff > 0 or o.payment_date != None:
                    data = self.set_data_from_order(data, o)
            if data != None:
                results = self.data_to_listing(results, data, u)
        return SortedDict([(key, self.fancy_date(results[key])) for key in sorted(results.keys())])
