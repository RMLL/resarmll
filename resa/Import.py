# -*- coding: utf-8 -*-

import sys, os.path

######################
sys.path.append('/srv/www/rmll/')
os.environ['DJANGO_SETTINGS_MODULE'] ='resarmll.settings'

from django.core.management import setup_environ
from resarmll import settings
######################

from django.core.exceptions import ObjectDoesNotExist
from resarmll.resa.models import Country
from resarmll.compta.models import PlanComptable
from django.contrib.auth.models import User

#####################
setup_environ(settings)
#####################

class CountryImport:
    @staticmethod
    def from_csv(fcsv):
        if os.path.exists(fcsv):
            handle = file(fcsv)
            for i in handle.readlines():
                lbls = {}
                code, lbls['en'], lbls['fr'], lbls['sp'] = i.split(';')
                try:
                    country = Country.objects.get(code=code)
                except ObjectDoesNotExist:
                    country = Country.objects.create(code=code)
                for lang in lbls:
                    country.set_label(value=lbls[lang], lang=lang)
        else:
            print "Err: unable to find file '%s'" % fcsv


class PlanComptableImport:
    @staticmethod
    def from_csv(fcsv):
        if os.path.exists(fcsv):
            handle = file(fcsv)
            for i in handle.readlines():
                values = i.split(';')
                p = PlanComptable(code=values[0], label=values[1])
                p.save()
        else:
            print "Err: unable to find file '%s'" % fcsv


class UserUpdate:
    @staticmethod
    def badges(only_with_fingerprint = False):
        users = User.objects.all().order_by('id')
        for i in users:
            if only_with_fingerprint and i.get_profile().fingerprint != '':
                print "%d : %s" % (i.id, i.email)
                i.get_profile().update_badge()
            elif not only_with_fingerprint:
                print "%d : %s" % (i.id, i.email)
                i.get_profile().update_badge()

if __name__ == "__main__":
    #CountryImport.from_csv(sys.argv[1])
    UserUpdate.badges(True)
