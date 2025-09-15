from django.contrib import admin
from .models import (
    Utilisateur, Propriete, Annonce,
    Transaction, Visite, Alerte, Activite,
    Message, Information, Temoignage  # <-- Ajout des modèles manquants ici
)

# ---------------------------
# Admin pour Utilisateur
# ---------------------------
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "email",
        "telephone", "role", "statut",
        "is_staff", "is_superuser"
    )
    list_filter = ("role", "statut", "is_staff", "is_superuser")
    search_fields = ("username", "email", "telephone")
    ordering = ("username",)
    filter_horizontal = ("groups", "user_permissions")

    def save_model(self, request, obj, form, change):
        if obj.role == "superadmin":
            obj.is_superuser = True
            obj.is_staff = True
        super().save_model(request, obj, form, change)

# ---------------------------
# Admin pour Propriete
# ---------------------------
@admin.register(Propriete)
class ProprieteAdmin(admin.ModelAdmin):
    list_display = (
        "id", "titre", "type", "prix",
        "statut", "proprietaire", "date_publication"
    )
    list_filter = ("type", "statut")
    search_fields = ("titre", "description", "ville", "commune")
    ordering = ("-date_publication",)


# ---------------------------
# Admin pour Annonce
# ---------------------------
@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "propriete", "utilisateur", "statut",
        "date_publication", "moderateur", "date_moderation"
    )
    list_filter = ("statut", "date_publication")
    search_fields = ("propriete__titre", "utilisateur__username", "moderateur__username")
    ordering = ("-date_publication",)


# ---------------------------
# Admin pour Transaction
# ---------------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "propriete", "utilisateur", "montant", "type", "date_transaction")
    list_filter = ("type", "date_transaction")
    search_fields = ("propriete__titre", "utilisateur__username")
    ordering = ("-date_transaction",)


# ---------------------------
# Admin pour Visite
# ---------------------------
@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ("id", "propriete", "utilisateur", "date_visite")
    list_filter = ("date_visite",)
    search_fields = ("propriete__titre", "utilisateur__username")
    ordering = ("-date_visite",)


# ---------------------------
# Admin pour Alerte
# ---------------------------
@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ("id", "propriete", "description", "statut", "date_creation", "admin")
    list_filter = ("statut", "date_creation")
    search_fields = ("propriete__titre", "description", "admin__username")
    ordering = ("-date_creation",)


# ---------------------------
# Admin pour Activite
# ---------------------------
@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ("id", "utilisateur", "action", "cible", "date_action")
    list_filter = ("date_action",)
    search_fields = ("utilisateur__username", "action", "cible")
    ordering = ("-date_action",)

# --- NOUVELLES CLASSES ADMIN AJOUTÉES ---

# ---------------------------
# Admin pour Message
# ---------------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "expediteur", "destinataire", "statut", "date_envoi")
    list_filter = ("statut", "date_envoi")
    search_fields = ("expediteur__username", "destinataire__username", "contenu")
    ordering = ("-date_envoi",)
    
# ---------------------------
# Admin pour Information
# ---------------------------
@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = ("id", "titre", "type", "date_creation", "admin" ,"image")
    list_filter = ("type",)
    search_fields = ("titre", "contenu")
    ordering = ("-date_creation",)
    
# ---------------------------
# Admin pour Temoignage
# ---------------------------
@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "utilisateur", "statut", "date_creation")
    list_filter = ("statut",)
    search_fields = ("nom", "contenu")
    ordering = ("-date_creation",)