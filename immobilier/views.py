from pyexpat.errors import messages
from urllib import request
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, generics
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.db.models import Sum, Count, Q
from datetime import date
from django.utils import timezone # 👈 NOUVEAU: Import pour gérer la date/heure
from django.contrib.auth import logout
from .forms import UtilisateurModificationForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

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
     ProprieteForm, AnnonceForm, TransactionForm,
    VisiteForm, AlerteForm, ActiviteForm, MessageForm, InformationForm, TemoignageForm,ContactForm,UtilisateurCreationForm
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
def inscription(request):
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST, request.FILES)
        if form.is_valid():
            utilisateur = form.save()
            
            # ✅ Ajout du backend manquant :
            utilisateur.backend = 'django.contrib.auth.backends.ModelBackend'

            login(request, utilisateur)
            return redirect('connexion')  # ou ta page d'accueil
    else:
        form = UtilisateurCreationForm()

    return render(request, 'utilisateurs/inscription.html', {'form': form})

@login_required(login_url='connexion')
def modifier_profil(request):
    
    instance_utilisateur = request.user 
    
    if request.method == 'POST':
        # 🟢 Utilisation du NOUVEAU formulaire de modification 🟢
        form = UtilisateurModificationForm(
            request.POST, 
            request.FILES, 
            instance=instance_utilisateur # <-- RÉSOUD l'erreur d'unicité du nom d'utilisateur
        )
        
        if form.is_valid():
            form.save()
            # 💡 Optionnel : Ajouter un message de succès (messages.success(request, 'Profil mis à jour!'))
            return redirect('profil') 
        
    else:
        # Utilisation du NOUVEAU formulaire pour le pré-remplissage
        form = UtilisateurModificationForm(instance=instance_utilisateur)

    context = {
        'form': form,
        'action': 'Modifier',
        'utilisateur': instance_utilisateur,
    }
    
    return render(request, 'utilisateurs/modifier_profil.html', context)

from .forms import UserLoginForm
def deconnexion(request):
    logout(request)
    return redirect('index') 

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirection selon rôle
            if user.is_superuser:
                return redirect('index')  # page_accueil gère le contexte
            elif user.role == 'proprietaire':
                return redirect('index')  # ou vers ton dashboard
            else:
                return redirect('index')  # client

    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})



# Vues générales du site
def page_accueil(request):
    user_role = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user_role = "admin"
        elif request.user.role == "proprietaire":
            user_role = "proprietaire"
        elif request.user.role == "admin":
            user_role = "admin"
        else:
            user_role = "client"

    proprietes_recentes = Propriete.objects.filter(
        Q(statut='disponible') | Q(statut='en_netoyage') | Q(statut='en_construction')
    ).annotate(
        nb_vues=Count('visites', distinct=True)
    ).order_by('-date_publication')[:6]

    context = {
        "user_role": user_role,
        "proprietes_recentes": proprietes_recentes,
    }

    return render(request, "index.html", context)


def proprietes_maison(request):
    # Récupère toutes les propriétés où le type est 'Maison'
    proprietes = Propriete.objects.filter(type__iexact='maison').annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    # Assurez-vous d'avoir un template 'maison.html' si vous ne voulez pas utiliser 'index.html'
    return render(request, 'index.html', context)



def proprietes_Terrain(request):
    # Récupère toutes les propriétés où le type est 'Maison'
    proprietes = Propriete.objects.filter(type='terrain').annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    # Assurez-vous d'avoir un template 'maison.html' si vous ne voulez pas utiliser 'index.html'
    return render(request, 'index.html', context)

def magasin(request):
    # Récupère toutes les propriétés où le type est 'Maison'
    proprietes = Propriete.objects.filter(type='magasin').annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    # Assurez-vous d'avoir un template 'maison.html' si vous ne voulez pas utiliser 'index.html'
    return render(request, 'index.html', context)

