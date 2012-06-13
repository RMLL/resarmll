# -*- coding: utf-8 -*-

import sys, os.path, tempfile, subprocess, glob

######################
sys.path.append(os.path.abspath("%s/../" % os.getcwd()))
os.environ['DJANGO_SETTINGS_MODULE'] ='resarmll.settings'

from django.core.management import setup_environ
from resarmll import settings
######################

from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.contrib.auth.models import User
from django.db.models import Q, Count

from resarmll.resa.models import Country
from resarmll.compta.models import PlanComptable
from resarmll.account.models import UserProfile, NetworkAccess
from resarmll.resa.models import Badge
from resarmll.utils.pdf import gen_pdf
from resarmll.resa.orders import Order
from resarmll.resa.utils.BadgeGenerator import BadgeGenerator


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
            print 'Err: unable to find file "%s"' % fcsv


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
            print 'Err: unable to find file "%s"' % fcsv

class Users:
    @staticmethod
    def allbadges2pdf(filepdf):
        ret = True
        print 'Generating all badges into a single file: "%s"...  ' % (filepdf),
        users_ids = []
        users = User.objects.all().order_by('id')
        if users:
            for user in users:
                users_ids.append(user.id)
        BadgeGenerator.allbadges2pdf(filepdf, users_ids)
        if os.path.exists(filepdf) and os.path.getsize(filepdf) > 0:
            print 'OK'
        else:
            print 'FAIL'
            ret = False
        return ret

    @staticmethod
    def gen_badges():
        ret = True
        fails = []
        users = User.objects.all().order_by('id')
        for i in users:
            print 'Updating badge for user #%d... ' % (i.id),
            try:
                i.get_profile().update_badge()
            except:
                fails.append('user #%d' % (i.id))
                print 'FAIL'
            else:
                print 'OK'
        if fails != []:
            print 'Fails for: \n%s' % ("\n".join(fails))
            ret = False
        return ret

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
                send_mail('Your particpation at LSM / Votre particpation aux RMLL', email, 'reservation@rmll.info', [values[3]])
        else:
            print 'Err: unable to find file "%s" or "%s"' % (fcsv, emailtmpl)

class Resa:
    @staticmethod
    def invoices(folder, paid=True):
        ret = True
        if paid:
            results = User.objects.filter(order__payment_date__isnull=False).order_by('id')
        else:
            results = User.objects.filter(order__payment_date__isnull=True).order_by('id')
        fails = []
        for u in results:
            translation.activate(u.get_profile().language)
            if paid:
                orders = u.order_set.filter(payment_date__isnull=False).order_by('id')
            else:
                orders = u.order_set.filter(payment_date__isnull=True).order_by('id')
            for i, o in enumerate(orders):
                bname = '%s/invoice_%04d-%03d.pdf' % (folder, u.id, i+1)
                print 'Writing invoice of user #%d: %s ...' % (u.id, bname),
                try:
                    buffer = gen_pdf('resa/orders_pdf.xml', {'user': u, 'order': o,
                        'address_lines': settings.FULL_ADDRESS.strip().split("\n"),
                        'tva': settings.TVA['value']})
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
            print 'Fails for: \n%s' % ("\n".join(fails))
            ret = False
        return ret

class Docs:
    @staticmethod
    def rm_recursive(folder):
        ret = True
        if os.path.isdir(folder):
            for dirname, dirnames, filenames in os.walk(folder):
                for f in filenames:
                    cfile = '%s/%s' % (folder, f)
                    try:
                        os.unlink(cfile)
                    except:
                        print 'Fail to delete file "%s" ' % (cfile)
                        ret = False
                for d in dirnames:
                    cdir = '%s/%s' % (dirname, d)
                    Docs.rm_recursive(cdir)
            try:
                os.rmdir(folder)
            except:
                print 'Fail to delete directory "%s" ' % (folder)
                ret = False
        return ret

    @staticmethod
    def generateall():
        ret = True
        # allbadges
        Users.allbadges2pdf(settings.DOCUMENTSDIR + '/allbadges.pdf')

        # invoices
        tmpdir = tempfile.mkdtemp('invoices', 'tmp', settings.TMPDIR)
        Resa.invoices(tmpdir)
        invoicespdf = glob.glob('%s/*.pdf' % tmpdir)
        if invoicespdf != []:
            cmdargs = ['pdftk']
            cmdargs += invoicespdf
            cmdargs += ['cat', 'output',  '%s/all_invoices.pdf' % settings.DOCUMENTSDIR]
            try:
                subprocess.call(cmdargs)
            except:
                print 'Unable to generate all_invoices.pdf'
        Docs.rm_recursive(tmpdir)

        # invoices not paid
        tmpdir = tempfile.mkdtemp('invoicesnotpaid', 'tmp', settings.TMPDIR)
        Resa.invoices(tmpdir, False)
        invoicespdf = glob.glob('%s/*.pdf' % tmpdir)
        if invoicespdf != []:
            cmdargs = ['pdftk']
            cmdargs += invoicespdf
            cmdargs += ['cat', 'output',  '%s/all_invoices_not_paid.pdf' % settings.DOCUMENTSDIR]
            try:
                subprocess.call(cmdargs)
            except:
                print 'Unable to generate all_invoices_not_paid.pdf'
        Docs.rm_recursive(tmpdir)

if __name__ == "__main__":
    ok = False
    args = ['all', 'badgegen', 'allbadges2pdf', 'importusers', 'invoices', 'invoices_not_paid']
    if len(sys.argv) > 1 and sys.argv[1] in args:
        ok = True
        if sys.argv[1] == 'all':
            Docs.generateall()
        elif sys.argv[1] == 'badgegen':
            Users.gen_badges()
        elif sys.argv[1] == 'allbadges2pdf' and len(sys.argv) > 2:
            Users.allbadges2pdf(sys.argv[2])
        elif sys.argv[1] == 'importusers' and len(sys.argv) > 3:
            Users.import_fromcsv(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'invoices' and len(sys.argv) > 2:
            Resa.invoices(sys.argv[2])
        elif sys.argv[1] == 'invoices_not_paid' and len(sys.argv) > 2:
            Resa.invoices(sys.argv[2], False)
        else:
            ok = False

    if not ok:
        print 'Usage: %s %s' % (sys.argv[0], "|".join(args))
