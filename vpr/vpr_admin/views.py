from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, views as auth_views
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.http import HttpResponse
from django import forms

from forms import ClientRegForm
from vpr_api.models import APIClient, generateClientKey

class DashboardView(TemplateView):
    
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        return None
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)


@csrf_protect
def loginView(request):
    """
    """
    ERROR_LOGIN = 'Log in failed: %s'
    data = {}

    if request.method == 'POST':
        # validate the inputs
        uid = request.POST.get('inputUID', '')
        password = request.POST.get('inputPassword', '')
        user = authenticate(username=uid, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/dashboard')
            data['error'] = ERROR_LOGIN % 'Only administrators allowed'
        else:
            data['error'] = ERROR_LOGIN % 'Invalid User ID or Password' 

    return render_to_response("login.html",
                              dictionary=data,
                              context_instance=RequestContext(request))

def logoutDashboard(request):
    """Log out current admin from dashboard"""
    if request.user.is_authenticated:
        defaults = {
            'current_app': '',
            'extra_context': {},
            'template_name': 'login.html',
            }
        return auth_views.logout(request, **defaults)
    return render_to_response("login.html",
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
def clientRegView(request):
    """ Dashboard view, for registering API Client """
    if request.method == 'POST':
        form = ClientRegForm(request.POST)
        if form.is_valid():
            client = APIClient()
            client.name = form['name'].value()
            client.client_id = form['client_id'].value()
            client.email = form['email'].value()
            client.organization = form['organization'].value()
            client.secret_key = generateClientKey(client.email)
            client.save()
            return redirect('/dashboard/clients/')
    else:
        form = ClientRegForm()
    return render(request, 'client_reg.html', {'form':form})
    

@login_required
def clientListView(request):
    """docstring for clientListView"""
    clients = APIClient.objects.all().order_by('name') 
    return render(request, 'clients.html', {'clients': clients})


def getNavigationBar(request):
    """ """
    BASE_URL = '/dashboard/'
    dashboard_items = {
        'Overview': BASE_URL,
        'API SERVICE': {
            'Client Management': BASE_URL + 'clients/',
            'Statistics': BASE_URL + 'stats/',
            },
        'SYSTEM': {
            'Processes': BASE_URL + 'processes/',
            'Resource Usages': BASE_URL + '',
            'Database': '',
            },
        'CONTENT MANAGEMENT': {
            'Materials': '',
            'Other Content': '',
            'Statistics': '',
            },
        'VP COMPONENTS': {
            'VP Web': '',
            'VP Core': '',
            'VP Transformer': '',
            },
        } 
    return dashboard_items
