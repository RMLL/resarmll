# -*- coding: utf-8 -*-
from django.contrib import admin

from forms import ArticleAdminForm, CountryAdminForm
from models import Article, Country, Badge, Stock
from orders import Order, OrderDetail

class CountryAdmin(admin.ModelAdmin):
    form = CountryAdminForm
    ordering = ('code',)
    search_fields = ('countrylabel__value', 'code',)
    list_display = ('label', 'code')
admin.site.register(Country, CountryAdmin)

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    ordering = ('order',)
    list_display = ('label', 'price', 'quantity', 'stock', 'order', 'count_confirmed', 'count_paid', 'count_distributed', 'enabled')
admin.site.register(Article, ArticleAdmin)

class BadgeAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name','alt_name', 'color', 'section', 'userchoice', 'default')
admin.site.register(Badge, BadgeAdmin)

class StockAdmin(admin.ModelAdmin):
    ordering = ('order',)
    list_display = ('label','quantity', 'quantity_ordered', 'quantity_paid')
admin.site.register(Stock, StockAdmin)

admin.site.register(Order, admin.ModelAdmin)
admin.site.register(OrderDetail, admin.ModelAdmin)
