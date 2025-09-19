from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

# Création d'un router pour les vues de l'API REST
router = DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'proprietes', views.ProprieteViewSet)
router.register(r'annonces', views.AnnonceViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'visites', views.VisiteViewSet)
router.register(r'alertes', views.AlerteViewSet)
router.register(r'activites', views.ActiviteViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'informations', views.InformationViewSet)
router.register(r'temoignages', views.TemoignageViewSet)

urlpatterns = [
    # --- URLS POUR LE SITE WEB (VUES HTML) ---
path('connexion/',views.login_view, name='login'),
    # Vues générales
    path('', views.page_accueil, name='index'),
    path('proprietes/maison/', views.proprietes_maison, name='proprietes_maison'),
    path('proprietes/Terrain/', views.proprietes_Terrain, name='proprietes_Terrain'),
    path('proprietes/shorts/', views.video_shorts, name='video_shorts'),
    path('proprietes/<int:pk>/', views.detail_propriete_web, name='detail_propriete_web'),

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

    # Vues CRUD pour les annonces
    path('gestion/annonces/', views.annonce_list, name='annonce_list'),
    path('gestion/annonces/ajouter/', views.annonce_create, name='annonce_create'),
    path('gestion/annonces/<int:pk>/modifier/', views.annonce_update, name='annonce_update'),
    path('gestion/annonces/<int:pk>/supprimer/', views.annonce_delete, name='annonce_delete'),

    # Vues CRUD pour les utilisateurs
    path('gestion/utilisateurs/', views.utilisateur_list, name='utilisateur_list'),
    path('gestion/utilisateurs/ajouter/', views.utilisateur_create, name='utilisateur_create'),
    path('gestion/utilisateurs/<int:pk>/modifier/', views.utilisateur_update, name='utilisateur_update'),
    path('gestion/utilisateurs/<int:pk>/supprimer/', views.utilisateur_delete, name='utilisateur_delete'),
    
    # Vues CRUD pour les transactions
    path('gestion/transactions/', views.transaction_list, name='transaction_list'),
    path('gestion/transactions/ajouter/', views.transaction_create, name='transaction_create'),
    path('gestion/transactions/<int:pk>/modifier/', views.transaction_update, name='transaction_update'),
    path('gestion/transactions/<int:pk>/supprimer/', views.transaction_delete, name='transaction_delete'),
    
    # Vues CRUD pour les visites
    path('gestion/visites/', views.visite_list, name='visite_list'),
    path('gestion/visites/ajouter/', views.visite_create, name='visite_create'),
    path('gestion/visites/<int:pk>/modifier/', views.visite_update, name='visite_update'),
    path('gestion/visites/<int:pk>/supprimer/', views.visite_delete, name='visite_delete'),
    
    # Vues CRUD pour les alertes
    path('gestion/alertes/', views.alerte_list, name='alerte_list'),
    path('gestion/alertes/ajouter/', views.alerte_create, name='alerte_create'),
    path('gestion/alertes/<int:pk>/modifier/', views.alerte_update, name='alerte_update'),
    path('gestion/alertes/<int:pk>/supprimer/', views.alerte_delete, name='alerte_delete'),
    
    # Vues CRUD pour les activites
    path('gestion/activites/', views.activite_list, name='activite_list'),
    path('gestion/activites/ajouter/', views.activite_create, name='activite_create'),
    path('gestion/activites/<int:pk>/modifier/', views.activite_update, name='activite_update'),
    path('gestion/activites/<int:pk>/supprimer/', views.activite_delete, name='activite_delete'),
    
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
    path('success/', views.success_page, name='success_page'),
     
    
    # Vues CRUD pour les informations
    path('gestion/informations/', views.information_list, name='information_list'),
    path('gestion/informations/ajouter/', views.information_create, name='information_create'),
    path('gestion/informations/<int:pk>/modifier/', views.information_update, name='information_update'),
    path('gestion/informations/<int:pk>/supprimer/', views.information_delete, name='information_delete'),
    path('about', views.abaut, name='about'),
    
    # Vues CRUD pour les temoignages
    path('gestion/temoignages/', views.temoignage_list, name='temoignage_list'),
    path('gestion/temoignages/ajouter/', views.temoignage_create, name='temoignage_create'),
    path('gestion/temoignages/<int:pk>/modifier/', views.temoignage_update, name='temoignage_update'),
    path('gestion/temoignages/<int:pk>/supprimer/', views.temoignage_delete, name='temoignage_delete'),

    # --- URLS POUR L'API REST (VUES JSON) ---
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),






    # urls pour la partie dinamique à rendre statique 

     path('detail_propriete', views.detail_propriete , name='detail_propriete'),
    path('superadmin',views.superadmin, name='superadmin'),
    path('proprietaire',views.proprietaire, name='proprietaire'),
    path('mes_proprietes',views.mes_proprietes, name='mes_proprietes'),
    path('proprietaire_parametres',views.proprietaire_parametres, name='proprietaire_parametres'),
    path('courte_video', views.courte_video, name='courte_video'),
    # path('about', views.abaut, name='about'),
    path('terrain', views.terrain, name='terrain'),
    path('maison', views.maison, name='maison'),
    path('plan', views.plan, name='plan'),
    path('statistiques', views.statistiques, name='statistiques'),
    path('temoingnages', views.temoingnages, name='temoingnages'),
    # path('mes_messages.html', views.mes_messages, name='mes_messages'),
    path('nav_bar', views.nav_bar, name='nav_bar')
]