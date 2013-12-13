from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from django.http import Http404
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, SingleObjectAPIView
from haystack.query import SearchQuerySet 

from vpr_api.decorators import api_token_required, api_log
import models
import serializers


def raise404(request, message=''):
    """Record failed API call and raise 404 exception"""
    raise Http404(message)


class GeneralSearch(ListAPIView):
    """docstring for Search"""

    @api_log
    @api_token_required
    def list(self, request, *args, **kwargs):
        """docstring for list"""
        keywords = request.GET.get('kw', '')
        try:
            limit = request.GET.get('on', '')
            material_type = request.GET.get('type', '')
            query = {'content': keywords}

            # branching for the person case
            if limit.lower() == 'p':  
                self.serializer_class = serializers.IndexPersonSerializer
                allow_models = [models.Person,]                                
            else: 
                if limit.lower() == 'm':
                    allow_models = [models.Material]
                else:
                    allow_models = [models.Material, models.Person]
                    
                self.serializer_class = serializers.IndexCommonSerializer
                try:
                    material_type = int(material_type)
                    query['material_type'] = material_type
                except ValueError:
                    pass    

            # get paging infomation
            pg_size = settings.REST_FRAMEWORK['PAGINATE_BY']
            pg_at = int(request.GET.get('page', 1))
            pg_start = (pg_at-1)*pg_size

            # perform search
            res = SearchQuerySet().models(*allow_models).filter(**query)
            result_count = res.count()
            self.object_list = [_ for _ in res[pg_start:pg_start+pg_size]]
        except:
            raise
            raise404(request)

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            error_args = {'class_name': self.__class__.__name__}
            raise404(self.empty_error % error_args)

        # build the next and previous pages
        page_prev, page_next = buildPageURLs(request) 
        if pg_at <= 1:
            page_prev = None
        if pg_size * pg_at >= result_count:
            page_next = None
        serializer = self.get_serializer(self.object_list)

        # alter serialization data
        new_data = {
            'next': page_next,
            'previous': page_prev,
            'results': serializer.data,
            'count': result_count,
            }
        serializer._data = new_data

        response = Response(serializer.data) 
        return response


def buildPageURLs(request):
    """Return the URLs of next and previous page from current one"""
    page = int(request.GET.get('page', 1))
    query = request.GET.dict()
    pre_location = request.path + '?' 
    query['page'] = page + 1
    query_st = '&'.join([k+'='+unicode(query[k]) for k in query])
    next_location = pre_location + query_st 
    query['page'] = page - 1
    query_st = '&'.join([k+'='+unicode(query[k]) for k in query])
    prev_location= pre_location + query_st 
    url_next = request.build_absolute_uri(next_location)
    url_prev = request.build_absolute_uri(prev_location)
    return url_prev, url_next

