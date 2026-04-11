from django.contrib import admin
from .models import (
    Utilisateur, Contact, Propriete, Visite, Message
)

# ---------------------------
# Admin pour Utilisateur
# ---------------------------
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "email", "first_name", "last_name",
        "telephone", "role", "statut", "cni_verifie",
        "phone_verified", "is_staff", "is_superuser"
    )
    list_filter = ("role", "statut", "cni_verifie", "phone_verified", "is_staff", "is_superuser")
    search_fields = ("username", "email", "telephone", "first_name", "last_name")
    ordering = ("-date_joined",)
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        ("Informations de connexion", {
            "fields": ("username", "email", "password")
        }),
        ("Informations personnelles", {
            "fields": ("first_name", "last_name", "telephone", "photo")
        }),
        ("Vérification CNI", {
            "fields": ("cni", "cni_verifie")
        }),
        ("Validation OTP", {
            "fields": ("phone_verified", "otp_code", "otp_created_at", "otp_attempts")
        }),
        ("Statut et rôle", {
            "fields": ("role", "statut", "is_active", "is_staff", "is_superuser")
        }),
        ("Permissions", {
            "fields": ("groups", "user_permissions")
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.role == "superadmin":
            obj.is_superuser = True
            obj.is_staff = True
        super().save_model(request, obj, form, change)


# ---------------------------
# Admin pour Contact (Conversation)
# ---------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "id", "utilisateur", "proprietaire", "propriete",
        "sujet_court", "statut", "date_envoi"
    )
    list_filter = ("statut", "date_envoi", "supprime_par_utilisateur", "supprime_par_proprietaire")
    search_fields = ("nom", "email", "telephone", "sujet", "message")
    ordering = ("-date_envoi",)
    readonly_fields = ("date_envoi",)

    def sujet_court(self, obj):
        return obj.sujet[:50] + "..." if obj.sujet and len(obj.sujet) > 50 else obj.sujet
    sujet_court.short_description = "Sujet"


# ---------------------------
# Admin pour Propriete
# ---------------------------
@admin.register(Propriete)
class ProprieteAdmin(admin.ModelAdmin):
    list_display = (
        "id", "titre", "type", "prix", "ville", "commune",
        "statut", "statut_propriete_admin", "statut_propriete_owner",
        "proprietaire", "date_publication"
    )
    list_filter = ("type", "statut", "statut_propriete_admin", "statut_propriete_owner", "ville")
    search_fields = ("titre", "description", "ville", "commune", "proprietaire__username")
    ordering = ("-date_publication",)
    readonly_fields = ("date_publication", "duree_video")

    fieldsets = (
        ("Informations générales", {
            "fields": ("titre", "description", "type", "prix")
        }),
        ("Localisation", {
            "fields": ("ville", "commune")
        }),
        ("Caractéristiques", {
            "fields": ("caracteristiques",)
        }),
        ("Médias", {
            "fields": ("image", "video", "duree_video")
        }),
        ("Statuts", {
            "fields": ("statut", "statut_propriete_admin", "statut_propriete_owner")
        }),
        ("Publication", {
            "fields": ("date_publication", "proprietaire")
        }),
    )


# ---------------------------
# Admin pour Visite
# ---------------------------
@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ("id", "propriete", "utilisateur", "date_visite")
    list_filter = ("date_visite",)
    search_fields = ("propriete__titre", "utilisateur__username")
    ordering = ("-date_visite",)
    readonly_fields = ("date_visite",)


# ---------------------------
# Admin pour Message
# ---------------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "expediteur", "destinataire", "contact", "statut", "date_envoi", "date_lu")
    list_filter = ("statut", "date_envoi")
    search_fields = ("expediteur__username", "destinataire__username", "contenu")
    ordering = ("-date_envoi",)
    readonly_fields = ("date_envoi", "date_lu")

    fieldsets = (
        ("Conversation", {
            "fields": ("contact",)
        }),
        ("Expéditeur et Destinataire", {
            "fields": ("expediteur", "destinataire")
        }),
        ("Message", {
            "fields": ("contenu", "statut", "date_envoi", "date_lu")
        }),
        ("Suppression", {
            "fields": ("supprime_par_expediteur", "supprime_par_destinataire", "supprime_pour_tous")
        }),
    )