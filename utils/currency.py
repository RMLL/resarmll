# -*- coding: utf-8 -*-

from decimal import Decimal
from resarmll import settings

def currency_alt(amount):
    ret = Decimal('0.0')
    if settings.CURRENCY_ALT:
        ret = Decimal("%.2f" % float(1.0 / settings.CURRENCY_ALT_RATE)) * Decimal("%.2f" % (amount))
        ret = ret.quantize(Decimal(10) ** -2)
    return ret
