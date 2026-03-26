# immobilier/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend d'authentification qui permet de se connecter avec:
    - username
    - email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None
        
        try:
            # Cherche par username ou email
            # Utilise first() au lieu de get() pour éviter MultipleObjectsReturned
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()  # ← Utilise first() au lieu de get()
            
            if user and user.check_password(password):
                return user
        except Exception as e:
            # Log l'erreur
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None