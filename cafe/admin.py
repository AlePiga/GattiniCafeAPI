from django.contrib import admin
from .models import Categoria, Prodotto, Ordine, OrdineProdotto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'descrizione']


@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'prezzo', 'disponibile', 'categoria']
    list_filter = ['disponibile', 'categoria']
    search_fields = ['nome', 'descrizione']


@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    list_display = ['id', 'utente', 'stato', 'totale', 'data_ordine']
    list_filter = ['stato']


@admin.register(OrdineProdotto)
class OrdineProdottoAdmin(admin.ModelAdmin):
    list_display = ['id', 'ordine', 'prodotto', 'quantita']
