# -*- coding: utf-8 -*-

import os, os.path, re, unicodedata, hashlib
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.contrib.auth.models import User

from bank import Bank
from resarmll import settings
from resarmll.resa.orders import Order
from resarmll.utils.mail import send_email, send_admins
from resarmll.compta.models import PaymentMethod
from resarmll.compta.models import SupplierAccount

class ogone(Bank):
    def __init__(self, req):
        super(ogone, self).__init__(req)

    def get_paiement_method(self):
        try:
            method = PaymentMethod.objects.filter(code=settings.COMPTA_METHOD_CODE_BANK)[0]
        except:
            method = None
        return method

    def get_supplier_account(self):
        try:
            account = SupplierAccount.objects.filter(label__startswith='ogone')[0]
        except:
            account = None
        return account

    def fix_lang(self, lang):
        if lang == 'en':
            lang = '%s_US' % (lang)
        else:
            lang = '%s_%s' % (lang, lang.upper())
        return lang

    def fix_encoding(self, data):
        return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')
        return s
        
    def compute_hash_sha(self, fields, key, hashtype):
        result = []
        data = {}
        for x in fields:
            data[x.upper()] = fields[x]
        keys = data.keys()
        keys.sort()
        for k in keys:
            if data[k] != '':
                result.append("%s=%s%s" % (k, data[k], key))

        rawhash = ''.join(result)
        strhash = ''
        if hashtype.lower() == 'sha512' or hashtype.lower() == 'sha-512':
            strhash = hashlib.sha512(rawhash).hexdigest()
        elif hashtype.lower() == 'sha256' or hashtype.lower() == 'sha-256':
            strhash = hashlib.sha256(rawhash).hexdigest()
        else:
            strhash = hashlib.sha1(rawhash).hexdigest()
            
        return strhash

    def form(self, order, user, lang, url=None):
        data = {}
        data['server'] = settings.OGONE_SETTINGS['server']
        data['fields'] = {}
        data['fields']['PSPID'] = settings.OGONE_SETTINGS['pspid']
        data['fields']['orderID'] = "%d-%d" % (order.id, self.get_transactionid())
        data['fields']['amount'] = int(order.totalamount()*100)
        data['fields']['currency'] = settings.OGONE_SETTINGS['currency']
        data['fields']['language'] = self.fix_lang(lang)
        data['fields']['CN'] = self.fix_encoding(user.get_full_name())
        data['fields']['EMAIL'] = user.email
        data['fields']['accepturl'] = "%s%s" % (url, settings.OGONE_SETTINGS['accepturl'])
        data['fields']['declineurl'] = "%s%s" % (url, settings.OGONE_SETTINGS['declineurl'])
        data['fields']['exceptionurl'] = "%s%s" % (url, settings.OGONE_SETTINGS['exceptionurl'])
        data['fields']['cancelurl'] = "%s%s" % (url, settings.OGONE_SETTINGS['cancelurl'])
        data['fields']['SHASign'] = self.compute_hash_sha(data['fields'], settings.OGONE_SETTINGS['secretkey-in'], settings.OGONE_SETTINGS['hashtype'])
        return data

    def getreturn(self, status):
        canceled = status == 'cancel'
        rejected = status == 'decline'
        accepted = status == 'accept'
        delayed = status == 'exception'
        if self.datas.has_key('orderID'):
            try:
                order_id = self.datas['orderID'].split('-')[0]
            except:
                order_id = 0
        return canceled, rejected, delayed, accepted, order_id
        
    def getreturndatas(self):
        data = {}
        for k,v in self.datas.iteritems():
            data[k] = v
        error = code = key = None
        
        if data.has_key('SHASIGN'):
            key = data['SHASIGN'].lower()
            del(data['SHASIGN'])
            keycompute = self.compute_hash_sha(data, settings.OGONE_SETTINGS['secretkey-out'], settings.OGONE_SETTINGS['hashtype']).lower()
            if key != keycompute:
                code = 'SHA1SIGN-INVALID'
            else:
                data['order_id'] = data['orderID'].split('-')[0]
                data['amount'] = Decimal(data['amount'])
        else:
            code = 'SHA1SIGN-NOT-FOUND'
        
        rdata = {}
        for k in data:
            rdata[k.upper()] = data[k]

        error = code != None
            
        return error, code, rdata
 
    def process_order(self):
        retcode = "OK"
        error, code, params = self.getreturndatas()
        
        if error or not params:
            self.add_error(_(u"Error while receiving data from the bank: [%s]") % (code))
        else:
            try:
                order = Order.objects.get(id=int(params['ORDER_ID']))
            except:
                order = None
            if not order:
                self.add_error(_(u"Unable to find order with id: #%d") % (int(params['ORDER_ID'])))
            elif order.payment_date != None:
                self.add_error(_(u"Order with id: #%d has already been paid") % (order.id))
            else:
                if params['STATUS'] not in ['5']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'STATUS', 'arg2': params['STATUS'], 'arg3': '5'})
                if params['ACCEPTANCE'].find('test') >= 0 and not settings.OGONE_SETTINGS['testmode']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'ACCEPTANCE', 'arg2': params['ACCEPTANCE'], 'arg3': '/\d+/'})
                if params['NCERROR'] not in ['0']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'NCERROR', 'arg2': params['NCERROR'], 'arg3': '0'})
                if params['CURRENCY'] != settings.OGONE_SETTINGS['currency']:
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'CURRENCY', 'arg2': params['CURRENCY'], 'arg3': settings.OGONE_SETTINGS['currency']})
                amount = Decimal(params['AMOUNT'])
                
                if amount != order.totalamount():
                    self.add_error(_(u"Wrong parameter '%(arg1)s': [%(arg2)s] instead of [%(arg3)s]") %
                        {'arg1': 'AMOUNT', 'arg2': amount, 'arg3': order.totalamount()})
                if not self.has_errors():
                    try:
                        user = User.objects.get(id=order.user_id)
                    except:
                        user = None
                    if not user:
                        self.add_error(_(u"Cannot find user associated to order no: #%d") % (order.id))
                    else:
                        tax = Decimal(str(settings.COMPTA_BANK_FIXED_TAX)) + Decimal(str(settings.COMPTA_BANK_VARIABLE_TAX))*order.totalamount()
                        # mark order as paid
                        self.order_paid(order, tax, user, 'ref:'+params['PAYID'])

                        # mail info to admins
                        send_admins(
                            "OGONE OK - [order=%d] [amount=%.2f] [user=%s] [email=%s]" %
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
                "OGONE FAIL",
                "resa/payment_fail_admin_email.txt",
                {'errors': "\n".join(self.errors),
                'env': self.env_datas(), 'dump': params})

        if error or self.has_errors():
            retcode = "KO"
        
        return retcode
