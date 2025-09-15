from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, generics
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

from .models import (
    Utilisateur, Propriete, Annonce, Transaction,
    Visite, Alerte, Activite, Message, Information, Temoignage,Contact
)
from .serializers import (
    UtilisateurSerializer, ProprieteSerializer, AnnonceSerializer,
    TransactionSerializer, VisiteSerializer, AlerteSerializer, ActiviteSerializer,
    MessageSerializer, InformationSerializer, TemoignageSerializer,ContactSerializer
)
from .forms import (
    UtilisateurForm, ProprieteForm, AnnonceForm, TransactionForm,
    VisiteForm, AlerteForm, ActiviteForm, MessageForm, InformationForm, TemoignageForm,ContactForm
)

# --- VUES POUR L'API REST (JSON) ---

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
    def get_permissions(self):
        """
        Définit les permissions pour chaque action.
        Seule la création est ouverte à tous (pour le formulaire de contact).
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]    

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


from .forms import UserLoginForm

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirection selon rôle
            if user.is_staff:
                # return redirect('admin_dashboard')
                return redirect('superadmin')
            
            elif user.role == 'proprietaire':
                # return redirect('proprietaire_dashboard')
                return redirect('proprietaire')
            else:
                # return redirect('client_dashboard')
                return redirect('proprietaire')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

# Vues générales du site
def page_accueil(request):
    # Récupérer les 6 dernières propriétés disponibles

    proprietes_recentes = Propriete.objects.filter(
        Q(statut='disponible') | Q(statut='en_netoyage') | Q(statut='en_construction')
    ).order_by('-date_publication')[:6]
    context = {
        'proprietes_recentes': proprietes_recentes,
    }
    return render(request, 'index.html', context)

def proprietes_maison(request):
    # Récupère toutes les propriétés où le type est 'Maison'
    proprietes = Propriete.objects.filter(type__iexact='maison')
    
    context = {
        'proprietes_recentes': proprietes,
    }
    # Assurez-vous d'avoir un template 'maison.html' si vous ne voulez pas utiliser 'index.html'
    return render(request, 'index.html', context)



def proprietes_Terrain(request):
    # Récupère toutes les propriétés où le type est 'Maison'
    proprietes = Propriete.objects.filter(type='terrain')
    
    context = {
        'proprietes_recentes': proprietes,
    }
    # Assurez-vous d'avoir un template 'maison.html' si vous ne voulez pas utiliser 'index.html'
    return render(request, 'index.html', context)

def video_shorts(request):
    # Filtre pour les propriétés qui ont une vidéo non nulle et dont la durée est <= 60 secondes
    proprietes_shorts = Propriete.objects.all()
       
    context = {
        'proprietes_shorts': proprietes_shorts,
    }
    
    return render(request, 'courtes_videos.html', context)




def detail_propriete_web(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    
    utilisateur_connecte = None
    if request.user.is_authenticated and request.user.id:
        try:
            utilisateur_connecte = Utilisateur.objects.get(pk=request.user.id)
        except Utilisateur.DoesNotExist:
            pass

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            telephone = form.cleaned_data['telephone']
            sujet = form.cleaned_data['sujet']
            message_content = form.cleaned_data['message']

            contact_fil = None
            if utilisateur_connecte:
                contact_fil = Contact.objects.filter(
                    utilisateur=utilisateur_connecte,
                    propriete=propriete,
                    proprietaire=propriete.proprietaire
                ).first()
            elif email:
                contact_fil = Contact.objects.filter(
                    email=email,
                    propriete=propriete,
                    proprietaire=propriete.proprietaire
                ).first()

            if not contact_fil:
                contact_fil = Contact.objects.create(
                    utilisateur=utilisateur_connecte,
                    proprietaire=propriete.proprietaire,
                    propriete=propriete,
                    nom=nom,
                    email=email,
                    telephone=telephone,
                    sujet=sujet,
                    message=message_content, 
                    statut='en_cours'
                )
            
            # --- MODIFICATION CLÉ ICI ---
            # Le code de création de Message doit être conditionné.
            if utilisateur_connecte:
                # Crée un message seulement si l'utilisateur est connecté.
                Message.objects.create(
                    contact=contact_fil,
                    expediteur=utilisateur_connecte, # C'est maintenant sûr, car l'utilisateur est connecté
                    destinataire=propriete.proprietaire,
                    contenu=message_content
                )
            
            # La redirection doit aussi être conditionnée.
            if utilisateur_connecte:
                return redirect('mes_messages_detail', contact_pk=contact_fil.pk)
            else:
                return redirect('success_page')

    # Le reste du code pour l'affichage de la page
    else:
        form = ContactForm()
    
    conditions = Q(type__iexact=propriete.type) | Q(commune__iexact=propriete.commune)
    if isinstance(propriete.caracteristiques, list):
        for caracteristique_nom in propriete.caracteristiques:
            conditions |= Q(caracteristiques__icontains=caracteristique_nom)

    proprietes_similaires = Propriete.objects.filter(conditions).exclude(
        pk=propriete.pk
    ).distinct()[:8]

    context = {
        'propriete': propriete,
        'proprietes_similaires': proprietes_similaires,
        'form': form,
    }
    
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

def contact_create(request):
    """
    Vue pour créer un nouveau contact via le formulaire de contact du site.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            
            # Assigner l'utilisateur connecté si disponible
            if request.user.is_authenticated:
                contact_message.utilisateur = request.user
            
            # Assigner un propriétaire (ex: le premier superadmin trouvé)
            admin_user = Utilisateur.objects.filter(role='superadmin').first()
            if admin_user:
                contact_message.proprietaire = admin_user
                contact_message.save()
                return redirect('succes_page') # Page de confirmation d'envoi
            else:
                # Gérer le cas où il n'y a pas de superadmin pour recevoir le message
                # Optionnel : Afficher un message d'erreur ou rediriger vers une page d'erreur.
                pass
    else:
        form = ContactForm()
    
    return render(request, 'contacts/form.html', {'form': form, 'action': 'Envoyer'})


