# immobilier/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UtilisateurViewSet, ProprieteViewSet, AnnonceViewSet,
    TransactionViewSet, VisiteViewSet, AlerteViewSet, ActiviteViewSet,
    RegisterView
)

# Création du routeur DRF
router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet)
router.register(r'proprietes', ProprieteViewSet)
router.register(r'annonces', AnnonceViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'visites', VisiteViewSet)
router.register(r'alertes', AlerteViewSet)
router.register(r'activites', ActiviteViewSet)

# URLs de l'app
urlpatterns = [
    path('', include(router.urls)),  # routes DRF
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT refresh
    path('register/', RegisterView.as_view(), name='register'),  # inscription
]
