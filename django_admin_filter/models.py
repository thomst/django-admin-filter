from urllib.parse import urlencode
from jsonfield import JSONField
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError
from . import settings as app_settings


class FilterQuery(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    persistent = models.BooleanField(default=False)
    querydict = JSONField(default=dict())
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

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
            )
            FilterQuery.objects.filter(
                id__in=history[app_settings.HISTORY_LIMIT:]
            ).delete()

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
