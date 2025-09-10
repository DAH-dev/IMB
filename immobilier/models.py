from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.serializers.json import DjangoJSONEncoder
# from moviepy.editor import VideoFileClip

# --- Utilisateur ---
class Utilisateur(AbstractUser):
    # Ajout du champ 'photo'
    photo = models.ImageField(upload_to="utilisateurs/", blank=True, null=True)
    # tes champs personnalisés ici
    telephone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=[('client','Client'),('proprietaire','Propriétaire'),('admin','Admin'),('superadmin','SuperAdmin')])
    statut = models.BooleanField(default=True)

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
    ville=models.CharField(max_length=50, default=True)
    commune=models.CharField(max_length=50, default=True)
    # localisation = models.JSONField(default=dict, blank=True)
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

    def save(self, *args, **kwargs):
        # Vérifie si un fichier vidéo a été uploadé
        if self.video:
            try:
                # Ouvre le fichier vidéo avec MoviePy pour obtenir sa durée
                clip = VideoFileClip(self.video.path)
                self.duree_video = int(clip.duration)
                clip.close()
            except Exception as e:
                # Gère les erreurs si la vidéo est corrompue ou si MoviePy ne peut pas la lire
                print(f"Erreur lors du calcul de la durée de la vidéo : {e}")
                self.duree_video = None # S'assure que le champ est vide en cas d'erreur

        # Appelle la méthode save() d'origine pour sauvegarder l'objet
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre


# --- Annonce ---
class Annonce(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
        ('supprime', 'Supprimée'),
    ]

    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name="annonces")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="annonces")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='attente')
    date_publication = models.DateTimeField(auto_now_add=True)
    date_moderation = models.DateTimeField(blank=True, null=True)
    moderateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name="modere_annonces")


# --- Transaction ---
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('achat', 'Achat'),
        ('location', 'Location'),
    ]
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name="transactions")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="transactions")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_transaction = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)


# --- Visite ---
class Visite(models.Model):
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name="visites")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="visites")
    date_visite = models.DateTimeField()


# --- Alerte ---
class Alerte(models.Model):
    STATUT_CHOICES = [
        ('non_resolue', 'Non résolue'),
        ('resolue', 'Résolue'),
    ]
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name="alertes")
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='non_resolue')
    date_creation = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name="alertes_traitees")

# --- Activité ---
class Activite(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="activites")
    action = models.CharField(max_length=100)
    cible = models.CharField(max_length=255)
    date_action = models.DateTimeField(auto_now_add=True)

# --- Message ---
class Message(models.Model):
    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('lu', 'Lu'),
        ('supprime', 'Supprimé'),
    ]
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="messages_envoyes")
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="messages_recus")
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='envoye')

    def __str__(self):
        return f"Message de {self.expediteur} à {self.destinataire} - {self.statut}"


# --- Information ---
class Information(models.Model):
    TYPE_CHOICES = [
        ('mission', 'Mission'),
        ('vision', 'Vision'),
        ('valeur', 'Valeur'),
        ('presentation', 'Présentation'),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name="informations_geres")

    def __str__(self):
        return f"{self.type} - {self.titre}"


# --- Temoignage ---
class Temoignage(models.Model):
    STATUT_CHOICES = [
        ('attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name="temoignages")
    nom = models.CharField(max_length=255, blank=True, null=True)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='attente')

    def __str__(self):
        auteur = self.utilisateur if self.utilisateur else self.nom
        return f"Témoignage de {auteur} - {self.statut}"