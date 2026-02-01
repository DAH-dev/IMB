from rest_framework import serializers
from .models import Utilisateur, Propriete, Annonce, Transaction, Visite, Alerte, Activite, Message, Information, Temoignage,Contact

# --- Sérialiseurs pour les modèles ---
class UtilisateurSerializer(serializers.ModelSerializer):
    # Les champs de mot de passe ne sont pas stockés en clair
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = Utilisateur
        fields = ["id", "username", "email", "password", "password2", "telephone", "role", "photo", "first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        # Validez si les deux mots de passe correspondent
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        # Créez l'utilisateur avec tous les champs
        user = Utilisateur(
            username=validated_data["username"],
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            telephone=validated_data.get("telephone"),
            role=validated_data.get("role"),
            photo=validated_data.get("photo"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
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