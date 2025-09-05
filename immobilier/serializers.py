from rest_framework import serializers
from .models import Utilisateur, Propriete, Annonce, Transaction, Visite, Alerte, Activite, Message, Information, Temoignage

# --- Sérialiseurs pour les modèles ---
class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'


class ProprieteSerializer(serializers.ModelSerializer):
    proprietaire = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())
    
    class Meta:
        model = Propriete
        fields = '__all__'


class AnnonceSerializer(serializers.ModelSerializer):
    propriete = serializers.PrimaryKeyRelatedField(queryset=Propriete.objects.all())
    utilisateur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())
    moderateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Annonce
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    propriete = serializers.PrimaryKeyRelatedField(queryset=Propriete.objects.all())
    utilisateur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'


class VisiteSerializer(serializers.ModelSerializer):
    propriete = serializers.PrimaryKeyRelatedField(queryset=Propriete.objects.all())
    utilisateur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())

    class Meta:
        model = Visite
        fields = '__all__'


class AlerteSerializer(serializers.ModelSerializer):
    propriete = serializers.PrimaryKeyRelatedField(queryset=Propriete.objects.all())
    admin = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Alerte
        fields = '__all__'


class ActiviteSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Activite
        fields = '__all__'


# --- Nouveau : Message ---
class MessageSerializer(serializers.ModelSerializer):
    expediteur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())
    destinataire = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())

    class Meta:
        model = Message
        fields = '__all__'


# --- Nouveau : Information ---
class InformationSerializer(serializers.ModelSerializer):
    admin = UtilisateurSerializer(read_only=True)
    
    class Meta:
        model = Information
        fields = '__all__'


# --- Nouveau : Temoignage ---
class TemoignageSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Temoignage
        fields = '__all__'