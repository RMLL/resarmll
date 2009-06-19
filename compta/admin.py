# -*- coding: utf-8 -*-

from resarmll.compta.models import PaymentMethod, PlanComptable, BankAccount, \
SupplierAccount, ClientAccount, ProductAccount, ChargeAccount
from django.contrib import admin

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('code','label',)
admin.site.register(PaymentMethod, PaymentMethodAdmin)

class PlanComptableAdmin(admin.ModelAdmin):
    ordering = ('id',)
    search_fields = ('code', 'label')
admin.site.register(PlanComptable, PlanComptableAdmin)

class FinanceAccountAdmin(admin.ModelAdmin):
    ordering = ('id',)
    search_fields = ('code', 'label')

    form_filter = {'code__gte': 0}
    query_filter = {'plan__code__gte': 0}

    def queryset(self, request):
        return super(FinanceAccountAdmin, self).queryset(request).complex_filter(self.query_filter)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['adminform'].form['plan'].field.queryset = \
            context['adminform'].form['plan'].field.queryset.complex_filter(self.form_filter)
        return super(FinanceAccountAdmin, self).render_change_form(request, context, add, change, form_url, obj)

class BankAccountAdmin(FinanceAccountAdmin):
    form_filter = {'code__exact': 512}
    query_filter = {'plan__code__exact': 512}
admin.site.register(BankAccount, BankAccountAdmin)

class SupplierAccountAdmin(FinanceAccountAdmin):
    form_filter = {'code__exact': 401}
    query_filter = {'plan__code__exact': 401}
admin.site.register(SupplierAccount, SupplierAccountAdmin)

class ClientAccountAdmin(FinanceAccountAdmin):
    form_filter = {'code__exact': 411}
    query_filter = {'plan__code__exact': 411}
admin.site.register(ClientAccount, ClientAccountAdmin)

class ProductAccountAdmin(FinanceAccountAdmin):
    form_filter = {'code__startswith': '7'}
    query_filter = {'plan__code__startswith': '7'}
admin.site.register(ProductAccount, ProductAccountAdmin)

class ChargeAccountAdmin(FinanceAccountAdmin):
    form_filter = {'code__startswith': '6'}
    query_filter = {'plan__code__startswith': '6'}
admin.site.register(ChargeAccount, ChargeAccountAdmin)

