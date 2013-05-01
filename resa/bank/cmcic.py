# -*- coding: utf-8 -*-

import os, os.path, datetime, re
import hmac, sha, encodings.hex_codec
from decimal import Decimal as dec

from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.contrib.auth.models import User

from bank import Bank
from resarmll import settings
from resa.orders import Order
from resautils.mail import send_email, send_admins
from compta.models import PaymentMethod
from compta.models import SupplierAccount

class cmcic(Bank):
    def __init__(self, req):
        super(cmcic, self).__init__(req, True)

    def get_paiement_method(self):
        try:
            method = PaymentMethod.objects.filter(code=settings.COMPTA_METHOD_CODE_BANK)[0]
        except:
            method = None
        return method

    def get_supplier_account(self):
        try:
            account = SupplierAccount.objects.filter(label__startswith='cmcic')[0]
        except:
            account = None
        return account

    def fix_lang(self, lang):
        lang =lang[:2].upper()
        return lang

    def compute_key(self, cle):
        hexStrKey = cle[0:38]
        hexFinal = cle[38:40] + "00";

        cca0=ord(hexFinal[0:1])
        if cca0 > 70 and cca0 < 97:
            hexStrKey += chr(cca0-23) + hexFinal[1:2]
        elif hexFinal[1:2] == "M":
            hexStrKey += hexFinal[0:1] + "0" 
        else:
            hexStrKey += hexFinal[0:2]

        return encodings.hex_codec.Codec().decode(hexStrKey)[0]

    def get_hmac_sha1(self, cle, sdata):
        return hmac.HMAC(self.compute_key(cle), sdata, sha).hexdigest()

    def valid_hmac_sha1(self, cle, sdata, mac):
        return self.get_hmac_sha1(cle, sdata).lower() == mac.lower()

    def form(self, order, user, lang, url=None):
        data = {}
        for k,v in settings.CMCIC_SETTINGS.iteritems():
            if url and str(k).startswith('url_'):
                data['cmcic_'+k] = '%s%s/%s' % (url, v, order.id)
            else:
                data['cmcic_'+k] = str(v).replace('*', '-')
        data['date'] = datetime.datetime.now().strftime('%d/%m/%Y:%H:%M:%S')
        data['lgue'] = self.fix_lang(lang)
        data['email'] = user.email
        data['reference'] = "%d-%d" % (order.id, self.get_transactionid())
        data['montant'] = "%.2f%s" % (order.totalamount(), data['cmcic_devise'])
        data['texte'] = _(u"Order no %d").replace('*', '-') % (order.id)

        smac = []
        # TPE
        smac.append(data['cmcic_tpe'])
        # date
        smac.append(data['date'])
        # montant
        smac.append(data['montant'])
        # reference
        smac.append(data['reference'])
        # texte libre
        smac.append(data['texte'])
        # version tpe
        smac.append(data['cmcic_version'])
        # langue
        smac.append(data['lgue'])
        # code société
        smac.append(data['cmcic_codesociete'])
        # email
        smac.append(data['email'])
        # nb échéances
        smac.append('')
        # date échéance 1
        smac.append('')
        # montant échéance 1
        smac.append('')
        # date échéance 2
        smac.append('')
        # montant échéance 2
        smac.append('')
        # date échéance 3
        smac.append('')
        # montant échéance 3
        smac.append('')
        # date échéance 4
        smac.append('')
        # montant échéance 4
        smac.append('')
        # options
        smac.append('')
        
        data['mac'] = self.get_hmac_sha1(data['cmcic_cle'], '*'.join(smac))
        return data

    def getreturn(self, status, order_id):
        canceled = status == None
        rejected = status == 'err'
        accepted = status == 'ok'
        delayed = False
        return canceled, rejected, delayed, accepted, order_id

    def getreturndatas(self):
        data = {}
        for k,v in self.datas.iteritems():
            data[k] = v
        error = code = None
        if data.has_key('MAC'):
            smac = []
            # TPE
            smac.append(data['TPE'])
            # date
            smac.append(data['date'])
            # montant
            smac.append(data['montant'])
            # reference
            smac.append(data['reference'])
            # texte libre
            smac.append(data['texte-libre'])
            # version tpe
            smac.append(settings.CMCIC_SETTINGS['version'])
            # code retour
            smac.append(data['code-retour'])
            # cryptogramme visuel
            smac.append(data['cvx'])
            # date de validité
            smac.append(data['vld'])
            # type de carte
            smac.append(data['brand'])
            # 3D secure ?
            smac.append(data['status3ds'])
            # Numéro autorisation
            if data.has_key('numauto'):
                smac.append(data['numauto'])
            else:
                smac.append('')
            # Motif refus (optional)
            if data.has_key('motifrefus'):
                smac.append(data['motifrefus'])
            else:
                smac.append('')
            # Code pays origine carte
            if data.has_key('originecb'):
                smac.append(data['originecb'])
            else:
                smac.append('')
            # Code BIN de la banque du porteur
            if data.has_key('bincb'):
                smac.append(data['bincb'])
            else:
                smac.append('')
            # hash du numéro de la carte
            if data.has_key('hpancb'):
                smac.append(data['hpancb'])
            else:
                smac.append('')
            # IP client
            if data.has_key('ipclient'):
                smac.append(data['ipclient'])
            else:
                smac.append('')
            # Code Pays origine transaction
            if data.has_key('originetr'):
                smac.append(data['originetr'])
            else:
                smac.append('')
            # Montant échéance (optional)
            if data.has_key('montantech'):
                smac.append(data['montantech'])
            else:
                smac.append('')
            # Quelques ajouts pour combler (pas documenté)
            smac.append('')
            smac.append('')

            if not self.valid_hmac_sha1(settings.CMCIC_SETTINGS['cle'], '*'.join(smac), data['MAC']):
                code = 'MAC-INVALID'
            else:
                data['order_id'] = data['reference'].split('-')[0]
                m = re.match(r"(?P<amount>(\d+|\d+\.\d+))(?P<devise>\w{3})?$", data['montant'])
                if m:
                    data['amount'] = m.group('amount')
                    data['devise'] = m.group('devise')
                else:
                    data['amount'] = ''
                    data['devise'] = ''
        else:
            code = 'MAC-NOT-FOUND'
        error = code != None

        return error, code, data
 
    def process_order(self):
        retcode = "version=2\ncdr=0\n"
        error, code, params = self.getreturndatas()
        if error:
            retcode = "version=2\ncdr=1\n"
        if error or not params:
            self.add_error(_(u"Error while receiving data from the bank: [%s]") % (code))
        else:
            try:
                order = Order.objects.get(id=int(params['order_id']))
            except:
                order = None
            if not order:
                self.add_error(_(u"Unable to find order with id: #%d") % (int(params['order_id'])))
            elif order.payment_date != None:
                self.add_error(_(u"Order with id: #%d has already been paid") % (order.id))
            else:
                if params['code-retour'] not in ['Annulation', 'paiement', 'payetest']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'code-retour', 'arg2': params['code-retour'], 'arg3': '\'Annulation\' or \'paiement\' or \'payetest\''})
                elif params['code-retour'] == 'payetest' and not settings.CMCIC_SETTINGS['testmode']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'code-retour', 'arg2': params['code-retour'], 'arg3': '\'Annulation\' or \'paiement\''})
                elif params['code-retour'] == 'Annulation':
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                    {'arg1': 'code-retour', 'arg2': params['code-retour'], 'arg3': '\'paiement\''})
                if params['TPE'] != settings.CMCIC_SETTINGS['tpe']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'TPE', 'arg2': params['TPE'], 'arg3': settings.CMCIC_SETTINGS['tpe']})
                if params['devise'] != settings.CMCIC_SETTINGS['devise']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'devise', 'arg2': params['devise'], 'arg3': settings.CMCIC_SETTINGS['devise']})
                amount = dec(params['amount'])
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
                        # mark order as paid
                        self.order_paid(order, tax, user, 'ref:'+params['numauto'])

                        # mail info to admins
                        send_admins(
                            "CMCIC OK - [order=%d] [amount=%.2f] [user=%s] [email=%s]" %
                                (order.id, order.totalamount(), user.id, user.email),
                                "resa/payment_ok_bank_admin_email.txt",
                                {'order': order,
                                'currency': settings.CURRENCY, 'currency_alt': settings.CURRENCY_ALT,
                                'env': self.env_datas(), 'dump': params})

                        # switch language before sending mail
                        translation.activate(user.get_profile().language)
                        # mail info to user
                        send_email([user.email], _(u"Bank payment - order no #%d") % order.id,
                            "resa/payment_bank_email.txt",
                            {'order': order, 'currency': settings.CURRENCY, 'currency_alt': settings.CURRENCY_ALT})

        if self.has_errors():
            send_admins(
                "CMCIC FAIL",
                "resa/payment_fail_admin_email.txt",
                {'errors': "\n".join(self.errors),
                'env': self.env_datas(), 'dump': params})

        return retcode

