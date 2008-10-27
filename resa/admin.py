from resa.models import Language, Country
from django.contrib import admin

class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Language, LanguageAdmin)

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Country, CountryAdmin)