def proprietes_plan(request):
    # Récupère toutes les propriétés où le type est 'Maison'
    proprietes = Propriete.objects.filter(type='magasin').annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
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
    propriete = get_object_or_404(
        Propriete.objects.annotate(
            nb_vues=Count('visites', distinct=True)
        ), 
        pk=pk
    )
    
    utilisateur_connecte = None
    if request.user.is_authenticated and request.user.id:
        try:
            utilisateur_connecte = Utilisateur.objects.get(pk=request.user.id)
        except Utilisateur.DoesNotExist:
            pass

    # 🔹 Si on reçoit un POST
    if request.method == 'POST':
        print("✅ POST reçu !")

        if not request.user.is_authenticated:
            return redirect(f"{reverse('connexion')}?next={request.path}")

        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            telephone = form.cleaned_data['telephone']
            sujet = form.cleaned_data['sujet']
            message_content = form.cleaned_data['message']

            # Vérifier ou créer le contact
            contact_fil = Contact.objects.filter(
                utilisateur=utilisateur_connecte,
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

            # Créer le message
            Message.objects.create(
                contact=contact_fil,
                expediteur=utilisateur_connecte,
                destinataire=propriete.proprietaire,
                contenu=message_content
            )
            print("📨 Message créé, redirection discussion !")
            return redirect('mes_messages_detail', contact_pk=contact_fil.pk)
        else:
            print("⚠️ Erreurs formulaire :", form.errors)

    # 🔹 Si on reçoit un GET
    else:
        form = ContactForm()

    # 🔹 Propriétés similaires
    conditions = Q(type__iexact=propriete.type) | Q(commune__iexact=propriete.commune)
    if isinstance(propriete.caracteristiques, list):
        for caracteristique_nom in propriete.caracteristiques:
            conditions |= Q(caracteristiques__icontains=caracteristique_nom)

    proprietes_similaires = Propriete.objects.filter(conditions).exclude(
        pk=propriete.pk
    ).distinct()[:8]
    if request.user.is_authenticated:
        # ⚠️ On utilise directement request.user qui est l'instance Utilisateur
        client_visiteur = request.user 
        
        # 1. Le propriétaire ne compte pas ses propres vues
        if client_visiteur != propriete.proprietaire:
            try:
                # Créer l'entrée Visite
                Visite.objects.create(
                    propriete=propriete,
                    # On s'assure que c'est bien l'instance Utilisateur
                    utilisateur=client_visiteur, 
                    date_visite=timezone.now()
                )
                print(f"✅ Vue unique enregistrée pour {client_visiteur.username} sur {propriete.titre}.")
            except IntegrityError:
                # L'entrée existe déjà (vue unique à vie).
                print(f"🚫 Vue non enregistrée : existe déjà pour {client_visiteur.username}.")
                pass
    # 🔹 Contexte rendu
    context = {
        'propriete': propriete,
        'proprietes_similaires': proprietes_similaires,
        'form': form,
    }

    return render(request, 'detail_propriete.html', context)

def navbar(request):

    return render(request, 'includes/nav_bar.html')

def utilisateur_list(request):
    objets = Utilisateur.objects.all()
    return render(request, 'utilisateurs/list.html', {'objets': objets})


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


@login_required(login_url='connexion')
def propriete_list(request):
    objets = Propriete.objects.all()
    return render(request, 'proprietes/list.html', {'objets': objets})

def propriete_par_proprietaire(request, proprietaire_pk):
    proprietaire = get_object_or_404(Utilisateur, pk=proprietaire_pk)
    proprietes = Propriete.objects.filter(proprietaire=proprietaire).order_by('-date_publication')
    context = {
        'proprietaire': proprietaire,
        'proprietes': proprietes,
        'titre_page': f'Propriétés de {proprietaire.last_name} {proprietaire.first_name}', # Pour le titre de la page
         }
    return render(request, 'proprietes_par_proprietaire.html', context)


@login_required(login_url='connexion')
def propriete_create(request):
    
    is_admin = request.user.role in ('admin', 'superadmin')
    
    # Sécurité: Vérification d'autorisation
    if request.user.role not in ('proprietaire', 'admin', 'superadmin'):
        return redirect('index') # Redirige vers la page d'accueil ou une page d'erreur 403

    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES)
        
        # 🟢 CORRECTION CRUCIALE 1 (POST): Supprimer le champ avant la validation 🟢
        # Si ce n'est pas un admin, on retire le champ pour que Django l'ignore lors de la validation
        if not is_admin and 'proprietaire' in form.fields:
            del form.fields['proprietaire']
            
        if form.is_valid():
            # L'assignation manuelle de request.user empêche l'utilisateur
            # de s'attribuer la propriété à un autre compte (même si le champ était visible)
            propriete = form.save(commit=False)
            propriete.proprietaire = request.user 
            propriete.save() 
            
            if is_admin: 
                return redirect('propriete_list')
            else: 
                return redirect('mes_proprietes') 
    else:
        # Initialisation du formulaire pour la méthode GET
        form = ProprieteForm()
        
    # 🟢 CORRECTION CRUCIALE 2 (GET): Supprimer le champ avant le rendu 🟢
    # Retirer le champ de la liste des champs du formulaire avant le rendu (si l'utilisateur n'est pas admin)
    if not is_admin and 'proprietaire' in form.fields:
        del form.fields['proprietaire'] 
            
    return render(request, 'proprietes/form.html', {'form': form, 'action': 'Créer'})

