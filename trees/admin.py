from django.contrib import admin
from .models import TreeSpecies, Tree, TreeUpdate

@admin.register(TreeSpecies)
class TreeSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('tree_id', 'species', 'planting_date', 'beneficiary', 'status')

@admin.register(TreeUpdate)
class TreeUpdateAdmin(admin.ModelAdmin):
    list_display = ('tree', 'date', 'status')
