from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import UniqueConstraint
# from moviepy.editor import VideoFileClip

# --- Utilisateur ---
# --- Utilisateur ---
class Utilisateur(AbstractUser):
    # Ajout du champ 'photo'
    photo = models.ImageField(upload_to="utilisateurs/", blank=True, null=True)
    
    # CNI obligatoire
    cni = models.ImageField(upload_to="utilisateurs/cni/", blank=True, null=True, verbose_name="Carte Nationale d'Identité")
    
    # telephone obligatoire
    telephone = models.CharField(max_length=20, blank=False)
    
    # ✅ Rendre first_name et last_name obligatoires
    first_name = models.CharField(max_length=150, blank=False)  # ← plus de blank=True
    last_name = models.CharField(max_length=150, blank=False)   # ← plus de blank=True
    
    role = models.CharField(max_length=20, choices=[('client','Client'),('proprietaire','Propriétaire'),('admin','Admin'),('superadmin','SuperAdmin')])
    statut = models.BooleanField(default=True)
    
    # Champ pour indiquer si la CNI est vérifiée
    cni_verifie = models.BooleanField(default=False, verbose_name="CNI vérifiée")

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    otp_attempts = models.IntegerField(default=0)

    # ⚠️ évite le conflit avec auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='immobilier_user_set',  # <- nom unique
        blank=True,
        help_text='Les groupes auxquels cet utilisateur appartient.',
        verbose_name='groupes'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='immobilier_user_permissions_set',  # <- nom unique
        blank=True,
        help_text='Permissions spécifiques à cet utilisateur.',
        verbose_name='permissions utilisateur'
    )

    # --- Contact ---
class Contact(models.Model):
    STATUT_CHOICES = [
        ('non_lu', 'Non lu'),
        ('en_cours', 'En cours'),
        ('traite', 'Traité'),
    ]

    # Le visiteur (si connecté)
    utilisateur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts"
    )

    # Le propriétaire de la propriété ou l'admin
    proprietaire = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name="contacts_recus"
    )

    # Propriété concernée (optionnelle si c'est un contact général)
    propriete = models.ForeignKey(
        'Propriete',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts_propriete"
    )

    # Infos du message
    nom = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    sujet = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='non_lu')
    date_envoi = models.DateTimeField(auto_now_add=True)

    # 🚨 Nouveaux champs pour suppression côté utilisateur
    supprime_par_utilisateur = models.BooleanField(default=False)
    supprime_par_proprietaire = models.BooleanField(default=False)

    def __str__(self):
        cible = self.propriete.titre if self.propriete else "Contact général"
        return f"Contact - {self.nom or self.utilisateur} -> {self.proprietaire} ({cible})"

# --- Propriété ---
class Propriete(models.Model):
    TYPE_CHOICES = [
        ('maison', 'Maison'),
        ('appartement', 'Appartement'),
        ('terrain', 'Terrain'),
        ('villa', 'Villa'),
        ('immeuble', 'Immeuble'),
        ('magasin', 'Magasin'),
    ]
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reserve', 'Réservé'),
        ('vendu', 'Vendu'),
        ('en_netoyage', 'En netoyage'),
        ('en_construction', 'En construction'),
    ]

    titre = models.CharField(max_length=255)
    description = models.TextField()
    caracteristiques = models.JSONField(default=list, encoder=DjangoJSONEncoder, blank=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    ville=models.CharField(max_length=50)
    commune=models.CharField(max_length=50)
    statut_propriete_admin = models.BooleanField(default=True)   # Contrôle admin (True = autorisé)
    statut_propriete_owner = models.BooleanField(default=False)   # Choix du propriétaire
   
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    date_publication = models.DateTimeField(auto_now_add=True)
    proprietaire = models.ForeignKey("Utilisateur", on_delete=models.CASCADE, related_name="proprietes")
    # Ajout des champs 'image' et 'video'
    image = models.ImageField(upload_to="proprietes/images/", blank=True, null=True)
    video = models.FileField(upload_to="proprietes/videos/", blank=True, null=True)
    duree_video = models.PositiveIntegerField(
        help_text="Durée de la vidéo en secondes, calculée automatiquement.",
        blank=True,
        null=True
    )
    def __str__(self):
        return self.titre


# --- Visite ---
class Visite(models.Model):
    propriete = models.ForeignKey('Propriete', on_delete=models.CASCADE, related_name="visites")
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name="visites")
    date_visite = models.DateTimeField(auto_now_add=True) # Ajout de auto_now_add=True
    
    class Meta:
        constraints = [
            # Assure qu'un utilisateur ne peut avoir qu'une seule entrée de visite pour une propriété (Vue UNIQUE À VIE)
            models.UniqueConstraint(fields=['propriete', 'utilisateur'], name='unique_property_view') 
        ]



# --- Message ---
class Message(models.Model):
    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('lu', 'Lu'),
        ('supprime', 'Supprimé'),
    ]

    expediteur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name="messages_envoyes"
    )
    
    destinataire = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name="messages_recus"
    )
    
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True
    )
    
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='envoye')
    
    # ✅ NOUVEAU : Ajoutez ce champ si vous voulez la date de lecture
    date_lu = models.DateTimeField(null=True, blank=True)  # ← À AJOUTER SI VOUS VOULEZ
    
    # Champs pour la suppression
    supprime_par_expediteur = models.BooleanField(default=False)
    supprime_par_destinataire = models.BooleanField(default=False)
    supprime_pour_tous = models.BooleanField(default=False)

    def __str__(self):
        return f"Message de {self.expediteur} à {self.destinataire} - {self.statut}"




