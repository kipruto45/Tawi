from django.contrib import admin
from .models import Beneficiary

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'contact_person')


from django.contrib import admin
from .models import PlantingSite

@admin.register(PlantingSite)
class PlantingSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'beneficiary', 'address')
