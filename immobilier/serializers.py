from rest_framework import serializers
from .models import Utilisateur, Propriete, Visite, Message,Contact

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

class VisiteSerializer(serializers.ModelSerializer):
    propriete = serializers.PrimaryKeyRelatedField(queryset=Propriete.objects.all())
    utilisateur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())

    class Meta:
        model = Visite
        fields = '__all__'

# --- Nouveau : Message ---
class MessageSerializer(serializers.ModelSerializer):
    expediteur = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())
    destinataire = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())

    class Meta:
        model = Message
        fields = '__all__'