@login_required(login_url='connexion')
def propriete_update(request, pk):
    objet = get_object_or_404(Propriete, pk=pk)
    is_admin = request.user.role in ('admin', 'superadmin')
    is_owner = objet.proprietaire == request.user
    
    # Sécurité: Vérification d'autorisation
    if not (is_admin or is_owner):
        return redirect('mes_proprietes')
    
    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES, instance=objet)
        
        # 🟢 CORRECTION CRUCIALE 1: Supprimer le champ avant la validation 🟢
        # Si ce n'est pas un admin, on retire le champ pour que Django l'ignore lors de la validation
        if not is_admin and 'proprietaire' in form.fields:
            del form.fields['proprietaire']
        
        if form.is_valid():
            # ... le reste de la logique de sauvegarde ...
            form.save() 
            
            if is_admin: 
                return redirect('gestion_proprietes_admin')
            else: 
                return redirect('mes_proprietes') 
    else:
        # Initialisation pour GET
        form = ProprieteForm(instance=objet) 
        
    # 🟢 CORRECTION CRUCIALE 2: Supprimer le champ AVANT le rendu (si ce n'est pas un admin) 🟢
    # Ce code est le même que celui qui était dans le bloc 'else' précédent
    if not is_admin and 'proprietaire' in form.fields:
        del form.fields['proprietaire']
        
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


@login_required(login_url='connexion')
def mes_messages(request, contact_pk=None):
    utilisateur = request.user

    # Récupérer les conversations où l'utilisateur est soit le "contact" soit le "proprietaire"
    # ET la conversation n'a pas été marquée comme "supprimée" par l'utilisateur actuel.
    conversations = Contact.objects.filter(
        Q(utilisateur=utilisateur, supprime_par_utilisateur=False) |
        Q(proprietaire=utilisateur, supprime_par_proprietaire=False)
    )

    messages_du_fil = []
    contact_actuel = None

    if contact_pk:
        contact_actuel = get_object_or_404(Contact, pk=contact_pk)

        # Vérification des droits pour accéder à cette conversation
        if contact_actuel.utilisateur != utilisateur and contact_actuel.proprietaire != utilisateur:
            return redirect('mes_messages')

        # Si l'utilisateur a marqué cette conversation comme supprimée, on la masque aussi
        if (contact_actuel.utilisateur == utilisateur and contact_actuel.supprime_par_utilisateur) or \
           (contact_actuel.proprietaire == utilisateur and contact_actuel.supprime_par_proprietaire):
            return redirect('mes_messages')
            
        # Récupérer les messages du fil
        messages_du_fil = Message.objects.filter(contact=contact_actuel).order_by('date_envoi')

    context = {
        'utilisateur': utilisateur,
        'conversations': conversations.order_by('-date_envoi'),  # C'est mieux de trier par date d'envoi que par ID
        'messages': messages_du_fil,
        'contact_actuel': contact_actuel,
    }
    return render(request, 'messages/messages.html', context)

@login_required
def supprimer_conversation(request, contact_pk):
    contact = get_object_or_404(Contact, pk=contact_pk)
    utilisateur = request.user

    if utilisateur == contact.utilisateur:
        contact.supprime_par_utilisateur = True
    elif utilisateur == contact.proprietaire:
        contact.supprime_par_proprietaire = True
    else:
        # Empêcher un utilisateur de supprimer une conversation qui n'est pas la sienne
        return redirect('mes_messages')

    contact.save()
    return redirect("mes_messages")

@login_required(login_url='login')
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

@login_required
def supprimer_message(request, message_pk, mode):
    message = get_object_or_404(Message, pk=message_pk)
    utilisateur = request.user
    contact_pk = message.contact.pk

    # L'utilisateur doit être l'expéditeur ou le destinataire du message
    if utilisateur != message.expediteur and utilisateur != message.contact.proprietaire and utilisateur != message.contact.utilisateur:
        return redirect('mes_messages_detail', contact_pk=contact_pk)

    # Logique de suppression
    if mode == 'pour_moi':
        if utilisateur == message.expediteur:
            message.supprime_par_expediteur = True
        else: # C'est le destinataire
            message.supprime_par_destinataire = True
        message.save()
    elif mode == 'pour_tous' and utilisateur == message.expediteur:
        # Seul l'expéditeur peut choisir de supprimer pour tout le monde
        message.supprime_pour_tous = True
        message.save()
    
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

def nav_bar(request):
    return render(request , 'includes/nav_bar.html' )



# les fontion pour lla partie statique à rendre dinamique




def detail_propriete(request):

    return render(request ,'immobilier/detail_propriete.html', {})



