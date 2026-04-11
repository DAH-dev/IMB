# from pyexpat.errors import messages
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
import random
import json
from datetime import datetime, timedelta
from django.contrib import messages


from .models import (
    Utilisateur, Propriete, 
    Visite,  Message, Contact
)
from .serializers import (
    UtilisateurSerializer, ProprieteSerializer, 
    VisiteSerializer, 
    MessageSerializer,ContactSerializer
)
from .forms import (
     ProprieteForm, 
    VisiteForm,  MessageForm, ContactForm,UtilisateurCreationForm
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


class VisiteViewSet(viewsets.ModelViewSet):
    queryset = Visite.objects.all()
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]



class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]



class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UtilisateurSerializer

# --- VUES POUR LE SITE WEB (HTML) ---
# views.py - Remplacer la fonction inscription

import random
import requests
from datetime import timedelta
from django.utils import timezone

def generate_otp():
    """Génère un code OTP à 6 chiffres"""
    return f"{random.randint(100000, 999999)}"

def send_sms(phone_number, code):
    """
    Envoie un SMS via un service.
    Pour le moment, on simule l'envoi.
    À remplacer par un vrai service SMS (Twilio, Africa's Talking, etc.)
    """
    # TODO: Remplacer par un vrai service SMS
    print(f"📱 SMS envoyé à {phone_number} : Votre code est {code}")
    
    # Simuler un envoi réussi
    return True

# from twilio.rest import Client

# def send_sms(telephone, otp):
#     account_sid = 'TON_SID'
#     auth_token = 'TON_TOKEN'
#     client = Client(account_sid, auth_token)

#     try:
#         message = client.messages.create(
#             body=f"Votre code OTP est : {otp}",
#             from_='+1234567890',  # numéro Twilio
#             to=telephone
#         )
#         return True
#     except Exception as e:
#         print("Erreur SMS:", e)
#         return False

def inscription(request):
    """Étape 1 : Formulaire d'inscription"""
    if request.method == 'POST':
        print("🔵 ========== DÉBUT POST INSCRIPTION ==========")
        print("🔵 Données POST reçues:", request.POST)
        print("🔵 Fichiers reçus:", request.FILES)
        
        form = UtilisateurCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("✅ FORMULAIRE VALIDE")
            
            # Vérifier si le téléphone existe déjà
            telephone = form.cleaned_data.get('telephone')
            print(f"📞 Téléphone: {telephone}")
            
            if Utilisateur.objects.filter(telephone=telephone).exists():
                print("❌ Téléphone déjà utilisé")
                messages.error(request, "Ce numéro de téléphone est déjà utilisé.")
                return render(request, 'utilisateurs/inscription.html', {'form': form})
            
            # Sauvegarder les données en session (pas les fichiers)
            # Pour les fichiers, on les garde temporairement ailleurs
            request.session['inscription_data'] = {
                'username': form.cleaned_data.get('username'),
                'email': form.cleaned_data.get('email'),
                'first_name': form.cleaned_data.get('first_name'),
                'last_name': form.cleaned_data.get('last_name'),
                'telephone': telephone,
                'password': form.cleaned_data.get('password1'),
                'role': form.cleaned_data.get('role', 'client'),
            }
            print("📦 Données texte sauvegardées en session")
            
            # Pour les fichiers, on les sauvegarde dans des variables temporaires
            # ou on les garde dans request.FILES pour la prochaine étape
            # Solution simple : sauvegarder les fichiers temporairement dans un dossier
            import os
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            # Créer un dossier temporaire pour les fichiers
            temp_dir = 'temp_uploads/'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Sauvegarder la photo temporairement
            if 'photo' in request.FILES and request.FILES['photo']:
                photo_file = request.FILES['photo']
                photo_path = default_storage.save(
                    f'{temp_dir}{photo_file.name}', 
                    ContentFile(photo_file.read())
                )
                request.session['temp_photo_path'] = photo_path
                print(f"📸 Photo sauvegardée temporairement: {photo_path}")
                # Remettre le curseur du fichier au début pour le formulaire
                photo_file.seek(0)
            
            # Sauvegarder la CNI temporairement
            if 'cni' in request.FILES and request.FILES['cni']:
                cni_file = request.FILES['cni']
                cni_path = default_storage.save(
                    f'{temp_dir}{cni_file.name}', 
                    ContentFile(cni_file.read())
                )
                request.session['temp_cni_path'] = cni_path
                print(f"🪪 CNI sauvegardée temporairement: {cni_path}")
                cni_file.seek(0)
            
            # Générer et envoyer OTP
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['otp_created_at'] = timezone.now().isoformat()
            request.session['telephone'] = telephone
            print(f"🔐 OTP généré: {otp}")
            print(f"⏰ Créé à: {request.session['otp_created_at']}")
            
            # Envoyer le SMS
            print(f"📱 Envoi SMS à {telephone} avec code {otp}")
            if send_sms(telephone, otp):
                print("✅ SMS envoyé avec succès")
                print("➡️ Redirection vers inscription_otp")
                return redirect('inscription_otp')
            else:
                print("❌ Erreur lors de l'envoi du SMS")
                messages.error(request, "Erreur lors de l'envoi du SMS. Vérifiez votre numéro.")
                return render(request, 'utilisateurs/inscription.html', {'form': form})
        else:
            print("❌ FORMULAIRE INVALIDE")
            print("Erreurs du formulaire:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {errors}")
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            return render(request, 'utilisateurs/inscription.html', {'form': form})
    
    else:
        print("🟢 GET sur la page d'inscription")
        form = UtilisateurCreationForm()
    
    return render(request, 'utilisateurs/inscription.html', {'form': form})

