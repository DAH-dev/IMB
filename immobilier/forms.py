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
        fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'role', 'photo', 'cni', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limiter le choix du rôle à Client et Propriétaire pour l’inscription
        self.fields['role'].choices = [
            ('client', 'Client'),
            ('proprietaire', 'Propriétaire')
        ]

        # Personnalisation des labels
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['email'].label = "Adresse e-mail"
        self.fields['first_name'].label = "Prénom"
        self.fields['last_name'].label = "Nom"
        self.fields['telephone'].label = "Téléphone"
        self.fields['photo'].label = "Photo de profil (optionnel)"
        self.fields['cni'].label = "Carte Nationale d'Identité"
        
        # ✅ Rendre tous les champs obligatoires
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['telephone'].required = True
        self.fields['cni'].required = True
        self.fields['photo'].required = False  # Photo reste optionnelle

        # Ajouter des classes CSS
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("L'adresse email est obligatoire.")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError("Le prénom est obligatoire.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError("Le nom est obligatoire.")
        return last_name
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone:
            raise ValidationError("Le numéro de téléphone est obligatoire.")
        if not telephone.isdigit():
            raise ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        if len(telephone) < 8:
            raise ValidationError("Le numéro de téléphone doit contenir au moins 8 chiffres.")
        return telephone
    
    def clean_cni(self):
        cni = self.cleaned_data.get('cni')
        if not cni:
            raise ValidationError("La Carte Nationale d'Identité est obligatoire.")
        return cni


class UtilisateurModificationForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'telephone', 'role', 'photo', 'cni']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.role not in ('admin', 'superadmin') and 'role' in self.fields:
             self.fields['role'].choices = [
                ('client', 'Client'),
                ('proprietaire', 'Propriétaire')
            ]
        
        # Personnalisation des labels
        self.fields['first_name'].label = "Prénom"
        self.fields['last_name'].label = "Nom"
        self.fields['cni'].label = "Carte Nationale d'Identité"
        
        # ✅ Rendre les champs obligatoires pour la modification
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['telephone'].required = True
        
        # CNI obligatoire seulement si elle n'existe pas encore
        if not self.instance.cni:
            self.fields['cni'].required = True
        else:
            self.fields['cni'].required = False
        
        # Photo reste optionnelle
        self.fields['photo'].required = False
        
        # Ajouter des classes CSS
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = 'form-control'
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone:
            raise ValidationError("Le numéro de téléphone est obligatoire.")
        if not telephone.isdigit():
            raise ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        if len(telephone) < 8:
            raise ValidationError("Le numéro de téléphone doit contenir au moins 8 chiffres.")
        return telephone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("L'adresse email est obligatoire.")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError("Le prénom est obligatoire.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError("Le nom est obligatoire.")
        return last_name
    
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