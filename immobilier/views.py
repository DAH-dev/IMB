from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import (
    Utilisateur, Propriete, Annonce, Transaction,
    Visite, Alerte, Activite, Message, Information, Temoignage
)
from .serializers import (
    UtilisateurSerializer, ProprieteSerializer, AnnonceSerializer,
    TransactionSerializer, VisiteSerializer, AlerteSerializer, ActiviteSerializer,
    MessageSerializer, InformationSerializer, TemoignageSerializer
)
from .forms import (
    UtilisateurForm, ProprieteForm, AnnonceForm, TransactionForm,
    VisiteForm, AlerteForm, ActiviteForm, MessageForm, InformationForm, TemoignageForm
)

# --- VUES POUR L'API REST (JSON) ---

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]

class ProprieteViewSet(viewsets.ModelViewSet):
    queryset = Propriete.objects.all()
    serializer_class = ProprieteSerializer
    permission_classes = [AllowAny]

class AnnonceViewSet(viewsets.ModelViewSet):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [IsAuthenticated]

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

class VisiteViewSet(viewsets.ModelViewSet):
    queryset = Visite.objects.all()
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]

class AlerteViewSet(viewsets.ModelViewSet):
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer
    permission_classes = [IsAuthenticated]

class ActiviteViewSet(viewsets.ModelViewSet):
    queryset = Activite.objects.all()
    serializer_class = ActiviteSerializer
    permission_classes = [IsAuthenticated]

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

class InformationViewSet(viewsets.ModelViewSet):
    queryset = Information.objects.all()
    serializer_class = InformationSerializer
    permission_classes = [AllowAny]

class TemoignageViewSet(viewsets.ModelViewSet):
    queryset = Temoignage.objects.all()
    serializer_class = TemoignageSerializer
    permission_classes = [AllowAny]

class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UtilisateurSerializer

# --- VUES POUR LE SITE WEB (HTML) ---

# Vues générales du site
def page_accueil(request):
    informations = Information.objects.filter(type='presentation').first()
    temoignages_valides = Temoignage.objects.filter(statut='valide')
    context = {'informations': informations, 'temoignages': temoignages_valides}
    return render(request, 'immobilier/index.html', context)

def liste_proprietes_web(request):
    proprietes = Propriete.objects.filter(statut='disponible').order_by('-date_publication')
    context = {'proprietes': proprietes}
    return render(request, 'liste_proprietes.html', context)

