from django.contrib import admin

# immobilier/admin.py
from django.contrib import admin
from .models import (
    Utilisateur, Propriete, Annonce,
    Transaction, Visite, Alerte, Activite
)

# ---------------------------
# Admin pour Utilisateur
# ---------------------------
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'statut', 'is_staff', 'is_superuser')
    list_filter = ('role', 'statut', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'telephone')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

# ---------------------------
# Admin pour Propriete
# ---------------------------
@admin.register(Propriete)
class ProprieteAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'type', 'prix', 'statut', 'proprietaire', 'date_publication')
    list_filter = ('type', 'statut')
    search_fields = ('titre', 'description', 'localisation')
    ordering = ('-date_publication',)

# ---------------------------
# Admin pour Annonce
# ---------------------------
@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('id', 'propriete', 'utilisateur', 'statut', 'date_publication', 'moderateur', 'date_moderation')
    list_filter = ('statut',)
    search_fields = ('propriete__titre', 'utilisateur__username')
    ordering = ('-date_publication',)

# ---------------------------
# Admin pour Transaction
# ---------------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'propriete', 'utilisateur', 'montant', 'type', 'date_transaction')
    list_filter = ('type', 'date_transaction')
    search_fields = ('propriete__titre', 'utilisateur__username')
    ordering = ('-date_transaction',)

# ---------------------------
# Admin pour Visite
# ---------------------------
@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'propriete', 'utilisateur', 'date_visite')
    list_filter = ('date_visite',)
    search_fields = ('propriete__titre', 'utilisateur__username')
    ordering = ('-date_visite',)

# ---------------------------
# Admin pour Alerte
# ---------------------------
@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('id', 'propriete', 'description', 'statut', 'date_creation', 'admin')
    list_filter = ('statut', 'date_creation')
    search_fields = ('propriete__titre', 'description', 'admin__username')
    ordering = ('-date_creation',)

# ---------------------------
# Admin pour Activite
# ---------------------------
@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'action', 'cible', 'date_action')
    list_filter = ('date_action',)
    search_fields = ('utilisateur__username', 'action', 'cible')
    ordering = ('-date_action',)