@login_required(login_url='connexion')
def superadmin(request):
    """
    Vue pour le super admin avec statistiques globales du site.
    Accessible uniquement aux super administrateurs.
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un super admin
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    # --- STATISTIQUES GLOBALES ---
    
    # 1. Statistiques principales
    total_proprietes = Propriete.objects.count()
    total_utilisateurs = Utilisateur.objects.count()
    total_vues = Visite.objects.count()
    total_messages = Message.objects.count()
    
    # 2. Propriétés à modérer (statut 'en_attente' pour Annonce ou propriétés signalées)
    # Pour Annonce avec statut 'attente'
    annonces_a_moderer = Annonce.objects.filter(statut='attente').count()
    
    # Pour propriétés qui pourraient avoir besoin de modération
    # (vous n'avez pas de statut 'signale' dans Propriete, donc on utilise Annonce)
    proprietes_a_moderer = annonces_a_moderer
    
    # 3. Utilisateurs suspendus (statut=False)
    utilisateurs_suspendus = Utilisateur.objects.filter(statut=False).count()
    
    # 4. Transactions totales
    transactions_totales = Transaction.objects.count()
    
    # 5. Alertes critiques récentes (non résolues)
    alertes_critiques = Alerte.objects.filter(
        statut='non_resolue'
    ).select_related('propriete', 'admin').order_by('-date_creation')[:10]
    
    # 6. Activité récente (dernières 24h)
    activite_recente = Activite.objects.filter(
        date_action__gte=timezone.now() - timezone.timedelta(days=1)
    ).select_related('utilisateur').order_by('-date_action')[:10]
    
    # 7. Liste des annonces à modérer
    annonces_a_moderer_liste = Annonce.objects.filter(
        statut='attente'
    ).select_related('propriete', 'utilisateur').order_by('-date_publication')[:50]
    
    # 8. Liste de tous les utilisateurs
    utilisateurs_liste = Utilisateur.objects.all().order_by('-date_joined')[:50]
    
    # 9. Statistiques par type de propriété
    from django.db.models import Count
    stats_par_type = Propriete.objects.values('type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 10. Statistiques temporelles (30 derniers jours)
    date_30_jours = timezone.now() - timezone.timedelta(days=30)
    
    # Propriétés créées dans les 30 derniers jours
    nouvelles_proprietes_30j = Propriete.objects.filter(
        date_publication__gte=date_30_jours
    ).count()
    
    # Utilisateurs inscrits dans les 30 derniers jours
    nouveaux_utilisateurs_30j = Utilisateur.objects.filter(
        date_joined__gte=date_30_jours
    ).count()
    
    # Visites dans les 30 derniers jours
    visites_30j = Visite.objects.filter(
        date_visite__gte=date_30_jours
    ).count()
    
    # 11. Top 5 des propriétés les plus vues
    top_proprietes_vues = Propriete.objects.annotate(
        nb_vues=Count('visites')
    ).order_by('-nb_vues')[:5]
    
    # 12. Top 5 des propriétaires les plus actifs
    top_proprietaires = Utilisateur.objects.filter(
        role='proprietaire'
    ).annotate(
        nb_proprietes=Count('proprietes')
    ).order_by('-nb_proprietes')[:5]
    
    # 13. Messages non lus (statut='envoye' pour non lu, 'lu' pour lu)
    messages_non_lus = Message.objects.filter(statut='envoye').count()
    
    # 14. Contacts récents (derniers 7 jours)
    contacts_recents = Contact.objects.filter(
        date_envoi__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # 15. Répartition par rôle d'utilisateur
    repartition_roles = Utilisateur.objects.values('role').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 16. Propriétés par commune
    proprietes_par_commune = Propriete.objects.values('commune').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # 17. Témoignages en attente de validation
    temoignages_en_attente = Temoignage.objects.filter(statut='attente').count()
    
    # 18. Transactions par type
    transactions_par_type = Transaction.objects.values('type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 19. Propriétés par statut
    proprietes_par_statut = Propriete.objects.values('statut').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 20. Chiffre d'affaires total (somme des transactions)
    chiffre_affaires_total = Transaction.objects.aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    # 21. Propriétés avec vidéo
    proprietes_avec_video = Propriete.objects.exclude(video='').count()
    
    # 22. Messages échangés aujourd'hui
    messages_aujourdhui = Message.objects.filter(
        date_envoi__date=timezone.now().date()
    ).count()
    
    # 23. Visites aujourd'hui
    visites_aujourdhui = Visite.objects.filter(
        date_visite__date=timezone.now().date()
    ).count()
    
    # 24. Top 5 des villes les plus populaires
    proprietes_par_ville = Propriete.objects.values('ville').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # 25. Contacts non lus
    contacts_non_lus = Contact.objects.filter(statut='non_lu').count()
    
    # 26. Alertes non résolues
    alertes_non_resolues = Alerte.objects.filter(statut='non_resolue').count()
    
    # 27. Derniers témoignages validés
    derniers_temoignages = Temoignage.objects.filter(
        statut='valide'
    ).select_related('utilisateur').order_by('-date_creation')[:5]
    
    # 28. Informations par type
    informations_par_type = Information.objects.values('type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 29. Utilisateurs par statut
    utilisateurs_par_statut = Utilisateur.objects.values('statut').annotate(
        count=Count('id')
    )
    
    # 30. Annonces par statut
    annonces_par_statut = Annonce.objects.values('statut').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Préparation du contexte
    context = {
        # --- STATISTIQUES PRINCIPALES ---
        'total_proprietes': total_proprietes,
        'total_utilisateurs': total_utilisateurs,
        'total_vues': total_vues,
        'total_messages': total_messages,
        
        # --- MODÉRATION ---
        'proprietes_a_moderer': proprietes_a_moderer,
        'annonces_a_moderer': annonces_a_moderer,
        'utilisateurs_suspendus': utilisateurs_suspendus,
        'transactions_totales': transactions_totales,
        
        # --- DONNÉES POUR LES TABLEAUX ---
        'alertes_critiques': alertes_critiques,
        'activite_recente': activite_recente,
        'annonces_a_moderer_liste': annonces_a_moderer_liste,
        'utilisateurs_liste': utilisateurs_liste,
        
        # --- STATISTIQUES DÉTAILLÉES ---
        'stats_par_type': stats_par_type,
        'nouvelles_proprietes_30j': nouvelles_proprietes_30j,
        'nouveaux_utilisateurs_30j': nouveaux_utilisateurs_30j,
        'visites_30j': visites_30j,
        
        # --- TOPS ET CLASSEMENTS ---
        'top_proprietes_vues': top_proprietes_vues,
        'top_proprietaires': top_proprietaires,
        'proprietes_par_ville': proprietes_par_ville,
        'derniers_temoignages': derniers_temoignages,
        
        # --- STATISTIQUES DIVERSES ---
        'messages_non_lus': messages_non_lus,
        'contacts_recents': contacts_recents,
        'repartition_roles': repartition_roles,
        'proprietes_par_commune': proprietes_par_commune,
        'temoignages_en_attente': temoignages_en_attente,
        'transactions_par_type': transactions_par_type,
        'proprietes_par_statut': proprietes_par_statut,
        'chiffre_affaires_total': chiffre_affaires_total,
        'proprietes_avec_video': proprietes_avec_video,
        'messages_aujourdhui': messages_aujourdhui,
        'visites_aujourdhui': visites_aujourdhui,
        'contacts_non_lus': contacts_non_lus,
        'alertes_non_resolues': alertes_non_resolues,
        'informations_par_type': informations_par_type,
        'utilisateurs_par_statut': utilisateurs_par_statut,
        'annonces_par_statut': annonces_par_statut,
        
        # --- INFO UTILISATEUR ---
        'user': user,
        
        # --- DATES POUR LES FILTRES ---
        'today': timezone.now().date(),
        'date_30_jours': date_30_jours.date(),
    }
    
    return render(request, 'immobilier/superadmin.html', context)


@login_required(login_url='connexion')
def gestion_utilisateurs_admin(request):
    """
    Page admin pour gérer tous les utilisateurs avec leurs informations complètes.
    Accessible uniquement aux super administrateurs et administrateurs.
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un admin
    if not user.is_superuser and user.role not in ["superadmin", "admin"]:
        return redirect('index')
    
    # Importer les fonctions nécessaires
    from django.db.models import Q, Value
    from django.db.models.functions import Concat
    
    # Récupérer tous les utilisateurs avec annotation pour nom_complet
    utilisateurs = Utilisateur.objects.annotate(
        nom_complet=Concat('first_name', Value(' '), 'last_name')
    ).order_by('-date_joined')
    
    # Récupérer le paramètre de recherche
    search_query = request.GET.get('q', '').strip()
    
    # Appliquer la recherche textuelle
    if search_query:
        search_lower = search_query.lower()
        
        # Créer une requête Q complète
        q_objects = Q()
        
        # Chercher dans tous les champs
        q_objects |= Q(username__icontains=search_query)
        q_objects |= Q(email__icontains=search_query)
        q_objects |= Q(telephone__icontains=search_query)
        q_objects |= Q(first_name__icontains=search_query)
        q_objects |= Q(last_name__icontains=search_query)
        
        # Chercher dans le nom_complet annoté
        q_objects |= Q(nom_complet__icontains=search_query)
        
        # Mapping pour la recherche par rôle (français/anglais)
        role_search_map = {
            'client': ['client', 'clients', 'acheteur', 'acheteurs'],
            'proprietaire': ['proprietaire', 'propriétaire', 'propriétaires', 'vendeur', 'vendeurs'],
            'admin': ['admin', 'administrateur', 'administrateurs', 'gestionnaire'],
            'superadmin': ['superadmin', 'superadministrateur', 'super administrateur', 'superuser'],
        }
        
        # Vérifier chaque rôle
        for role_key, search_terms in role_search_map.items():
            if any(term in search_lower for term in search_terms):
                q_objects |= Q(role=role_key)
                break
        
        # Recherche par statut
        if any(term in search_lower for term in ['actif', 'actifs', 'actifes', 'actives']):
            q_objects |= Q(statut=True)
        elif any(term in search_lower for term in ['inactif', 'inactifs', 'inactives', 'désactivé', 'desactive']):
            q_objects |= Q(statut=False)
        
        # Recherche par superuser
        if 'superuser' in search_lower or 'super utilisateur' in search_lower:
            q_objects |= Q(is_superuser=True)
        
        # Appliquer le filtre
        utilisateurs = utilisateurs.filter(q_objects).distinct()
    
    # ... reste du code inchangé (statistiques, pagination, contexte)
    
    # Récupérer les valeurs distinctes pour les statistiques
    roles_distincts = Utilisateur.objects.values_list('role', flat=True).distinct()
    
    # Statistiques (sur les utilisateurs filtrés)
    total_users_count = utilisateurs.count()
    utilisateurs_actifs = utilisateurs.filter(statut=True).count()
    utilisateurs_admin = utilisateurs.filter(
        Q(role='admin') | Q(role='superadmin') | Q(is_superuser=True)
    ).count()
    utilisateurs_proprietaires = utilisateurs.filter(role='proprietaire').count()
    utilisateurs_clients = utilisateurs.filter(role='client').count()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(utilisateurs, 50)  # 50 utilisateurs par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'utilisateurs': page_obj,
        'user': user,
        'utilisateurs_actifs': utilisateurs_actifs,
        'utilisateurs_admin': utilisateurs_admin,
        'utilisateurs_proprietaires': utilisateurs_proprietaires,
        'utilisateurs_clients': utilisateurs_clients,
        'search_query': search_query,
        'roles_distincts': roles_distincts,
        'total_users_count': total_users_count,
    }
    
    return render(request, 'immobilier/gestion_utilisateurs.html', context)

