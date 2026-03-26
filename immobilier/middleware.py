# immobilier/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SessionDebugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            logger.debug(f"Session ID: {request.session.session_key}")
            logger.debug(f"User: {request.user.username}")
            logger.debug(f"User ID: {request.user.id}")
            logger.debug(f"Is authenticated: {request.user.is_authenticated}")
            logger.debug(f"Session expired: {request.session.get_expiry_age()}")
        else:
            if request.path not in ['/login/', '/static/', '/admin/']:
                logger.debug(f"Not authenticated on {request.path}")

    def process_response(self, request, response):
        if request.user.is_authenticated:
            logger.debug(f"Response for {request.path} - Status: {response.status_code}")
        return response