# views.py - Ajouter cette fonction

def inscription_otp(request):
    """Étape 2 : Vérification du code OTP"""
    
    # Vérifier que les données existent en session
    if 'inscription_data' not in request.session:
        return redirect('inscription')
    
    telephone = request.session.get('telephone')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        saved_otp = request.session.get('otp')
        otp_created = request.session.get('otp_created_at')
        
        # Vérifier si le code n'est pas expiré (5 minutes)
        if otp_created:
            otp_created = datetime.fromisoformat(otp_created)
            if timezone.now() > otp_created + timedelta(minutes=5):
                messages.error(request, "Le code a expiré. Veuillez demander un nouveau code.")
                return redirect('inscription')
        
        if otp_code == saved_otp:
            # Code correct : créer l'utilisateur
            data = request.session['inscription_data']
            
            # Récupérer les fichiers temporaires
            from django.core.files import File
            import os
            
            user = Utilisateur(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                telephone=data['telephone'],
                role=data['role'],
                phone_verified=True
            )
            
            # Récupérer la photo temporaire
            temp_photo_path = request.session.get('temp_photo_path')
            if temp_photo_path and os.path.exists(temp_photo_path):
                with open(temp_photo_path, 'rb') as f:
                    user.photo.save(os.path.basename(temp_photo_path), File(f), save=False)
                os.remove(temp_photo_path)
            
            # Récupérer la CNI temporaire
            temp_cni_path = request.session.get('temp_cni_path')
            if temp_cni_path and os.path.exists(temp_cni_path):
                with open(temp_cni_path, 'rb') as f:
                    user.cni.save(os.path.basename(temp_cni_path), File(f), save=False)
                os.remove(temp_cni_path)
            
            # Sauvegarder l'utilisateur
            user.set_password(data['password'])
            user.save()
            
            # Nettoyer la session
            del request.session['inscription_data']
            del request.session['otp']
            del request.session['otp_created_at']
            del request.session['telephone']
            if 'temp_photo_path' in request.session:
                del request.session['temp_photo_path']
            if 'temp_cni_path' in request.session:
                del request.session['temp_cni_path']
            
            # Connecter l'utilisateur
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur IMB Immobilier.")
            return redirect('index')
        else:
            messages.error(request, "Code incorrect. Veuillez réessayer.")
            # Incrémenter les tentatives
            attempts = request.session.get('otp_attempts', 0) + 1
            request.session['otp_attempts'] = attempts
            if attempts >= 3:
                messages.error(request, "Trop de tentatives. Veuillez recommencer l'inscription.")
                return redirect('inscription')
    
    return render(request, 'utilisateurs/inscription_otp.html', {'telephone': telephone})

