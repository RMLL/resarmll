# -*- coding: utf-8 -*-

import sys, os.path

######################
sys.path.append('/srv/www/rmll/')
os.environ['DJANGO_SETTINGS_MODULE'] ='resarmll.settings'

from django.core.management import setup_environ
from resarmll import settings
######################

from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from resarmll.resa.models import Country
from resarmll.compta.models import PlanComptable
from django.contrib.auth.models import User
from resarmll.account.models import UserProfile
from resarmll.resa.models import Badge

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

class Users:
    @staticmethod
    def gen_badges():
        users = User.objects.all().order_by('id')
        for i in users:
            print "%d : %s" % (i.id, i.email)
            i.get_profile().update_badge()

    @staticmethod
    def import_fromcsv(fcsv, emailtmpl):
        if os.path.exists(fcsv) and os.path.exists(emailtmpl):
            handle = file(fcsv)
            for i in handle.readlines():
                values = i.strip().split(';')
                print values
                try:
                    c = Country.objects.get(code=values[6])
                except:
                    c = Country.objects.get(code='fr')

                new_user = User.objects.create_user(
                    username=values[2],
                    email=values[3]
                )
                new_user.first_name=values[1]
                new_user.last_name=values[0]
                new_user.set_password(values[4])
                new_user.save()
                badge = Badge.objects.filter(default=True)[0]
                new_profile = UserProfile(
                    user=new_user,
                    language=values[5],
                    country=c,
                    badge_type = badge,
                    badge_text=values[7],
                )
                new_profile.save()

                handle2 = file(emailtmpl)
                email = handle2.read()
                email = email.replace('###LOGIN###', values[2])
                email = email.replace('###PASSWORD###', values[4])
                send_mail("Your particpation at LSM / Votre particpation aux RMLL", email, 'reservation@rmll.info', [values[3]])
        else:
            print "Err: unable to find file '%s' or '%s'" % (fcsv, emailtmpl)

if __name__ == "__main__":
    ok = False
    args = ['badgegen', 'importusers']
    if len(sys.argv) > 1 and sys.argv[1] in args:
        ok = True
        if sys.argv[1] == 'badgegen':
            Users.gen_badges()
        elif sys.argv[1] == 'importusers' and len(sys.argv) > 3:
            Users.import_fromcsv(sys.argv[2], sys.argv[3])
        else:
            ok = False

    if not ok:
        print 'Usage: %s %s' % (sys.argv[0], "|".join(args))
