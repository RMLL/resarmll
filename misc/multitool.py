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
from django.utils import translation
from django.contrib.auth.models import User

from resarmll.resa.models import Country
from resarmll.compta.models import PlanComptable
from resarmll.account.models import UserProfile, NetworkAccess
from resarmll.resa.models import Badge
from resarmll.utils.pdf import gen_pdf
from resarmll.resa.orders import Order

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

    @staticmethod
    def bills(folder):
        results = User.objects.filter(order__payment_date__isnull=False).order_by('id')
        fails = []
        for u in results:
            translation.activate(u.get_profile().language)
            orders = u.order_set.filter(payment_date__isnull=False).order_by('id')
            for i, o in enumerate(orders):
                bname = "%s/bill_%04d-%03d.pdf" % (folder, u.id, i+1)
                print "Writing bill for %s, #%d : %s ..." % (u.get_full_name(), u.id, bname),
                try:
                    buffer = gen_pdf('resa/orders_pdf.xml', {'user': u, 'order': o,
                        'address_lines': settings.FULL_ADDRESS.strip().split("\n"),
                        'tva': settings.TVA})
                except:
                    buffer = None
                if buffer:
                    pdffile = open(bname, 'w')
                    pdffile.write(buffer)
                    pdffile.close()
                    print 'OK'
                else:
                    print 'FAIL'
                    fails.append(u.get_full_name())
        if fails != []:
            print "Fails for: \n%s" % ("\n".join(fails))

    @staticmethod
    def bills_orga(folder):
        results = User.objects.filter(userprofile__notes__contains='COMMANDE_ORGA').order_by('id')
        fails = []
        for u in results:
            cmd = u.get_profile().get_order_orga()
            if cmd:
                translation.activate(u.get_profile().language)
                o = Order.objects.get(id=int(cmd))
                bname = "%s/bill_%04d-%03d.pdf" % (folder, u.id, 1)
                print "Writing bill for %s, #%d : %s ..." % (u.get_full_name(), u.id, bname),
                try:
                    buffer = gen_pdf('resa/orders_pdf.xml', {'user': u, 'order': o,
                        'address_lines': settings.FULL_ADDRESS.strip().split("\n"),
                        'tva': settings.TVA})
                except:
                    buffer = None
                if buffer:
                    pdffile = open(bname, 'w')
                    pdffile.write(buffer)
                    pdffile.close()
                    print 'OK'
                else:
                    print 'FAIL'
                    fails.append(u.get_full_name())
        if fails != []:
            print "Fails for: \n%s" % ("\n".join(fails))

    @staticmethod
    def mass_mail(emailtmpl):
        results = User.objects.all()
        #results = User.objects.filter(order__orderdetail__product=2).order_by('last_name')
        for u in results:
            print u.get_full_name()
            handle = file(emailtmpl)
            email = handle.read()
            handle.close()
            send_mail("Your particpation at LSM / Votre particpation aux RMLL", email, 'reservation@rmll.info', [u.email])

class WiFi:
    @staticmethod
    def import_fromcsv(fcsv):
        if os.path.exists(fcsv):
            handle = file(fcsv)
            for i in handle.readlines():
                values = i.strip().split(';')
                a = NetworkAccess(username=values[0], password=values[1])
                a.save()
        else:
            print "Err: unable to find file '%s' or '%s'" % (fcsv, emailtmpl)

if __name__ == "__main__":
    ok = False
    args = ['badgegen', 'importusers', 'importwifi', 'billsgen', 'billsgenorga', 'usermassmail']
    if len(sys.argv) > 1 and sys.argv[1] in args:
        ok = True
        if sys.argv[1] == 'badgegen':
            Users.gen_badges()
        elif sys.argv[1] == 'importusers' and len(sys.argv) > 3:
            Users.import_fromcsv(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'importwifi' and len(sys.argv) > 2:
            WiFi.import_fromcsv(sys.argv[2])
        elif sys.argv[1] == 'billsgen' and len(sys.argv) > 2:
            Users.bills(sys.argv[2])
        elif sys.argv[1] == 'billsgenorga' and len(sys.argv) > 2:
            Users.bills_orga(sys.argv[2])
        elif sys.argv[1] == 'usermassmail' and len(sys.argv) > 2:
            Users.mass_mail(sys.argv[2])
        else:
            ok = False

    if not ok:
        print 'Usage: %s %s' % (sys.argv[0], "|".join(args))
