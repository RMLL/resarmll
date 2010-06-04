# -*- coding: utf-8 -*-

import os, os.path, popen2, base64, tempfile
from decimal import Decimal as dec

from django.utils.translation import ugettext as _
from django.utils import translation
from django.contrib.auth.models import User

from bank import Bank
from resarmll import settings
from resarmll.resa.models import TransactionId
from resarmll.resa.orders import Order
from resarmll.utils.mail import send_email, send_admins
from resarmll.compta.models import PaymentMethod
from resarmll.compta.models import SupplierAccount

ETRANSACTIONS_CODES = {
    'XXXXXX' : u"transaction de test.",
    '00000'  : u"opération réussie.",
    '00003'  : u"erreur e-transactions.",
    '00004'  : u"numéro de porteur ou cryptogramme visuel invalide.",
    '00006'  : u"accès refusé ou site/rang/identifiant incorrect.",
    '00008'  : u"date de fin de validité incorrecte.",
    '00009'  : u"erreur vérification comportementale.",
    '00010'  : u"devise inconnue.",
    '00011'  : u"montant incorrect.",
    '00015'  : u"paiement déjà effectué.",
    '00016'  : u"inutilisé.",
    '00021'  : u"carte non autorisée.",
    # codes 001XX
    '00100' : u"transaction approuvée ou traitée avec succès.",
    '00102' : u"contacter lémetteur de carte.",
    '00103' : u"commerçant invalide.",
    '00104' : u"conserver la carte.",
    '00105' : u"ne pas honorer.",
    '00107' : u"conserver la carte, conditions spéciales.",
    '00108' : u"approuver après identification du porteur.",
    '00112' : u"transaction invalide.",
    '00113' : u"montant invalide.",
    '00114' : u"numéro de porteur invalide.",
    '00115' : u"émetteur de carte inconnu.",
    '00117' : u"annulation client.",
    '00119' : u"répéter la transaction ultérieurement.",
    '00120' : u"réponse erronée (erreur dans le domaine serveur).",
    '00124' : u"mise à jour de fichier non supportée.",
    '00125' : u"impossible de localiser lenregistrement dans le fichier.",
    '00126' : u"enregistrement dupliqué, ancien enregistrement remplacé.",
    '00127' : u"erreur en 'edit' sur champ de mise à jour fichier.",
    '00128' : u"accès interdit au fichier.",
    '00129' : u"mise à jour de fichier impossible.",
    '00130' : u"erreur de format.",
    '00131' : u"identifiant de lorganisme acquéreur inconnu.",
    '00133' : u"date de validité de la carte dépassée.",
    '00134' : u"suspicion de fraude.",
    '00138' : u"nombre dessais code confidentiel dépassé.",
    '00141' : u"carte perdue.",
    '00143' : u"carte volée.",
    '00151' : u"provision insuffisante ou crédit dépassé.",
    '00154' : u"date de validité de la carte dépassée.",
    '00155' : u"code confidentiel erroné.",
    '00156' : u"carte absente du fichier.",
    '00157' : u"transaction non permise à ce porteur.",
    '00158' : u"transaction interdite au terminal.",
    '00159' : u"suspicion de fraude.",
    '00160' : u"laccepteur de carte doit contacter lacquéreur.",
    '00161' : u"dépasse la limite du montant de retrait.",
    '00163' : u"règles de sécurité non respectées.",
    '00168' : u"réponse non parvenue ou reçue trop tard.",
    '00175' : u"nombre dessais code confidentiel dépassé.",
    '00176' : u"porteur déjà en opposition, ancien enregistrement conservé.",
    '00190' : u"arrêt momentané du système.",
    '00191' : u"émetteur de cartes inaccessible.",
    '00194' : u"demande dupliquée.",
    '00196' : u"mauvais fonctionnement du système.",
    '00197' : u"échéance de la temporisation de surveillance globale.",
    '00198' : u"serveur inaccessible (positionné par le serveur).",
    '00199' : u"incident domaine initiateur."
}

