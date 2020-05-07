from django.conf import settings


HISTORY_LIMIT = getattr(settings, 'ADMIN_FILTER_HISTORY_LIMIT', 3)
URL_PATH = getattr(settings, 'ADMIN_FILTER_URL_PATH', 'filter').strip('/') + '/'
