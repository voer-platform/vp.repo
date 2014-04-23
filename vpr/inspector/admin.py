from django.contrib.admin import site

from models import TermSeverity, FlagTerm, CensorResult


site.register(TermSeverity)
site.register(FlagTerm)
site.register(CensorResult)