@login_required(login_url='connexion')
def modifier_utilisateur_admin(request, pk):
    """
    Permet à un admin de modifier n'importe quel utilisateur.
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un admin
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    # Récupérer l'utilisateur à modifier
    utilisateur_a_modifier = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        form = UtilisateurModificationForm(
            request.POST, 
            request.FILES, 
            instance=utilisateur_a_modifier
        )
        
        if form.is_valid():
            form.save()
            # Message de succès (si vous utilisez les messages Django)
            # messages.success(request, f"Utilisateur {utilisateur_a_modifier.username} modifié avec succès.")
            return redirect('gestion_utilisateurs_admin')
    else:
        form = UtilisateurModificationForm(instance=utilisateur_a_modifier)
    
    context = {
        'form': form,
        'action': 'Modifier',
        'utilisateur': utilisateur_a_modifier,
        'user': user,
    }
    
    return render(request, 'immobilier/modifier_profil_admin.html', context)

@login_required(login_url='connexion')
def supprimer_utilisateur_admin(request, pk):
    """
    Permet à un admin de supprimer n'importe quel utilisateur.
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un admin
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    utilisateur_a_supprimer = get_object_or_404(Utilisateur, pk=pk)
    
    # Empêcher un admin de se supprimer lui-même
    if utilisateur_a_supprimer == user:
        # messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('gestion_utilisateurs_admin')
    
    if request.method == 'POST':
        username = utilisateur_a_supprimer.username
        utilisateur_a_supprimer.delete()
        # messages.success(request, f"Utilisateur {username} supprimé avec succès.")
        return redirect('gestion_utilisateurs_admin')
    
    context = {
        'utilisateur': utilisateur_a_supprimer,
        'user': user,
    }
    
    return render(request, 'immobilier/confirm_delete_admin.html', context)

