#from django.core.signals import Signal
import django.dispatch

after_apicall = django.dispatch.Signal(providing_args=['request'])