# immobilier/views.py

def contact_list(request):
    """
    Affiche la liste de tous les messages de contact reçus par l'utilisateur connecté.
    """
    # Seuls les messages où l'utilisateur est le destinataire sont affichés
    objets = Contact.objects.filter(proprietaire=request.user).order_by('-date_envoi')
    return render(request, 'contacts/list.html', {'objets': objets})

# immobilier/views.py

def contact_update(request, pk):
    """
    Permet de modifier le statut d'un contact.
    """
    objet = get_object_or_404(Contact, pk=pk, proprietaire=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm(instance=objet)
        
    return render(request, 'contacts/form.html', {'form': form, 'action': 'Modifier'})

# immobilier/views.py

def contact_delete(request, pk):
    """
    Permet de supprimer un contact.
    """
    objet = get_object_or_404(Contact, pk=pk, proprietaire=request.user)
    
    if request.method == 'POST':
        objet.delete()
        return redirect('contact_list')
        
    return render(request, 'contacts/confirm_delete.html', {'objet': objet})


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
        # La ligne cruciale pour la modification
        form = ProprieteForm(instance=objet) 
    return render(request, 'proprietes/form.html', {'form': form, 'objet': objet, 'action': 'Modifier'})

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


@login_required
def mes_messages(request, contact_pk=None):
    """
    Vue principale pour le système de messagerie.
    Affiche la liste des conversations et le contenu d'une conversation spécifique.
    """
    if not request.user.is_authenticated:
        return redirect('login') # Redirige vers la page de connexion
    
    utilisateur = Utilisateur.objects.get(pk=request.user.id)

    # Récupérer les conversations (fils de discussion) de l'utilisateur
    # L'utilisateur peut être l'expéditeur initial (utilisateur) ou le destinataire (propriétaire)
    conversations = Contact.objects.filter(
        Q(utilisateur=utilisateur) | Q(proprietaire=utilisateur)
    ).order_by('-date_envoi')

    messages_du_fil = []
    contact_actuel = None
    
    if contact_pk:
        # Si un ID de contact est fourni dans l'URL, on récupère ce fil de discussion
        contact_actuel = get_object_or_404(Contact, pk=contact_pk)
        
        # S'assurer que l'utilisateur a le droit d'accéder à ce fil
        if contact_actuel.utilisateur != utilisateur and contact_actuel.proprietaire != utilisateur:
            return redirect('mes_messages') # Redirection vers la liste s'il n'a pas les droits
            
        # Récupérer tous les messages liés à ce fil de discussion
        messages_du_fil = Message.objects.filter(contact=contact_actuel).order_by('date_envoi')
        
    context = {
        'utilisateur': utilisateur,
        'conversations': conversations,
        'messages': messages_du_fil,
        'contact_actuel': contact_actuel,
    }
    
    return render(request, 'messages/messages.html', context)

def send_message(request, contact_pk):
    if request.method == 'POST' and request.user.is_authenticated:
        contact = get_object_or_404(Contact, pk=contact_pk)
        contenu = request.POST.get('contenu')
        
        if contenu:
            Message.objects.create(
                contact=contact,
                expediteur=Utilisateur.objects.get(pk=request.user.id),
                destinataire=contact.proprietaire if contact.utilisateur == Utilisateur.objects.get(pk=request.user.id) else contact.utilisateur,
                contenu=contenu
            )
    return redirect('mes_messages_detail', contact_pk=contact_pk)



def success_page(request):
    return render(request, 'success_message.html')
    
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
        # C'est ici que se trouve l'erreur la plus probable.
        # Vous devez ajouter 'request.FILES' pour que les fichiers soient traités.
        form = InformationForm(request.POST, request.FILES, instance=objet)
        
        if form.is_valid():
            form.save()
            return redirect('information_list') # Redirection vers la liste
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

def abaut(request):
    objets = Information.objects.all()
    return render(request,'about.html', {'objets': objets} ) 




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
# def mes_messages(request):
#     return render(request, 'immobilier/mes_messages.html' )

def courte_video(request):
    return render(request,'immobilier/courte_video.html' )

# def abaut(request):
#     return render(request,'immobilier/about.html' ) 
 
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