@login_required(login_url='connexion')
def creer_utilisateur_admin(request):
    """
    Permet à un admin de créer un nouvel utilisateur.
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un admin
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            nouvel_utilisateur = form.save()
            # messages.success(request, f"Utilisateur {nouvel_utilisateur.username} créé avec succès.")
            return redirect('gestion_utilisateurs_admin')
    else:
        form = UtilisateurCreationForm()
    
    context = {
        'form': form,
        'action': 'Créer',
        'user': user,
    }
    
    return render(request, 'immobilier/creer_utilisateur_admin.html', context)


@login_required(login_url='connexion')
def gestion_proprietes_admin(request):
    """
    Page admin pour gérer toutes les propriétés avec filtres.
    Accessible uniquement aux super administrateurs et administrateurs.
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un admin
    if not user.is_superuser and user.role not in ["superadmin", "admin"]:
        return redirect('index')
    
    # Récupérer toutes les propriétés
    proprietes = Propriete.objects.all().order_by('-date_publication')
    
    # Appliquer les filtres
    proprietaire_filter = request.GET.get('proprietaire')
    type_filter = request.GET.get('type')
    statut_filter = request.GET.get('statut')
    commune_filter = request.GET.get('commune')
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    
    # Récupérer le nom du propriétaire filtré (pour l'affichage)
    proprietaire_nom = None
    
    if proprietaire_filter:
        # Vérifier que le propriétaire existe
        try:
            proprietaire_obj = Utilisateur.objects.get(id=proprietaire_filter)
            proprietaire_nom = proprietaire_obj.get_full_name() or proprietaire_obj.username
            # Filtrer les propriétés de ce propriétaire
            proprietes = proprietes.filter(proprietaire=proprietaire_obj)
        except Utilisateur.DoesNotExist:
            # Si le propriétaire n'existe pas, on ne filtre pas
            proprietaire_nom = "Propriétaire inconnu"
    
    if type_filter:
        proprietes = proprietes.filter(type=type_filter)
    
    if statut_filter:
        proprietes = proprietes.filter(statut=statut_filter)
    
    if commune_filter:
        proprietes = proprietes.filter(commune__icontains=commune_filter)
    
    if prix_min:
        proprietes = proprietes.filter(prix__gte=prix_min)
    
    if prix_max:
        proprietes = proprietes.filter(prix__lte=prix_max)
    
    # Statistiques
    total_proprietes = Propriete.objects.count()
    proprietes_disponibles = Propriete.objects.filter(statut='disponible').count()
    proprietes_vendues = Propriete.objects.filter(statut='vendu').count()
    proprietes_reservees = Propriete.objects.filter(statut='reserve').count()
    
    from django.db.models import Avg
    prix_moyen = Propriete.objects.aggregate(Avg('prix'))['prix__avg'] or 0
    
    # Propriétaires distincts pour le filtre
    proprietaires_distincts = Utilisateur.objects.filter(
        role='proprietaire'
    ).distinct()
    
    # Types distincts
    types_distincts = Propriete.objects.values_list('type', flat=True).distinct()
    
    # Communes distinctes
    communes_distinctes = Propriete.objects.values_list('commune', flat=True).distinct()
    
    # Statuts distincts
    statuts_distincts = Propriete.objects.values_list('statut', flat=True).distinct()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(proprietes, 50)  # 50 propriétés par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'proprietes': page_obj,
        'user': user,
        'total_proprietes': total_proprietes,
        'proprietes_disponibles': proprietes_disponibles,
        'proprietes_vendues': proprietes_vendues,
        'proprietes_reservees': proprietes_reservees,
        'prix_moyen': prix_moyen,
        'proprietaires_distincts': proprietaires_distincts,
        'types_distincts': types_distincts,
        'communes_distinctes': communes_distinctes,
        'statuts_distincts': statuts_distincts,
        'filters': {
            'proprietaire': proprietaire_filter,
            'type': type_filter,
            'statut': statut_filter,
            'commune': commune_filter,
            'prix_min': prix_min,
            'prix_max': prix_max,
        },
        'proprietaire_nom': proprietaire_nom,  # Pour l'affichage dans le résumé
    }
    
    return render(request, 'immobilier/gestion_proprietes.html', context)

