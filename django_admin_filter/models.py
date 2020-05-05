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


class Filter(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    persistent = models.BooleanField(default=False)
    querydict = JSONField()
    updated = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-updated']

    def save(self, *args, **kwargs):
        if not self.name:
            if settings.USE_TZ:
                now = timezone.localtime().strftime('%x %X')
            else:
                now = timezone.now().strftime('%x %X')
            self.name = _('Filter from ') + now
        if not self.description:
            self.description = self.pretty_query
        super().save(*args, **kwargs)

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

    def is_valid(self, model=None):
        model = model or self.content_type.model_class()
        try:
            model.objects.filter(**self.querydict)
        except (FieldError, ValidationError) as err:
            return False
        else:
            return True
