from django import forms
from .models import (
    Utilisateur, Propriete, Annonce, Transaction,
    Visite, Alerte, Activite, Message, Information, Temoignage
)

# --- Formulaires basés sur les modèles (ModelForms) ---

class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = '__all__'
        exclude = ('last_login', 'date_joined', 'groups', 'user_permissions')

class ProprieteForm(forms.ModelForm):
    class Meta:
        model = Propriete
        fields = '__all__'

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