@login_required(login_url='connexion')
def propriete_update_admin(request, pk):
    """
    Mise à jour d'une propriété PAR L'ADMIN
    """
    
    # Récupérer la propriété
    propriete = get_object_or_404(Propriete, pk=pk)
    
    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES, instance=propriete)
        
        if form.is_valid():
            form.save()
            return redirect('gestion_proprietes_admin')
    else:
        form = ProprieteForm(instance=propriete)
    
    return render(request, 'proprietes/form.html', {
        'form': form,
        'objet': propriete,
        'action': 'Modifier'
    })

@login_required(login_url='connexion')
def export_proprietes_pdf(request):
    """Export des propriétés en PDF"""
    user = request.user
    
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    proprietes = Propriete.objects.all().order_by('-date_publication')
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Titre
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Liste des Propriétés - IMMO ABIDJAN")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Export du {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Contenu
    y = 700
    for i, propriete in enumerate(proprietes):
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750
        
        p.drawString(100, y, f"{propriete.id}. {propriete.titre}")
        p.drawString(400, y, f"{propriete.prix} FCFA")
        y -= 20
    
    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="proprietes_export.pdf"'
    return response

@login_required(login_url='connexion')
def toggle_statut_utilisateur(request, pk):
    """
    Active ou désactive un utilisateur (toggle du statut).
    """
    user = request.user
    
    # Vérifier que l'utilisateur est un admin
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    utilisateur_cible = get_object_or_404(Utilisateur, pk=pk)
    
    # Empêcher un admin de se désactiver lui-même
    if utilisateur_cible == user:
        # messages.error(request, "Vous ne pouvez pas modifier votre propre statut.")
        return redirect('gestion_utilisateurs_admin')
    
    # Inverser le statut
    utilisateur_cible.statut = not utilisateur_cible.statut
    utilisateur_cible.save()
    
    action = "activé" if utilisateur_cible.statut else "désactivé"
    # messages.success(request, f"Utilisateur {utilisateur_cible.username} {action}.")
    
    return redirect('gestion_utilisateurs_admin')



