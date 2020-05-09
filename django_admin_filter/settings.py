from django.conf import settings


HISTORY_LIMIT = getattr(settings, 'ADMIN_FILTER_HISTORY_LIMIT', 3)
TRUNCATE_HISTORY = getattr(settings, 'ADMIN_FILTER_TRUNCATE_HISTORY', True)
URL_PATH = getattr(settings, 'ADMIN_FILTER_URL_PATH', 'filter').strip('/') + '/'
