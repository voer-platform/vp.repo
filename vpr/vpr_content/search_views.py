from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from django.http import Http404
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from haystack.query import SearchQuerySet, SQ
from vpr_api.decorators import api_token_required, api_log
from utils import buildPageURLs

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


def getOrFields(request):
    """ Get the fields for OR conditions from request
    """
    # get the OR criterias
    or_fields = request.GET.get('or', [])
    if or_fields:
        or_fields = [cr.lower().strip() for cr in or_fields.split(',')]
    return or_fields


def queryCategory(request, sqset, use_or =True):
    """ Use the given SearchQuerySet (qset) and continue query on category
    """
    CAT_NAME = 'categories'
    if request.GET.has_key(CAT_NAME):
        sel_cats = request.GET.get(CAT_NAME, '').split(',')
        # search with OR or AND option
        if use_or:
            if sel_cats:
                first_cat = models.wrapAssignedCategory(sel_cats[0])
                sq = SQ(categories__contains=first_cat)
            for cat in sel_cats[1:]:
                org_cat = models.wrapAssignedCategory(cat)
                sq = sq | SQ(categories__contains=org_cat)
            sqset = sqset.filter(sq) 
        else:
            for cat in sel_cats:
                org_cat = models.wrapAssignedCategory(cat)
                sqset = sqset.filter(categories__contains=org_cat)
    return sqset


@api_log
@api_token_required
@api_view(['GET'])
def facetSearchView(request, *args, **kwargs):
    """ Return the faceted data corresponding to the given query 
    """
    facet_fields = ('material_type', 'categories', 'language')
    query = {}
    or_fields = getOrFields(request)
    # support both 'type' & 'material_type'
    if request.GET.get('type', None):
        query['material_type'] = request.GET['type']
    allow_model = models.Material
    sqs = SearchQuerySet().models(allow_model).filter(**query)    
    # add custom fileting with categories 
    sqs = queryCategory(request, sqs, 'categories' in or_fields)  
    # implement facet
    for field in facet_fields:
        sqs = sqs.facet(field)
    counts = sqs.facet_counts()
    # refine the category IDs
    cats = counts['fields']['categories']
    cat_dict = {}
    for cid in range(len(cats)):
        raw_id = models.restoreAssignedCategory(cats[cid][0])
        if raw_id: 
            raw_id = str(raw_id[0])
        else:
            raw_id = '0'
        if cat_dict.has_key(raw_id):
            cat_dict[raw_id] += cats[cid][1]
        else:
            cat_dict[raw_id] = cats[cid][1]
    cats = []
    for key in cat_dict:
        cats.append([int(key), cat_dict[key]])
    counts['fields']['categories'] = cats

    return Response(counts)