def detail_propriete_web(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    context = {'propriete': propriete}
    return render(request, 'detail_propriete.html', context)

# --- Vues de gestion (CRUD) par table ---

# Utilisateur
def utilisateur_list(request):
    objets = Utilisateur.objects.all()
    return render(request, 'utilisateurs/list.html', {'objets': objets})

def utilisateur_create(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('utilisateur_list')
    else:
        form = UtilisateurForm()
    return render(request, 'utilisateurs/form.html', {'form': form, 'action': 'Créer'})

def utilisateur_update(request, pk):
    objet = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, request.FILES, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('utilisateur_list')
    else:
        form = UtilisateurForm(instance=objet)
    return render(request, 'utilisateurs/form.html', {'form': form, 'action': 'Modifier'})

def utilisateur_delete(request, pk):
    objet = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('utilisateur_list')
    return render(request, 'utilisateurs/confirm_delete.html', {'objet': objet})

# Propriete
def propriete_list(request):
    objets = Propriete.objects.all()
    return render(request, 'proprietes/list.html', {'objets': objets})

def propriete_create(request):
    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('propriete_list')
    else:
        form = ProprieteForm()
    return render(request, 'proprietes/form.html', {'form': form, 'action': 'Créer'})

def propriete_update(request, pk):
    objet = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('propriete_list')
    else:
        form = ProprieteForm(instance=objet)
    return render(request, 'proprietes/form.html', {'form': form, 'action': 'Modifier'})

def propriete_delete(request, pk):
    objet = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('propriete_list')
    return render(request, 'proprietes/confirm_delete.html', {'objet': objet})

# Annonce
def annonce_list(request):
    objets = Annonce.objects.all()
    return render(request, 'annonces/list.html', {'objets': objets})

def annonce_create(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('annonce_list')
    else:
        form = AnnonceForm()
    return render(request, 'annonces/form.html', {'form': form, 'action': 'Créer'})

def annonce_update(request, pk):
    objet = get_object_or_404(Annonce, pk=pk)
    if request.method == 'POST':
        form = AnnonceForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('annonce_list')
    else:
        form = AnnonceForm(instance=objet)
    return render(request, 'annonces/form.html', {'form': form, 'action': 'Modifier'})

def annonce_delete(request, pk):
    objet = get_object_or_404(Annonce, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('annonce_list')
    return render(request, 'annonces/confirm_delete.html', {'objet': objet})

# Transaction
def transaction_list(request):
    objets = Transaction.objects.all()
    return render(request, 'transactions/list.html', {'objets': objets})

def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/form.html', {'form': form, 'action': 'Créer'})

def transaction_update(request, pk):
    objet = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=objet)
    return render(request, 'transactions/form.html', {'form': form, 'action': 'Modifier'})

def transaction_delete(request, pk):
    objet = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/confirm_delete.html', {'objet': objet})

# Visite
def visite_list(request):
    objets = Visite.objects.all()
    return render(request, 'visites/list.html', {'objets': objets})

def visite_create(request):
    if request.method == 'POST':
        form = VisiteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('visite_list')
    else:
        form = VisiteForm()
    return render(request, 'visites/form.html', {'form': form, 'action': 'Créer'})

def visite_update(request, pk):
    objet = get_object_or_404(Visite, pk=pk)
    if request.method == 'POST':
        form = VisiteForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('visite_list')
    else:
        form = VisiteForm(instance=objet)
    return render(request, 'visites/form.html', {'form': form, 'action': 'Modifier'})

def visite_delete(request, pk):
    objet = get_object_or_404(Visite, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('visite_list')
    return render(request, 'visites/confirm_delete.html', {'objet': objet})

# Alerte
def alerte_list(request):
    objets = Alerte.objects.all()
    return render(request, 'alertes/list.html', {'objets': objets})

def alerte_create(request):
    if request.method == 'POST':
        form = AlerteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('alerte_list')
    else:
        form = AlerteForm()
    return render(request, 'alertes/form.html', {'form': form, 'action': 'Créer'})

def alerte_update(request, pk):
    objet = get_object_or_404(Alerte, pk=pk)
    if request.method == 'POST':
        form = AlerteForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('alerte_list')
    else:
        form = AlerteForm(instance=objet)
    return render(request, 'alertes/form.html', {'form': form, 'action': 'Modifier'})

def alerte_delete(request, pk):
    objet = get_object_or_404(Alerte, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('alerte_list')
    return render(request, 'alertes/confirm_delete.html', {'objet': objet})
    
# Activite
def activite_list(request):
    objets = Activite.objects.all()
    return render(request, 'activites/list.html', {'objets': objets})

def activite_create(request):
    if request.method == 'POST':
        form = ActiviteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('activite_list')
    else:
        form = ActiviteForm()
    return render(request, 'activites/form.html', {'form': form, 'action': 'Créer'})

def activite_update(request, pk):
    objet = get_object_or_404(Activite, pk=pk)
    if request.method == 'POST':
        form = ActiviteForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('activite_list')
    else:
        form = ActiviteForm(instance=objet)
    return render(request, 'activites/form.html', {'form': form, 'action': 'Modifier'})

def activite_delete(request, pk):
    objet = get_object_or_404(Activite, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('activite_list')
    return render(request, 'activites/confirm_delete.html', {'objet': objet})

# Message
def message_list(request):
    objets = Message.objects.all()
    return render(request, 'messages/list.html', {'objets': objets})

def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = MessageForm()
    return render(request, 'messages/form.html', {'form': form, 'action': 'Créer'})

def message_update(request, pk):
    objet = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = MessageForm(instance=objet)
    return render(request, 'messages/form.html', {'form': form, 'action': 'Modifier'})

def message_delete(request, pk):
    objet = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('message_list')
    return render(request, 'messages/confirm_delete.html', {'objet': objet})
    
# Information
def information_list(request):
    objets = Information.objects.all()
    return render(request, 'informations/list.html', {'objets': objets})

def information_create(request):
    if request.method == 'POST':
        form = InformationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('information_list')
    else:
        form = InformationForm()
    return render(request, 'informations/form.html', {'form': form, 'action': 'Créer'})

def information_update(request, pk):
    objet = get_object_or_404(Information, pk=pk)
    if request.method == 'POST':
        form = InformationForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('information_list')
    else:
        form = InformationForm(instance=objet)
    return render(request, 'informations/form.html', {'form': form, 'action': 'Modifier'})

def information_delete(request, pk):
    objet = get_object_or_404(Information, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('information_list')
    return render(request, 'informations/confirm_delete.html', {'objet': objet})
    
# Temoignage
def temoignage_list(request):
    objets = Temoignage.objects.all()
    return render(request, 'temoignages/list.html', {'objets': objets})

def temoignage_create(request):
    if request.method == 'POST':
        form = TemoignageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('temoignage_list')
    else:
        form = TemoignageForm()
    return render(request, 'temoignages/form.html', {'form': form, 'action': 'Créer'})

def temoignage_update(request, pk):
    objet = get_object_or_404(Temoignage, pk=pk)
    if request.method == 'POST':
        form = TemoignageForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('temoignage_list')
    else:
        form = TemoignageForm(instance=objet)
    return render(request, 'temoignages/form.html', {'form': form, 'action': 'Modifier'})

def temoignage_delete(request, pk):
    objet = get_object_or_404(Temoignage, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('temoignage_list')
    return render(request, 'temoignages/confirm_delete.html', {'objet': objet})




# les fontion pour lla partie statique à rendre dinamique




def detail_propriete(request):

    return render(request ,'immobilier/detail_propriete.html', {})
def superadmin(request):
    return render(request,'immobilier/superadmin.html' )
def proprietaire(request):
    return render(request, 'immobilier/proprietaire.html' )
def mes_proprietes(request):
    return render(request, 'immobilier/mes_proprietes.html' )

def proprietaire_parametres(request):
    return render(request, 'immobilier/parametres_proprietaire.html' )
def mes_messages(request):
    return render(request, 'immobilier/mes_messages.html' )

def courte_video(request):
    return render(request,'immobilier/courte_video.html' )

def abaut(request):
    return render(request,'immobilier/about.html' ) 
 
def terrain(request):
    return render(request,'immobilier/terrain.html' )  

def maison(request):
    return render(request,'immobilier/Maisons.html' )  
def plan(request):
    return render(request,'immobilier/plan.html' ) 

def statistiques(request):
    return render(request,'immobilier/statistiques.html' ) 

def temoingnages(request):
    return render(request,'immobilier/temoingnages.html' ) 
 

def nav_bar(request):
    return render(request, 'immobilier/nav_bar.html')