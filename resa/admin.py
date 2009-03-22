# -*- coding: utf-8 -*-                                                                                                                                        

from resa.forms import ArticleAdminForm, CountryAdminForm
from resa.models import Article, Country
from django.contrib import admin

class CountryAdmin(admin.ModelAdmin):                                                                                                                          
    form = CountryAdminForm                                                                                                    

admin.site.register(Country, CountryAdmin)                                                                                                                     

class ArticleAdmin(admin.ModelAdmin):                                                                                                                          
    form = ArticleAdminForm                                                                                                                                  

admin.site.register(Article, ArticleAdmin)                                                                                                                     
