from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, views as auth_views
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.http import HttpResponse
from django import forms
from haystack.query import SearchQuerySet
from datetime import datetime, timedelta

import json
import pymongo

from forms import ClientRegForm
from vpr_api.models import APIClient, generateClientKey, APIToken
from vpr_admin import stats
from vpr_content import serializers, models


MATERIAL_LIMIT = 20


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
            'next_page': '/dashboard/',
            }
        return auth_views.logout(request, **defaults)
    return redirect('/dashboard/')

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
    

@csrf_protect
@login_required
def clientEditView(request, client_id):
    """ Dashboard view, for registering API Client """
    if request.method == 'POST':
        form = ClientRegForm(request.POST)
        if form.is_valid():
            cid = form['id'].value()
            client = APIClient.objects.get(id=cid)
            client.name = form['name'].value()
            client.client_id = form['client_id'].value()
            client.email = form['email'].value()
            client.organization = form['organization'].value()
            client.secret_key = form['secret_key'].value()
            client.save()
            return redirect('/dashboard/clients/')
        else:
            assert False

    # Open existing client object 
    client = APIClient.objects.get(id=client_id)
    form = ClientRegForm()
    form.fields['id'].initial = client.id
    form.fields['name'].initial = client.name
    form.fields['client_id'].initial = client.client_id 
    form.fields['organization'].initial = client.organization
    form.fields['email'].initial = client.email

    return render(request, 'client_reg.html', {'form': form,
                                               'client': client
                                               })

@login_required
def clientListView(request):
    """docstring for clientListView"""
    clients = APIClient.objects.all().order_by('name') 
    return render(request, 'clients.html', {'clients': clients})


@login_required
def tokenListView(request):
    """docstring for tokenListView"""
    tokens = APIToken.objects.all().order_by('since') 
    return render(request, 'tokens.html', {'tokens': tokens})


@login_required
def statsView(request):
    t_end = datetime.now()
    t_start = t_end - timedelta(days=3)
    rs = stats.APIRecordStats(t_start)
    p_results = rs.getPeriodResults(36)
    to_chart = [['Time', 'Aggregated', 'GET', 'POST', 'PUT', 'DELETE'],]
    for pi in range(len(p_results)):
        to_chart.append(['', p_results[pi], 0, 0, 0, 0])

    return render(request, 'stats.html', {'chart_data': to_chart})


@login_required
def apiRecordsView(request):
    client = pymongo.MongoClient()
    col = client['vpr'].api
    cur = col.find().sort('time', pymongo.DESCENDING).limit(200)
    logs = [item for item in cur]
    return render(request, 'api_records.html', {'logs': logs})


@login_required
def statsView(request):
    t_end = datetime.now()
    t_start = t_end - timedelta(days=3)
    rs = stats.APIRecordStats(t_start)
    p_results = rs.getPeriodResults(36)
    to_chart = [['Time', 'Aggregated', 'GET', 'POST', 'PUT', 'DELETE'],]
    for pi in range(len(p_results)):
        to_chart.append(['', p_results[pi], 0, 0, 0, 0])

    return render(request, 'stats.html', {'chart_data': to_chart})



@csrf_protect
@login_required
def materialsView(request):
    """View of the material management"""

    query = request.GET.get('kw', '')
    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1

    page_data = {'current_page': page}

    # process with request for deletion
    if request.method == "POST":    
        del_list = request.POST.getlist('check-delete')
        #import pdb;pdb.set_trace()
        models.Material.objects.filter(material_id__in=del_list).delete()
        page_data['removed'] = del_list 

    res = SearchQuerySet().models(models.Material)
    if query:
        res = res.filter(title=query)
    else:
        res = res.order_by('-modified')
    res_count = res.count()
    page_start = (page-1)*MATERIAL_LIMIT

    # variables to templates
    page_data['materials'] = res[page_start:page_start+MATERIAL_LIMIT]
    page_data['page_total'] = res_count / MATERIAL_LIMIT
    page_data['web_url'] = request.get_host().split(':')[0]

    return render(request, 'materials.html', dictionary=page_data)

