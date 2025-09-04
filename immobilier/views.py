from django.shortcuts import render

from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny
from .models import Utilisateur, Propriete, Annonce, Transaction, Visite, Alerte, Activite
from .serializers import (
    UtilisateurSerializer, ProprieteSerializer, AnnonceSerializer,
    TransactionSerializer, VisiteSerializer, AlerteSerializer, ActiviteSerializer
)

# CRUD viewsets
class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer


class ProprieteViewSet(viewsets.ModelViewSet):
    queryset = Propriete.objects.all()
    serializer_class = ProprieteSerializer


class AnnonceViewSet(viewsets.ModelViewSet):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class VisiteViewSet(viewsets.ModelViewSet):
    queryset = Visite.objects.all()
    serializer_class = VisiteSerializer


class AlerteViewSet(viewsets.ModelViewSet):
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer


class ActiviteViewSet(viewsets.ModelViewSet):
    queryset = Activite.objects.all()
    serializer_class = ActiviteSerializer


# ✅ Inscription
class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UtilisateurSerializer
