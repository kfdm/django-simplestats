import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Stat(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    key = models.TextField()
    value = models.FloatField()


class Countdown(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField()
    label = models.CharField(max_length=36)
    calendar = models.URLField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='coutdown', verbose_name=_('owner'))

    def remaining(self):
        return self.created - timezone.localtime(timezone.now())


class Chart(models.Model):
    created = models.DateTimeField()
    label = models.CharField(max_length=36)
    keys = models.CharField(max_length=36)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chart', verbose_name=_('owner'))
