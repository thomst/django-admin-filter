from urllib.parse import urlencode
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError
try:
    from django.db.models import JSONField
except ImportError:
    from django_jsonfield_backport.models import JSONField
from . import settings as app_settings


def default_dict():
    return dict()


class FilterQuery(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    persistent = models.BooleanField(default=False)
    querydict = JSONField(default=default_dict)
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    for_everyone = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        permissions = [('can_handle_global_filterqueries', 'Can handle global FilterQueries')]

    @staticmethod
    def has_global_perm(user):
        perm = 'django_admin_filter.can_handle_global_filterqueries'
        return user.has_perm(perm)

    def save(self, *args, **kwargs):
        # create a generic name if missing
        if not self.name:
            if settings.USE_TZ:
                now = timezone.localtime().strftime('%x %X')
            else:
                now = timezone.now().strftime('%x %X')
            self.name = _('Filter from ') + now

        # create a generic description if missing
        if not self.description:
            self.description = self.pretty_query

        # save filter-query
        super().save(*args, **kwargs)

        # truncate history
        if app_settings.TRUNCATE_HISTORY and not self.persistent:
            history = FilterQuery.objects.filter(
                user=self.user,
                content_type=self.content_type,
                persistent=False
            )[app_settings.HISTORY_LIMIT:]
            FilterQuery.objects.filter(id__in=[f.id for f in history]).delete()

    @property
    def pretty_query(self):
        lines = list()
        for key in sorted(self.querydict.keys()):
            line = '{} = {}'.format(key, self.querydict[key])
            lines.append(line)
        return '\n'.join(lines)

    @property
    def urlquery(self):
        return urlencode(self.querydict)