def proprietaire_parametres(request):
    return render(request, 'immobilier/parametres_proprietaire.html' )
 

def temoingnages(request):
    return render(request,'immobilier/temoingnages.html' ) 


def espace_client(request):
    return render(request, 'espace_client.html')




@login_required(login_url='connexion')
def profil(request):
    user = request.user  # utilisateur actuellement connecté
    return render(request, 'profil.html', {'user': user})

@login_required(login_url='connexion')
def proprietaire(request):
    user = request.user
    
    if user.role != "proprietaire":
        return redirect('index') 
    
    proprietes_owner = user.proprietes.all()
    proprietes_en_ligne = proprietes_owner.count()
    today = timezone.now().date() 

    # --- 1. Calculs pour les cartes (Totaux à vie/globaux) ---
    
    # 💡 Propriétés en ligne: Reste le total
    
    # Vues totales uniques (compte toutes les Visites pour les propriétés du user)
    # Grâce à la contrainte dans models.py, chaque entrée Visite est une vue unique à vie.
    vues_totales_global = Visite.objects.filter(propriete__in=proprietes_owner).count()

    # Conversations uniques (compte tous les Contacts pour les propriétés du user)
    messages_uniques_global = Contact.objects.filter(
        proprietaire=user,
        propriete__isnull=False # Filtre uniquement les contacts liés à une propriété
    ).count()

    # --- 2. Préparation du tableau (Statistiques par propriété, globales) ---
    
    proprietes_details = []
    
    # Agrégation des statistiques pour toutes les propriétés en UNE SEULE requête pour l'efficacité
    stats = proprietes_owner.annotate(
        nb_vues_uniques=Count('visites', distinct=True),
        nb_conversations=Count('contacts_propriete', filter=Q(contacts_propriete__propriete__isnull=False), distinct=True)
    )

    for prop in stats:
        proprietes_details.append({
            'titre': prop.titre,
            # date_publication est le champ de date d'ajout sur votre modèle Propriete
            'date_ajout': prop.date_publication.strftime('%d/%m/%Y'),
            # Statistiques globales agrégées
            'nb_vues': prop.nb_vues_uniques,
            'nb_messages': prop.nb_conversations,
            'url_detail': prop.get_absolute_url() if hasattr(prop, 'get_absolute_url') else '#'
        })
        
        
    context = {
        'proprietes_en_ligne': proprietes_en_ligne,
        'vues_totales': vues_totales_global,       # Pour la carte des vues
        'messages_uniques': messages_uniques_global, # Pour la carte des messages
        'proprietes_details': proprietes_details,
        'today_date': today
    }

    return render(request, 'immobilier/proprietaire.html', context)

@login_required(login_url='connexion')
def mes_proprietes(request):
    """
    Affiche toutes les propriétés appartenant au propriétaire connecté.
    """
    user = request.user  # utilisateur connecté

    # Vérifie que l'utilisateur est bien un propriétaire
    if hasattr(user, 'role') and user.role != 'proprietaire':
        return render(request, 'erreur.html', {'message': "Accès réservé aux propriétaires."})

    # On récupère toutes les propriétés de ce propriétaire
    proprietes = Propriete.objects.filter(proprietaire=user).order_by('-date_publication')

    # Envoi au template
    return render(request, 'proprietes/mes_proprietes.html', {'proprietes': proprietes})