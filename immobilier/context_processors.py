# immobilier/context_processors.py
from .models import Message

def notifications(request):
    """
    Context processor pour ajouter le nombre de messages non lus à tous les templates
    """
    total_non_lus = 0
    if request.user.is_authenticated:
        total_non_lus = Message.objects.filter(
            destinataire=request.user,
            statut='envoye'
        ).count()
    
    return {
        'total_non_lus': total_non_lus,
    }