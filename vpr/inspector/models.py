from django.db import models

from vpr_content.models import Material


class TermSeverity(models.Model):
    description = models.CharField(max_length=256)
    action = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return '%d - %s' % (self.pk, self.description)


class FlagTerm(models.Model):
    """ Single term that admin should be warned about """
    value = models.CharField(max_length=256)
    severity = models.ForeignKey(TermSeverity)
    active = models.BooleanField(default=True)


class CensorResult(models.Model):
    """ Store pointer to suspicious content """
    material = models.ForeignKey(Material)
    term = models.ForeignKey(FlagTerm)