@csrf_exempt
def resend_otp(request):
    """Renvoie un nouveau code OTP"""
    if request.method == 'POST':
        telephone = request.session.get('telephone')
        
        if telephone:
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['otp_created_at'] = timezone.now().isoformat()
            request.session['otp_attempts'] = 0
            
            print(f"🔐 Nouveau OTP généré: {otp}")
            
            if send_sms(telephone, otp):
                return JsonResponse({'success': True, 'message': 'Code renvoyé avec succès'})
            else:
                return JsonResponse({'success': False, 'message': 'Erreur lors de l\'envoi'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Requête invalide'}, status=400)

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

@login_required(login_url='connexion')
def verifier_cni(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    
    if not utilisateur.cni:
        return redirect('gestion_utilisateurs_admin')
    
    if request.method == 'POST':
        utilisateur.cni_verifie = True
        utilisateur.cni_verifie_le = timezone.now()
        utilisateur.cni_verifie_par = request.user
        utilisateur.cni_commentaire = request.POST.get('commentaire', '')
        utilisateur.save()
        
        # messages.success(request, f"CNI de {utilisateur.username} vérifiée.")
        return redirect('gestion_utilisateurs_admin')
    
    return render(request, 'utilisateurs/verifier_cni.html', {'utilisateur': utilisateur})

def contact(request):

    return render(request, 'contact.html', {})


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

    # Compter les messages non lus
    total_non_lus = 0
    if request.user.is_authenticated:
        total_non_lus = Message.objects.filter(
            destinataire=request.user,
            statut='envoye'
        ).count()        

    # Récupérer le terme de recherche
    recherche = request.GET.get('recherche', '').strip()
    
    # Base des propriétés
    proprietes = Propriete.objects.filter(
        Q(statut='disponible') | Q(statut='en_netoyage') | Q(statut='en_construction'),
        proprietaire__statut=True,
        statut_propriete_admin=True,
        statut_propriete_owner=True
    ).annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    # ✅ RECHERCHE AVANCÉE AVEC CORRESPONDANCE PARTIELLE
    if recherche:
        # Recherche exacte ou partielle
        q_objects = Q()
        
        # Recherche dans les champs de la propriété (correspondance partielle)
        q_objects |= Q(titre__icontains=recherche)
        q_objects |= Q(description__icontains=recherche)
        q_objects |= Q(ville__icontains=recherche)
        q_objects |= Q(commune__icontains=recherche)
        q_objects |= Q(type__icontains=recherche)
        q_objects |= Q(caracteristiques__icontains=recherche)
        
        # ✅ RECHERCHE DANS LES INFORMATIONS DU PROPRIÉTAIRE
        q_objects |= Q(proprietaire__username__icontains=recherche)
        q_objects |= Q(proprietaire__first_name__icontains=recherche)
        q_objects |= Q(proprietaire__last_name__icontains=recherche)
        q_objects |= Q(proprietaire__email__icontains=recherche)
        q_objects |= Q(proprietaire__telephone__icontains=recherche)
        
        # ✅ RECHERCHE COMBINÉE POUR LES NOMS COMPLETS
        # Chercher "Jean Paul" même si c'est écrit "Jean" ou "Paul"
        parts = recherche.split()
        if len(parts) > 1:
            # Recherche du prénom et nom combinés
            q_objects |= Q(proprietaire__first_name__icontains=parts[0]) & Q(proprietaire__last_name__icontains=' '.join(parts[1:]))
            q_objects |= Q(proprietaire__first_name__icontains=parts[-1]) & Q(proprietaire__last_name__icontains=' '.join(parts[:-1]))
        
        proprietes_recentes = proprietes.filter(q_objects).distinct().order_by('-nb_vues', '-date_publication')
    else:
        proprietes_recentes = proprietes.order_by('-nb_vues', '-date_publication')
    
    context = {
        "user_role": user_role,
        "proprietes_recentes": proprietes_recentes,
        "total_non_lus": total_non_lus,
        "recherche": recherche,
        "nombre_resultats": proprietes_recentes.count(),
    }

    return render(request, "index.html", context)

def conditions_utilisation(request):
    """Affiche les conditions d'utilisation"""
    return render(request, 'legal/conditions_utilisation.html')

def politique_confidentialite(request):
    """Affiche la politique de confidentialité"""
    return render(request, 'legal/politique_confidentialite.html')

def proprietes_maison(request):
    # Récupère toutes les propriétés où le type est 'Maison' et validées
    proprietes = Propriete.objects.filter(
        type__iexact='maison',
        proprietaire__statut=True,
        statut_propriete_admin=True,   # ✅ Validé par l'admin
        statut_propriete_owner=True    # ✅ Activé par le propriétaire
    ).annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    return render(request, 'index.html', context)



def proprietes_Terrain(request):
    # Récupère toutes les propriétés où le type est 'terrain' et validées
    proprietes = Propriete.objects.filter(
        type='terrain',
        proprietaire__statut=True,
        statut_propriete_admin=True,   # ✅ Validé par l'admin
        statut_propriete_owner=True    # ✅ Activé par le propriétaire
    ).annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    return render(request, 'index.html', context)

def magasin(request):
    # Récupère toutes les propriétés où le type est 'magasin' et validées
    proprietes = Propriete.objects.filter(
        type='magasin',
        proprietaire__statut=True,
        statut_propriete_admin=True,   # ✅ Validé par l'admin
        statut_propriete_owner=True    # ✅ Activé par le propriétaire
    ).annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    return render(request, 'index.html', context)

def proprietes_plan(request):
    # Récupère toutes les propriétés où le type est 'magasin' et validées
    proprietes = Propriete.objects.filter(
        type='magasin',
        proprietaire__statut=True,
        statut_propriete_admin=True,   # ✅ Validé par l'admin
        statut_propriete_owner=True    # ✅ Activé par le propriétaire
    ).annotate(
        nb_vues=Count('visites', distinct=True)
    )
    
    context = {
        'proprietes_recentes': proprietes,
    }
    return render(request, 'index.html', context)

def video_shorts(request):
    # Filtre pour les propriétés qui ont une vidéo et sont validées
    proprietes_shorts = Propriete.objects.filter(
        proprietaire__statut=True,
        statut_propriete_admin=True,
        statut_propriete_owner=True
    ).annotate(
        nb_conversations=Count('contacts_propriete', distinct=True)  # ← Compte TOUTES les conversations
    )
    
    # Recherche
    recherche = request.GET.get('q', '').strip()
    if recherche:
        proprietes_shorts = proprietes_shorts.filter(
            Q(titre__icontains=recherche) |
            Q(description__icontains=recherche) |
            Q(ville__icontains=recherche) |
            Q(commune__icontains=recherche) |
            Q(type__icontains=recherche) |
            Q(proprietaire__username__icontains=recherche) |
            Q(proprietaire__first_name__icontains=recherche) |
            Q(proprietaire__last_name__icontains=recherche)
        )
    
    context = {
        'proprietes_shorts': proprietes_shorts,
        'recherche': recherche,
    }
    
    return render(request, 'courtes_videos.html', context)


@login_required(login_url='connexion')
def demarrer_conversation(request, propriete_pk):
    """
    Démarre une conversation pour une propriété
    """
    propriete = get_object_or_404(Propriete, pk=propriete_pk)
    utilisateur = request.user
    
    # Vérifier si une conversation existe déjà
    contact = Contact.objects.filter(
        utilisateur=utilisateur,
        propriete=propriete,
        proprietaire=propriete.proprietaire
    ).first()
    
    if not contact:
        # Créer une nouvelle conversation
        contact = Contact.objects.create(
            utilisateur=utilisateur,
            proprietaire=propriete.proprietaire,
            propriete=propriete,
            statut='non_lu'
        )
    
    return redirect('mes_messages_detail', contact_pk=contact.pk)




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

    # 🔹 Déterminer le rôle de l'utilisateur
    user_role = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user_role = "admin"
        elif hasattr(request.user, 'role') and request.user.role == "proprietaire":
            user_role = "proprietaire"
        elif hasattr(request.user, 'role') and request.user.role == "admin":
            user_role = "admin"
        else:
            user_role = "client"    

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

    # ✅ CORRECTION : Propriétés similaires (seulement celles qui sont activées ET validées)
    # On exclut la propriété actuelle et on filtre les propriétés similaires visibles
    proprietes_similaires = Propriete.objects.filter(
        conditions
    ).exclude(
        pk=propriete.pk
    ).filter(
        statut_propriete_admin=True,   # ✅ Validé par l'admin
        statut_propriete_owner=True    # ✅ Activé par le propriétaire
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
        'user_role': user_role,
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
    
    total_non_lus = 0
    if request.user.is_authenticated:
        total_non_lus = Message.objects.filter(
            destinataire=request.user,
            statut='envoye'
        ).count()
    
    proprietaire_actif = proprietaire.statut
    
    # Filtrer les propriétés du propriétaire (seulement les validées et activées)
    if proprietaire_actif or (request.user.is_authenticated and 
                              (request.user.is_superuser or request.user.role in ['admin', 'superadmin'])):
        proprietes = Propriete.objects.filter(
            proprietaire=proprietaire,
            statut_propriete_admin=True,   # ✅ Validé par l'admin
            statut_propriete_owner=True    # ✅ Activé par le propriétaire
        ).annotate(
            nb_vues=Count('visites', distinct=True)
        ).order_by('-date_publication')
    else:
        proprietes = Propriete.objects.none()
    
    context = {
        'proprietaire': proprietaire,
        'proprietes': proprietes,
        'proprietaire_actif': proprietaire_actif,
        'titre_page': f'Propriétés de {proprietaire.last_name} {proprietaire.first_name}',
        'user_role': user_role,
        'total_non_lus': total_non_lus,
    }
    return render(request, 'proprietes_par_proprietaire.html', context)

@login_required(login_url='connexion')
def propriete_create(request):
    
    is_admin = request.user.role in ('admin', 'superadmin')
    
    if request.user.role not in ('proprietaire', 'admin', 'superadmin'):
        return redirect('index')

    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES)
        
        if not is_admin and 'proprietaire' in form.fields:
            del form.fields['proprietaire']
            
        if form.is_valid():
            propriete = form.save(commit=False)
            propriete.proprietaire = request.user
            
            # ✅ LOGIQUE :
            # - Admin crée : directement validé et actif
            # - Propriétaire crée : en attente de validation admin, mais activé par lui-même
            if is_admin:
                propriete.statut_propriete_admin = True   # Validé par admin
                propriete.statut_propriete_owner = True   # Actif
            else:
                propriete.statut_propriete_admin = False  # En attente validation
                propriete.statut_propriete_owner = True   # Le propriétaire veut le publier
                
            propriete.save()
            
            if is_admin: 
                return redirect('propriete_list')
            else: 
                return redirect('mes_proprietes')
    else:
        form = ProprieteForm()
        
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
        
        if not is_admin and 'proprietaire' in form.fields:
            del form.fields['proprietaire']
        
        if form.is_valid():
            propriete = form.save(commit=False)
            
            # ✅ Si c'est le propriétaire, on ne modifie pas les statuts admin
            if is_owner and not is_admin:
                # Garder les statuts admin inchangés
                propriete.statut_propriete_admin = objet.statut_propriete_admin
                propriete.statut_propriete_owner = objet.statut_propriete_owner
            
            propriete.save()
            
            if is_admin: 
                return redirect('gestion_proprietes_admin')
            else: 
                return redirect('mes_proprietes')
    else:
        form = ProprieteForm(instance=objet)
        
    if not is_admin and 'proprietaire' in form.fields:
        del form.fields['proprietaire']
        
    return render(request, 'proprietes/form.html', {'form': form, 'objet': objet, 'action': 'Modifier'})

def propriete_delete(request, pk):
    objet = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        objet.delete()
        return redirect('propriete_list')
    return render(request, 'proprietes/confirm_delete.html', {'objet': objet})


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
    is_admin = utilisateur.is_superuser or utilisateur.role in ['admin', 'superadmin']

    # Récupérer les conversations
    if is_admin:
        conversations = Contact.objects.all()
        
        # Gestion du filtre
        user_filter = request.GET.get('user_id', '').strip()
        if user_filter:
            try:
                user_id = int(user_filter)
                conversations = conversations.filter(
                    Q(utilisateur_id=user_id) | Q(proprietaire_id=user_id)
                )
            except ValueError:
                conversations = conversations.filter(
                    Q(utilisateur__username__icontains=user_filter) |
                    Q(utilisateur__first_name__icontains=user_filter) |
                    Q(utilisateur__last_name__icontains=user_filter) |
                    Q(proprietaire__username__icontains=user_filter) |
                    Q(proprietaire__first_name__icontains=user_filter) |
                    Q(proprietaire__last_name__icontains=user_filter)
                )
    else:
        conversations = Contact.objects.filter(
            Q(utilisateur=utilisateur, supprime_par_utilisateur=False) |
            Q(proprietaire=utilisateur, supprime_par_proprietaire=False)
        )

    # ✅ Garder 'conversations' pour le template
    conversations = conversations.order_by('-date_envoi')
    
    # ✅ Ajouter les infos de non lus dans un dictionnaire séparé
    non_lus_par_conversation = {}
    total_non_lus = 0
    
    for conversation in conversations:
        count = Message.objects.filter(
            contact=conversation,
            destinataire=utilisateur,
            statut='envoye'
        ).count()
        non_lus_par_conversation[conversation.id] = count
        total_non_lus += count

    messages_du_fil = []
    contact_actuel = None

    if contact_pk:
        contact_actuel = get_object_or_404(Contact, pk=contact_pk)

        if not is_admin:
            if contact_actuel.utilisateur != utilisateur and contact_actuel.proprietaire != utilisateur:
                return redirect('mes_messages')
            
        # Marquer les messages comme lus
        Message.objects.filter(
            contact=contact_actuel,
            destinataire=utilisateur,
            statut='envoye'
        ).update(statut='lu')
        
        # ✅ Récupérer les messages en filtrant ceux qui sont supprimés
        messages_du_fil = Message.objects.filter(
            contact=contact_actuel,
            supprime_pour_tous=False  # ← Ne pas afficher les messages supprimés pour tous
        ).exclude(
            # Ne pas afficher les messages supprimés par l'expéditeur si l'utilisateur est l'expéditeur
            Q(supprime_par_expediteur=True, expediteur=utilisateur) |
            # Ne pas afficher les messages supprimés par le destinataire si l'utilisateur est le destinataire
            Q(supprime_par_destinataire=True, destinataire=utilisateur)
        ).order_by('date_envoi')

    context = {
    'utilisateur': utilisateur,
    'conversations': conversations,
    'non_lus_par_conversation': non_lus_par_conversation,  # ← Important !
    'messages': messages_du_fil,
    'contact_actuel': contact_actuel,
    'is_admin': is_admin,
    'user_filter': request.GET.get('user_id', ''),
    'filter_type': request.GET.get('filter_type', 'id'),
}
    return render(request, 'messages/messages.html', context)


@login_required
def supprimer_conversation(request, contact_pk):
    contact = get_object_or_404(Contact, pk=contact_pk)
    utilisateur = request.user

    # ✅ NOUVEAU : Vérifier si l'utilisateur est admin
    is_admin = utilisateur.is_superuser or utilisateur.role in ['admin', 'superadmin']

    # ✅ MODIFIÉ : Les admins peuvent supprimer n'importe quelle conversation
    if is_admin:
        # L'admin peut supprimer définitivement
        contact.delete()
        return redirect('mes_messages')

    # Comportement normal pour les non-admins
    if utilisateur == contact.utilisateur:
        contact.supprime_par_utilisateur = True
    elif utilisateur == contact.proprietaire:
        contact.supprime_par_proprietaire = True
    else:
        return redirect('mes_messages')

    contact.save()
    return redirect("mes_messages")


@login_required(login_url='login')
def send_message(request, contact_pk):
    if request.method == 'POST' and request.user.is_authenticated:
        contact = get_object_or_404(Contact, pk=contact_pk)
        contenu = request.POST.get('contenu')
        
        if contenu:
            is_admin = request.user.is_superuser or request.user.role in ['admin', 'superadmin']
            
            # Déterminer le destinataire
            if is_admin:
                if contact.utilisateur == request.user:
                    destinataire = contact.proprietaire
                elif contact.proprietaire == request.user:
                    destinataire = contact.utilisateur
                else:
                    destinataire = contact.proprietaire
            else:
                destinataire = contact.proprietaire if contact.utilisateur == request.user else contact.utilisateur
            
            # ✅ NOUVEAU : Créer le message avec statut 'envoye' (non lu)
            Message.objects.create(
                contact=contact,
                expediteur=request.user,
                destinataire=destinataire,
                contenu=contenu,
                statut='envoye'  # ← Important : non lu pour le destinataire
            )
    return redirect('mes_messages_detail', contact_pk=contact_pk)

# views.py
from django.http import JsonResponse

@login_required
def api_check_new_messages(request):
    """API pour vérifier les nouveaux messages"""
    conversation_id = request.GET.get('conversation_id')
    last_id = request.GET.get('last_id', 0)
    
    try:
        last_id = int(last_id)
        conversation_id = int(conversation_id)
        
        # ✅ Récupérer les messages plus récents que last_id, en excluant les supprimés
        nouveaux_messages = Message.objects.filter(
            contact_id=conversation_id,
            id__gt=last_id,
            supprime_pour_tous=False  # ← Exclure les messages supprimés pour tous
        ).exclude(
            # Exclure les messages supprimés par l'expéditeur si c'est l'utilisateur
            Q(supprime_par_expediteur=True, expediteur=request.user) |
            # Exclure les messages supprimés par le destinataire si c'est l'utilisateur
            Q(supprime_par_destinataire=True, destinataire=request.user)
        ).order_by('date_envoi')
        
        messages_data = []
        for msg in nouveaux_messages:
            messages_data.append({
                'id': msg.id,
                'contenu': msg.contenu,
                'time': msg.date_envoi.strftime('%H:%M'),
                'is_sent': msg.expediteur_id == request.user.id
            })
        
        return JsonResponse({
            'has_new': len(messages_data) > 0,
            'messages': messages_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@login_required
def supprimer_message(request, message_pk, mode):
    message = get_object_or_404(Message, pk=message_pk)
    utilisateur = request.user
    contact_pk = message.contact.pk
    
    # Vérifier si l'utilisateur est admin
    is_admin = utilisateur.is_superuser or (hasattr(utilisateur, 'role') and utilisateur.role in ['admin', 'superadmin'])

    # L'utilisateur doit être l'expéditeur, le destinataire ou admin
    if not (is_admin or utilisateur == message.expediteur or utilisateur == message.destinataire):
        return redirect('mes_messages_detail', contact_pk=contact_pk)

    # Logique de suppression
    if mode == 'pour_moi':
        # Supprimer seulement pour l'utilisateur actuel
        if utilisateur == message.expediteur:
            message.supprime_par_expediteur = True
        elif utilisateur == message.destinataire:
            message.supprime_par_destinataire = True
        message.save()
        
    elif mode == 'pour_tous':
        # Supprimer pour tout le monde (admin ou expéditeur)
        if is_admin or utilisateur == message.expediteur:
            message.supprime_pour_tous = True
            message.save()
    
    return redirect('mes_messages_detail', contact_pk=contact_pk)


def abaut(request):
    objets = Information.objects.all()
    return render(request,'about.html', {'objets': objets} ) 



# les fontion pour lla partie statique à rendre dinamique




def detail_propriete(request):

    return render(request ,'immobilier/detail_propriete.html', {})




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
    user = request.user
    
    if not user.is_superuser and user.role != "superadmin" and user.role != "admin":
        return redirect('index')
    
    utilisateur_a_modifier = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        form = UtilisateurModificationForm(
            request.POST, 
            request.FILES, 
            instance=utilisateur_a_modifier
        )
        
        if form.is_valid():
            form.save()
            return redirect('gestion_utilisateurs_admin')
        else:
            print("ERREURS FORMULAIRE :", form.errors)  # 👈 IMPORTANT
    else:
        form = UtilisateurModificationForm(instance=utilisateur_a_modifier)
    
    return render(request, 'immobilier/modifier_profil_admin.html', {
        'form': form,
        'utilisateur': utilisateur_a_modifier,
        'user': user,
    })

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
    """
    user = request.user
    
    if not user.is_superuser and user.role not in ["superadmin", "admin"]:
        return redirect('index')
    
    proprietes = Propriete.objects.all().order_by('-date_publication')
    
    # Appliquer les filtres
    proprietaire_filter = request.GET.get('proprietaire')
    type_filter = request.GET.get('type')
    statut_filter = request.GET.get('statut')
    commune_filter = request.GET.get('commune')
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    statut_propriete_admin_filter = request.GET.get('statut_admin')
    statut_propriete_owner_filter = request.GET.get('statut_owner')
    
    proprietaire_nom = None
    
    if proprietaire_filter:
        try:
            proprietaire_obj = Utilisateur.objects.get(id=proprietaire_filter)
            proprietaire_nom = proprietaire_obj.get_full_name() or proprietaire_obj.username
            proprietes = proprietes.filter(proprietaire=proprietaire_obj)
        except Utilisateur.DoesNotExist:
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
    
    # ✅ Filtres pour les statuts
    if statut_propriete_admin_filter == 'valide':
        proprietes = proprietes.filter(statut_propriete_admin=True)
    elif statut_propriete_admin_filter == 'attente':
        proprietes = proprietes.filter(statut_propriete_admin=False)
    
    if statut_propriete_owner_filter == 'active':
        proprietes = proprietes.filter(statut_propriete_owner=True)
    elif statut_propriete_owner_filter == 'inactive':
        proprietes = proprietes.filter(statut_propriete_owner=False)
    
    # Statistiques
    total_proprietes = Propriete.objects.count()
    proprietes_disponibles = Propriete.objects.filter(statut='disponible').count()
    proprietes_vendues = Propriete.objects.filter(statut='vendu').count()
    proprietes_reservees = Propriete.objects.filter(statut='reserve').count()
    
    from django.db.models import Avg
    prix_moyen = Propriete.objects.aggregate(Avg('prix'))['prix__avg'] or 0
    
    proprietaires_distincts = Utilisateur.objects.filter(role='proprietaire').distinct()
    types_distincts = Propriete.objects.values_list('type', flat=True).distinct()
    communes_distinctes = Propriete.objects.values_list('commune', flat=True).distinct()
    statuts_distincts = Propriete.objects.values_list('statut', flat=True).distinct()
    
    from django.core.paginator import Paginator
    paginator = Paginator(proprietes, 50)
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
            'statut_admin': statut_propriete_admin_filter,
            'statut_owner': statut_propriete_owner_filter,
        },
        'proprietaire_nom': proprietaire_nom,
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
def toggle_admin_statut_propriete(request, pk):
    """
    Permet à l'admin de valider/invalider une propriété.
    Si l'admin invalide, le propriétaire ne peut plus réactiver.
    """
    user = request.user
    
    if not (user.is_superuser or user.role in ['admin', 'superadmin']):
        return redirect('index')
    
    propriete = get_object_or_404(Propriete, pk=pk)
    
    # ✅ L'admin peut changer le statut admin (validation)
    propriete.statut_propriete_admin = not propriete.statut_propriete_admin
    
    # ✅ Si l'admin invalide, on force la désactivation du propriétaire
    if not propriete.statut_propriete_admin:
        propriete.statut_propriete_owner = False
    # ✅ Si l'admin valide, on ne touche pas au statut du propriétaire
    # Il reste à son état précédent (True ou False)
    
    propriete.save()
    
    return redirect('gestion_proprietes_admin')

@login_required(login_url='connexion')
def toggle_owner_statut_propriete(request, pk):
    """
    Permet au propriétaire d'activer/désactiver sa propriété.
    Seulement si l'admin a validé (statut_propriete_admin = True)
    """
    propriete = get_object_or_404(Propriete, pk=pk, proprietaire=request.user)
    
    # ✅ Vérifier que l'admin a validé
    if propriete.statut_propriete_admin:
        propriete.statut_propriete_owner = not propriete.statut_propriete_owner
        propriete.save()
    
    return redirect('mes_proprietes')

@login_required(login_url='connexion')
def toggle_statut_propriete(request, pk):
    """
    Vue pour l'admin (à garder dans gestion_proprietes_admin)
    """
    user = request.user
    
    if not (user.is_superuser or user.role in ['admin', 'superadmin']):
        return redirect('index')
    
    propriete = get_object_or_404(Propriete, pk=pk)
    
    # ✅ L'admin peut bloquer/débloquer
    propriete.statut_propriete_admin = not propriete.statut_propriete_admin
    
    # ✅ Si l'admin bloque, on force la désactivation
    if not propriete.statut_propriete_admin:
        propriete.statut_propriete_owner = False
    else:
        # Si l'admin débloque, le propriétaire peut réactiver s'il veut
        # On ne touche pas à statut_propriete_owner, il reste à son état précédent
        pass
    
    propriete.save()
    
    return redirect('gestion_proprietes_admin')    

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




 

# def temoingnages(request):
#     return render(request,'immobilier/temoingnages.html' ) 


def espace_client(request):
    return render(request, 'espace_client.html')




@login_required(login_url='connexion')
def profil(request):
    user = request.user  # utilisateur actuellement connecté
    
    # Déterminer si l'utilisateur est admin
    is_admin = user.is_superuser or (hasattr(user, 'role') and user.role in ['admin', 'superadmin'])
    
    # Déterminer le rôle pour le template
    user_role = None
    if user.is_authenticated:
        if user.is_superuser:
            user_role = "admin"
        elif hasattr(user, 'role') and user.role == "proprietaire":
            user_role = "proprietaire"
        elif hasattr(user, 'role') and user.role == "admin":
            user_role = "admin"
        else:
            user_role = "client"
    
    context = {
        'user': user,
        'is_admin': is_admin,  # ← AJOUTER CETTE LIGNE
        'user_role': user_role,  # ← AJOUTER CETTE LIGNE
    }
    
    return render(request, 'profil.html', context)

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
    user = request.user

    if hasattr(user, 'role') and user.role != 'proprietaire':
        return render(request, 'erreur.html', {'message': "Accès réservé aux propriétaires."})

    # On récupère toutes les propriétés du propriétaire
    proprietes = Propriete.objects.filter(proprietaire=user).order_by('-date_publication')

    return render(request, 'proprietes/mes_proprietes.html', {'proprietes': proprietes})


#contact en utilisation le model contact et message pour creer une conversation entre l'utilisateur et les admins pour le formulaire de contact general

from django.contrib import messages as django_messages

def contact(request):
    """
    Vue pour le formulaire de contact général.
    Crée une conversation entre l'utilisateur et les administrateurs.
    """
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        sujet = request.POST.get('sujet')
        message_content = request.POST.get('message')
        
        # Trouver un admin pour recevoir le message
        # Priorité: superadmin > admin
        admin_user = Utilisateur.objects.filter(
            Q(is_superuser=True) | Q(role__in=['superadmin', 'admin'])
        ).first()
        
        if not admin_user:
            # Si aucun admin n'existe, créer le message quand même ou afficher une erreur
            django_messages.error(request, "Aucun administrateur disponible pour traiter votre demande.")
            return redirect('contact')
        
        # Récupérer l'utilisateur connecté (peut être None)
        utilisateur_connecte = request.user if request.user.is_authenticated else None
        
        # Vérifier si un contact existe déjà entre cet utilisateur et cet admin
        contact_fil = Contact.objects.filter(
            utilisateur=utilisateur_connecte,
            proprietaire=admin_user,
            propriete__isnull=True  # Contact général (pas lié à une propriété)
        ).first()
        
        if not contact_fil:
            # Créer un nouveau contact
            contact_fil = Contact.objects.create(
                utilisateur=utilisateur_connecte,
                proprietaire=admin_user,
                propriete=None,  # Pas de propriété liée
                nom=nom,
                email=email,
                telephone=telephone,
                sujet=sujet,
                message=message_content,
                statut='non_lu'  # Statut initial
            )
        
        # Créer le message associé
        Message.objects.create(
            contact=contact_fil,
            expediteur=utilisateur_connecte if utilisateur_connecte else None,
            destinataire=admin_user,
            contenu=message_content,
            statut='envoye'
        )
        
        django_messages.success(request, "Votre message a été envoyé avec succès. veillez verifier vos conversations pour voir la réponse de nos admins.")
        return redirect('contact')
    
    return render(request, 'contact.html', {})

# pour que les admins puissent voir tous les contacts généraux (pas liés à une propriété) et y répondre facilement, on crée une vue dédiée

@login_required(login_url='connexion')
def contacts_admin(request):
    """
    Affiche tous les contacts généraux pour les administrateurs.
    """
    if not (request.user.is_superuser or request.user.role in ['admin', 'superadmin']):
        return redirect('index')
    
    contacts = Contact.objects.filter(
        propriete__isnull=True  # Contacts généraux uniquement
    ).order_by('-date_envoi')
    
    # Statistiques
    non_lus = contacts.filter(statut='non_lu').count()
    
    context = {
        'contacts': contacts,
        'non_lus': non_lus,
    }
    return render(request, 'contacts/admin_list.html', context)