from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.http import HttpResponse
from django import forms

from forms import ClientRegForm
from vpc_api.models import APIClient

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
    """docstring for logoutDashboard"""
    if not request.user.is_anonymous:
       logout(request.user)
    return render_to_response("login.html",
                              dictionary={'error':'Logging out successfully'},
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
            client.save()
            return redirect('/client')
    else:
        form = ClientRegForm()
    return render(request, 'client_reg.html', {'form':form})
