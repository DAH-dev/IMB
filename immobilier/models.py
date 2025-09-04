from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- Utilisateur ---
class Utilisateur(AbstractUser):
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
    ]
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reserve', 'Réservé'),
        ('vendu', 'Vendu'),
    ]

    titre = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    localisation = models.CharField(max_length=255)
    surface = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    date_publication = models.DateTimeField(auto_now_add=True)
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="proprietes")


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

# Create your models here.