class eTransactions(Bank):
    def __init__(self, req):
        super(eTransactions, self).__init__(req, False)

    def get_paiement_method(self):
        try:
            method = PaymentMethod.objects.filter(code=settings.COMPTA_METHOD_CODE_BANK)[0]
        except:
            method = None
        return method

    def get_supplier_account(self):
        try:
            account = SupplierAccount.objects.filter(label__startswith='eTransactions')[0]
        except:
            account = None
        return account

    def put_temp_file(self, buffer):
        fd, n = tempfile.mkstemp('-eTransactions', 'resarmll-')
        f = os.fdopen(fd, 'w')
        f.write(buffer)
        f.close()
        return n

    def del_temp_file(self, file):
        try:
            os.unlink(file)
        except:
            pass

    def ssl_verify(self, key, sign, data):
        cmd = "openssl dgst -sha1 -verify \"%s\" -signature \"%s\" \"%s\"" % (key, sign, data)
        c = popen2.Popen3(cmd, 1)
        if c.wait() == 0:
            return True
        return False

    def decode(self):
        ret = False
        qs = self.env['QUERY_STRING']
        p = qs.rfind('&')
        if p >= 0:
            data = qs[:p]
            sign = base64.b64decode(self.datas.get('sign'))
            pubkey = "%s/etransactions/%s" % (os.path.dirname(__file__), 'etransactions.pem')
            fdata = self.put_temp_file(data)
            fsign = self.put_temp_file(sign)
            if os.path.isfile (pubkey) and os.path.isfile (fdata) and os.path.isfile (fsign):
                ret = self.ssl_verify(pubkey, fsign, fdata)
                self.del_temp_file(fdata)
                self.del_temp_file(fsign)
        return ret

    def fix_lang(self, lang):
        lang =lang[:2]
        if lang == 'es':
            lang = 'ESP'
        elif lang == 'en':
            lang = 'GBR'
        else:
            lang = 'FRA'
        return lang

    def process(self, cmd):
        ret = ''
        nwd = "%s/etransactions/" % (os.path.dirname(__file__))
        cmd = "cd %s && ./%s" % (nwd, cmd)
        c = popen2.Popen3(cmd, 1)
        if c.wait() == 0:
            ret = "\n".join(c.fromchild).strip()
        return ret

    def form(self, order, user, lang, ip_addr, url=None):
        args = {}
        args['PBX_SITE'] = settings.ETRANSACTIONS_SETTINGS['site']
        args['PBX_RANG'] = settings.ETRANSACTIONS_SETTINGS['rang']
        args['PBX_IDENTIFIANT'] = settings.ETRANSACTIONS_SETTINGS['identifiant']

        args['PBX_TOTAL'] = int(order.totalamount()*100)
        args['PBX_PORTEUR'] = user.email

        args['PBX_MODE'] = settings.ETRANSACTIONS_SETTINGS['mode']
        args['PBX_DEVISE'] = settings.ETRANSACTIONS_SETTINGS['devise']
        args['PBX_CMD'] = "%d-%d" % (order.id, self.get_transactionid())
        args['PBX_RETOUR'] = 'amount:M;order:R;idtrans:T;numtrans:S;autor:A;payment:P;card:C;country:Y;valid:D;ip:I;num:N;err:E;sign:K'

        args['PBX_EFFECTUE'] = "%s%s?action=return" % (url, settings.ETRANSACTIONS_SETTINGS['return_url_prefix'])
        args['PBX_REFUSE'] = "%s%s?action=reject" % (url, settings.ETRANSACTIONS_SETTINGS['return_url_prefix'])
        args['PBX_ANNULE'] = "%s%s?action=cancel" % (url, settings.ETRANSACTIONS_SETTINGS['return_url_prefix'])
        #args['PBX_ERREUR'] = ""

        # HTML4 code
        args['PBX_TXT'] = "<strong>%s</strong><br><br>%s<br><br>" % \
            (_(u"This page will automatically redirect in a few seconds..."), _(u"Click the button if the redirect fail."))
        args['PBX_WAIT'] = 0
        args['PBX_BOUTPI'] = "%s" % (_(u"Go to payment"))
        args['PBX_BKBD'] = 'white'
        args['PBX_LANGUE'] = self.fix_lang(lang)

        cmd_args = " ".join(map(lambda x: '"' + x + '=' + str(args[x]) + '"', args))
        cmd = "generate %s" % (cmd_args)

        result = self.process(cmd)
        result = result.split("\n\n\n\n")[1]
        result = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n%s" % (result)

        return result

    def getreturndatas(self):
        error = not self.decode()
        attr = {}
        for i in self.datas:
            attr[i] = self.datas[i]
        if attr.has_key('sign'):
            del attr['sign']
        return error, attr

    def getreturn(self):
        error, params = self.getreturndatas()
        canceled = rejected = accepted = order_id = None
        if params:
            if not params.has_key('action'):
                error = True
            else:
                canceled = params['action'] == 'cancel'
                rejected = params['action'] == 'reject'
                accepted = params['action'] == 'return'
            if params.has_key('order'):
                order_id = params['order'].split('-')[0]
            if params.has_key('autor') and not settings.ETRANSACTIONS_SETTINGS['testmode']:
                rejected = rejected or params['autor'] == 'XXXXXX'
        return error, canceled, rejected, accepted, order_id

    def process_order(self):
        error, params = self.getreturndatas()
        if error or not params:
            self.add_error(_(u"Error while receiving data from the bank."))
        else:
            order_id = int(params['order'].split('-')[0])
            try:
                order = Order.objects.get(id=order_id)
            except:
                order = None
            if not order:
                self.add_error(_(u"Unable to find order with id: #%d") % (order_id))
            elif order.payment_date != None:
                self.add_error(_(u"Order with id: #%d has already been paid") % (order.id))
            else:
                if params.has_key('autor') and params['autor'] == 'XXXXXX' and not settings.ETRANSACTIONS_SETTINGS['testmode']:
                    self.add_error(_(u"Fictive payment received (AUTOR=%s)") % (params['autor']))
                elif params['err'] != '00000' and ETRANSACTIONS_CODES.has_key(params['err']):
                    self.add_error(_(u"Payment error: %s") % (ETRANSACTIONS_CODES[params['err']]))
                elif params['err'] == '00000':
                    # payment ok
                    pass
                else:
                    self.add_error(_(u"Payment received with invalid error code: [%s]") % (params['err']))

                amount = dec(params['amount']) / 100
                if amount != order.totalamount():
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'amount', 'arg2': amount, 'arg3': order.totalamount()})

                if not self.has_errors():
                    try:
                        user = User.objects.get(id=order.user_id)
                    except:
                        user = None
                    if not user:
                        self.add_error(_(u"Cannot find user associated to order no: #%d") % (order.id))
                    else:
                        tax = dec(str(settings.COMPTA_BANK_FIXED_TAX)) + dec(str(settings.COMPTA_BANK_VARIABLE_TAX))*order.totalamount()
                        ## mark order as paid
                        self.order_paid(order, tax, user, 'ref: %s/%s' % (params['idtrans'], params['numtrans']))

                        ## mail info to admins
                        send_admins(
                            "ETRANSACTIONS OK - [order=%d] [amount=%.2f] [user=%s] [email=%s]" %
                                (order.id, order.totalamount(), user.id, user.email),
                                "resa/payment_ok_bank_admin_email.txt",
                                {'order_id': order.id, 'amount': order.totalamount(),
                                'env': self.env_datas(), 'dump': params})

                        # switch language before sending mail
                        translation.activate(user.get_profile().language)
                        # mail info to user
                        send_email([user.email], _(u"Bank payment - order no #%d") % order.id,
                            "resa/payment_bank_email.txt",
                            {'order_id': order.id, 'amount': order.totalamount()})

        if self.has_errors():
            send_admins(
                "ETRANSACTIONS FAIL",
                "resa/payment_fail_admin_email.txt",
                {'errors': "\n".join(self.errors),
                'env': self.env_datas(), 'dump': params})
