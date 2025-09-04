from rest_framework import serializers
from .models import Utilisateur, Propriete, Annonce, Transaction, Visite, Alerte, Activite


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'


class ProprieteSerializer(serializers.ModelSerializer):
    proprietaire = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Propriete
        fields = '__all__'


class AnnonceSerializer(serializers.ModelSerializer):
    propriete = ProprieteSerializer(read_only=True)
    utilisateur = UtilisateurSerializer(read_only=True)
    moderateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Annonce
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    propriete = ProprieteSerializer(read_only=True)
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class VisiteSerializer(serializers.ModelSerializer):
    propriete = ProprieteSerializer(read_only=True)
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Visite
        fields = '__all__'


class AlerteSerializer(serializers.ModelSerializer):
    propriete = ProprieteSerializer(read_only=True)
    admin = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Alerte
        fields = '__all__'


class ActiviteSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Activite
        fields = '__all__'
