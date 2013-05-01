# -*- coding: utf-8 -*-
import sys, os.path

from resa.models import Country
from compta.models import PlanComptable

class CountryImport:
    @staticmethod
    def from_csv(fcsv):
        if os.path.exists(fcsv):
            handle = file(fcsv)
            for i in handle.readlines():
                print i.split(';')
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
