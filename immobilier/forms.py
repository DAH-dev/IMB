from django import forms
import json
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Utilisateur, Propriete, Annonce, Transaction,
    Visite, Alerte, Activite, Message, Information, Temoignage,Contact
)






# immobilier/forms.py
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.db.models import Q

# Ajoutez le bon import pour le modèle Utilisateur
from .models import Utilisateur
from django import forms

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur ou Email")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Nom d'utilisateur/E-mail ou mot de passe incorrect.")
        return self.cleaned_data


# --- Formulaires basés sur les modèles (ModelForms) ---
class UtilisateurCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'role', 'photo', 'password1', 'password2')  
        # ⚠️ Django attend 'password1' et 'password2', pas 'password' et 'password2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limiter le choix du rôle à Client et Propriétaire pour l’inscription
        self.fields['role'].choices = [
            ('client', 'Client'),
            ('proprietaire', 'Propriétaire')
        ]

        # Optionnel : personnalisation du style ou des labels
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['email'].label = "Adresse e-mail"
        self.fields['telephone'].label = "Téléphone"
        self.fields['photo'].label = "Photo de profil"

        # Tu peux aussi ajouter des classes CSS si besoin
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'  

class UtilisateurModificationForm(forms.ModelForm):
    # 💡 C'est la bonne classe pour l'édition d'un modèle existant
    class Meta:
        model = Utilisateur
        # Liste des champs que l'utilisateur peut modifier (sans le mot de passe)
        fields = ['username', 'email', 'first_name', 'last_name', 'telephone', 'role', 'photo']
        
        # NOTE : Si vous ne voulez pas que le champ 'role' soit modifiable par l'utilisateur
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.role not in ('admin', 'superadmin') and 'role' in self.fields:
             self.fields['role'].choices = [
                ('client', 'Client'),
                ('proprietaire', 'Propriétaire')
            ]
    
    
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'email', 'telephone', 'sujet', 'message']  # ⚠️ NE PAS inclure proprietaire ni statut

# class ProprieteForm(forms.ModelForm):
#     # Ce champ de formulaire gère la conversion entre la liste Python et la chaîne JSON
#     caracteristiques = forms.CharField(required=False, widget=forms.HiddenInput())

#     class Meta:
#         model = Propriete
#         fields = [
#             'titre', 
#             'description', 
#             'type', 
#             'prix', 
#             'ville', 
#             'commune', 
#             'statut', 
#             'image', 
#             'video', 
#             'proprietaire' # Laissé pour les administrateurs
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Si le formulaire est lié à une instance (mode modification)
#         if self.instance and self.instance.caracteristiques:
#             # On prend la liste Python du modèle et on la convertit en une chaîne JSON
#             # que notre JavaScript pourra lire.
#             self.initial['caracteristiques'] = json.dumps(self.instance.caracteristiques)

#     def clean_caracteristiques(self):
#         # Cette méthode est appelée lors de la soumission du formulaire
#         caracteristiques_json_str = self.cleaned_data.get('caracteristiques')

#         if not caracteristiques_json_str:
#             return []

#         try:
#             # On décode la chaîne JSON reçue du formulaire en une liste Python
#             return json.loads(caracteristiques_json_str)
#         except json.JSONDecodeError:
#             raise ValidationError('Le format des caractéristiques est invalide.')
        
class ProprieteForm(forms.ModelForm):
    # Ce champ de formulaire gère la conversion entre la liste Python et la chaîne JSON
    caracteristiques = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Propriete
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si le formulaire est lié à une instance (mode modification)
        if self.instance and self.instance.caracteristiques:
            # On prend la liste Python du modèle et on la convertit en une chaîne JSON
            # que notre JavaScript pourra lire.
            self.initial['caracteristiques'] = json.dumps(self.instance.caracteristiques)

    def clean_caracteristiques(self):
        # Cette méthode est appelée lors de la soumission du formulaire
        caracteristiques_json_str = self.cleaned_data.get('caracteristiques')

        if not caracteristiques_json_str:
            return []

        try:
            # On décode la chaîne JSON reçue du formulaire en une liste Python
            return json.loads(caracteristiques_json_str)
        except json.JSONDecodeError:
            raise ValidationError('Le format des caractéristiques est invalide.')
        

class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = '__all__'

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

class VisiteForm(forms.ModelForm):
    class Meta:
        model = Visite
        fields = '__all__'

class AlerteForm(forms.ModelForm):
    class Meta:
        model = Alerte
        fields = '__all__'

class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite
        fields = '__all__'

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'

class InformationForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = '__all__'

class TemoignageForm(forms.ModelForm):
    class Meta:
        model = Temoignage
        fields = '__all__'