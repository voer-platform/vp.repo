from django.db import models

from vpr_content.models import Material


class TermSeverity(models.Model):
    level = models.IntegerField(default=1)
    description = models.CharField(max_length=256)
    action = models.CharField(max_length=256)


class BlackTerm(models.Model):
    """ Single term that admin should be warned about """
    value = models.CharField(max_length=256)
    severity = models.ForeignKey(TermSeverity)


class CensorResult(models.Model):
    """ Store pointer to suspicious content """
    material = models.ForeignKey(Material)
    term = models.ForeignKey(BlackTerm)
