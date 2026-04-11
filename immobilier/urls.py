from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

# Création d'un router pour les vues de l'API REST
router = DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'proprietes', views.ProprieteViewSet)

router.register(r'visites', views.VisiteViewSet)

router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    # --- URLS POUR LE SITE WEB (VUES HTML) ---
path('inscription/', views.inscription, name='inscription'),
path('connexion/',views.login_view, name='connexion'),
path('deconnexion/', views.deconnexion, name='logout'),

# urls.py - Ajouter ces lignes
path('inscription/verification/', views.inscription_otp, name='inscription_otp'),
path('inscription/renvoyer-code/', views.resend_otp, name='resend_otp'),
    # Vues générales
    path('', views.page_accueil, name='index'),
    path('proprietes/maison/', views.proprietes_maison, name='proprietes_maison'),
    path('proprietes/Terrain/', views.proprietes_Terrain, name='proprietes_Terrain'),
    path('proprietes/plan/', views.proprietes_plan, name='proprietes_plan'),
    path('proprietes/shorts/', views.video_shorts, name='video_shorts'),
    path('proprietes/<int:pk>/', views.detail_propriete_web, name='detail_propriete_web'),
    path('navbar/', views.navbar, name='navbar'),

 # Vues de gestion pour les Contacts
    path('contact/create/', views.contact_create, name='contact_create'),
    path('contact/list/', views.contact_list, name='contact_list'),
    path('contact/update/<int:pk>/', views.contact_update, name='contact_update'),
    path('contact/delete/<int:pk>/', views.contact_delete, name='contact_delete'),

    # Vues CRUD pour les propriétés
    path('gestion/proprietes/', views.propriete_list, name='propriete_list'),
    path('gestion/proprietes/ajouter/', views.propriete_create, name='propriete_create'),
    path('gestion/proprietes/<int:pk>/modifier/', views.propriete_update, name='propriete_update'),
    path('gestion/proprietes/<int:pk>/supprimer/', views.propriete_delete, name='propriete_delete'),


    # Vues CRUD pour les utilisateurs
    path('gestion/utilisateurs/', views.utilisateur_list, name='utilisateur_list'),
  

    # path('gestion/utilisateurs/<int:pk>/modifier/', views.utilisateur_update, name='utilisateur_update'),
    path('gestion/utilisateurs/<int:pk>/supprimer/', views.utilisateur_delete, name='utilisateur_delete'),
    

    # Vues CRUD pour les visites
    path('gestion/visites/', views.visite_list, name='visite_list'),
    path('gestion/visites/ajouter/', views.visite_create, name='visite_create'),
    path('gestion/visites/<int:pk>/modifier/', views.visite_update, name='visite_update'),
    path('gestion/visites/<int:pk>/supprimer/', views.visite_delete, name='visite_delete'),
    
    # Vues CRUD pour les messages (pour les administrateurs)
    path('gestion/messages/', views.message_list, name='message_list'),
    path('gestion/messages/ajouter/', views.message_create, name='message_create'),
    path('gestion/messages/<int:pk>/modifier/', views.message_update, name='message_update'),
    path('gestion/messages/<int:pk>/supprimer/', views.message_delete, name='message_delete'),

    # Vues pour la messagerie (pour les utilisateurs)
    path('messages/', views.mes_messages, name='mes_messages'),
    path('messages/<int:contact_pk>/', views.mes_messages, name='mes_messages_detail'),
    path('send_message/<int:contact_pk>/', views.send_message, name='send_message'),
     path('messages/supprimer/<int:message_pk>/<str:mode>/', views.supprimer_message, name='supprimer_message'),
    path("messages/<int:contact_pk>/supprimer/", views.supprimer_conversation, name="supprimer_conversation"),
    path('demarrer-conversation/<int:propriete_pk>/', views.demarrer_conversation, name='demarrer_conversation'),

    # API pour l'actualisation des messages
    path('api/check-new-messages/', views.api_check_new_messages, name='check_new_messages'),
    
    path('about/', views.abaut, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # --- URLS POUR L'API REST (VUES JSON) ---
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),

    # urls pour la partie dinamique à rendre statique 

    path('detail_propriete', views.detail_propriete , name='detail_propriete'),
   
    path('proprietaire',views.proprietaire, name='proprietaire'),
    path('espace-client/', views.espace_client, name='espace_client'),
    path('mes_proprietes',views.mes_proprietes, name='mes_proprietes'),
    path('proprietaire/<int:proprietaire_pk>/', views.propriete_par_proprietaire, name='propriete_par_proprietaire'),
  
    path('profil',views.profil, name='profil'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),


    path('superadmin/utilisateurs/', views.gestion_utilisateurs_admin, name='gestion_utilisateurs_admin'),
    path('superadmin/utilisateurs/creer/', views.creer_utilisateur_admin, name='creer_utilisateur_admin'),
    path('superadmin/utilisateurs/<int:pk>/modifier/', views.modifier_utilisateur_admin, name='modifier_utilisateur_admin'),
    path('superadmin/utilisateurs/<int:pk>/supprimer/', views.supprimer_utilisateur_admin, name='supprimer_utilisateur_admin'),
    path('superadmin/utilisateurs/<int:pk>/toggle-statut/', views.toggle_statut_utilisateur, name='toggle_statut_utilisateur'),

    path('conditions_utilisation/', views.conditions_utilisation, name='conditions_utilisation'),
    path('politique_confidentialite/', views.politique_confidentialite, name='politique_confidentialite'),

    path('utilisateur/verifier-cni/<int:pk>/', views.verifier_cni, name='verifier_cni'),
    # Gestion des proprietes (admin)
    path('superadmin/proprietes/', views.gestion_proprietes_admin, name='gestion_proprietes_admin'),
    path('superadmin/proprietes/<int:pk>/modifier/', views.propriete_update_admin, name='propriete_update_admin'),
    path('propriete/toggle-statut/<int:pk>/', views.toggle_statut_propriete, name='toggle_statut_propriete'),

   # urls.py
   path('propriete/toggle-admin-statut/<int:pk>/', views.toggle_admin_statut_propriete, name='toggle_admin_statut_propriete'),
   path('propriete/toggle-owner-statut/<int:pk>/', views.toggle_owner_statut_propriete, name='toggle_owner_statut_propriete'),

     path('contact/', views.contact, name='contact'),
     path('contacts-admin/', views.contacts_admin, name='contacts_admin'),
]