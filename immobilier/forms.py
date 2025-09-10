from django import forms
import json
from django.core.exceptions import ValidationError
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
    # Ce champ sera utilisé pour capturer la chaîne JSON du front-end
    caracteristiques_json = forms.CharField(required=False, widget=forms.HiddenInput())
    
    # Le champ "caracteristiques" de votre modèle sera traité manuellement
    
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