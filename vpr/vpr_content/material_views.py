from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, CreateAPIView, SingleObjectAPIView
from vpr_api.decorators import api_token_required, api_log
from models import MaterialComment, getMaterialRawID, MaterialViewCount
from models import MaterialRating, MaterialFavorite
from serializers import MaterialCommentSerializer


class MaterialComments(ListCreateAPIView):
    """
    """
    model  = MaterialComment
    serializer_class = MaterialCommentSerializer

    def create(self, request, *args, **kwargs):
        # change material_id & version to material raw ID
        data = request.DATA.dict()
        rid = getMaterialRawID(kwargs['mid'], kwargs.get('version', None))
        data['material'] = rid

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_log
    @api_token_required
    def post(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.create(request, *args, **kwargs)
        return response 

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.list(request, *args, **kwargs)        
        return response

    def list(self, request, *args, **kwargs):
        """ Original list function with caching implemented
        """
        rid = getMaterialRawID(kwargs['mid'], kwargs.get('version', None))
        self.object_list = MaterialComment.objects.filter( material=rid)
        self.object_list = self.object_list.order_by('modified')

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            error_args = {'class_name': self.__class__.__name__}
            raise Http404(self.empty_error % error_args)

        # Pagination size is set by the `.paginate_by` attribute,
        # which may be `None` to disable pagination.
        page_size = self.get_paginate_by(self.object_list)
        if page_size:
            packed = self.paginate_queryset(self.object_list, page_size)
            paginator, page, queryset, is_paginated = packed
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list)
        sr_data = serializer.data
        return Response(sr_data)


@csrf_exempt
@api_log
@api_token_required
@api_view(['GET', 'PUT', 'DELETE'])
def materialCounterView(request, *args, **kwargs):
    """ View for update and get material view number
    """
    rid = getMaterialRawID(kwargs['mid'], kwargs.get('version', None))
    try:
        counter = MaterialViewCount.objects.get(material=rid)
    except MaterialViewCount.DoesNotExist:
        counter = MaterialViewCount(material_id=rid, count=0)
        counter.save()
    
    data = {}
    if request.method == 'GET':
        pass
    elif request.method == 'PUT':
        try:    
            if not request.DATA:
                incr = 1
            else:
                incr = int(request.DATA.get('increment', 1))
            counter.count += incr 
        except ValueError:
            pass
        counter.last_visit = datetime.utcnow()
        counter.save() 
    elif request.method == 'DELETE':
        counter.count = 0
        counter.save()

    data['view'] = counter.count
    data['last_visit'] = counter.last_visit
    return Response(data)
    

@csrf_exempt
@api_log
@api_token_required
@api_view(['GET', 'POST', 'DELETE'])
def materialRatesView(request, *args, **kwargs):
    """ View for update and get material view number
    """
    rid = getMaterialRawID(kwargs['mid'], kwargs.get('version', None))
    data = {} 
    if request.method == 'POST':
        pid = request.DATA['person']
        rate = request.DATA['rate'] 
        if not MaterialRating.objects.filter(material=rid, person=pid).exists():
            rate_obj = MaterialRating(material_id=rid, person_id=pid, rate=rate)
            rate_obj.save() 
    elif request.method == 'GET':
        pid = request.GET.get('person', None)
        if pid:
            try:
                s_rate = MaterialRating.objects.get(material=rid, person=pid)
                data = {'rate': s_rate.rate, 'count': 1}
            except MaterialRating.DoesNotExist:
                data = {'rate': None, 'count': 0}
            return Response(data)
    elif request.method == 'DELETE':
        pid = request.GET.get('person', None)
        if pid:
            MaterialRating.objects.filter(material=rid, person=pid).delete()
        else:
            # hey, be careful
            MaterialRating.objects.filter(material=rid).delete()

    # all cases return final rates
    avg_rate, count = getMaterialAvgRate(rid)
    data = {'rate': avg_rate, 'count': count}
    return Response(data)


def getMaterialAvgRate(mrid):
    """ Queries, calculates then returns final material rate
    """
    query = MaterialRating.objects.filter(material=mrid)
    count = query.count()
    res = query.aggregate(Avg('rate'))
    avg_rate = res[res.keys()[0]]
    return avg_rate, count


@csrf_exempt
@api_log
@api_token_required
@api_view(['GET', 'POST', 'DELETE'])
def materialFavoriteView(request, *args, **kwargs):
    """ View for update and get material view number
    """
    rid = getMaterialRawID(kwargs['mid'], kwargs.get('version', None))
    data = {} 
    if request.method == 'POST':
        pid = request.DATA['person']
        if not MaterialFavorite.objects.filter(material=rid, person=pid).exists():
            fav_obj = MaterialFavorite(material_id=rid, person_id=pid)
            fav_obj.save() 
    elif request.method == 'GET':
        pid = request.GET.get('person', None)
        if pid is not None:
            try:
                count = MaterialFavorite.objects.filter(
                    material=rid, person=pid).exists() and 1 or 0
                data = {'favorite': count}
            except MaterialFavorite.DoesNotExist:
                data = {'favorite': 0}
            return Response(data)
        pass
    elif request.method == 'DELETE':
        pid = request.GET.get('person', None)
        if pid:
            MaterialFavorite.objects.filter(material=rid, person=pid).delete()

    # all cases return final rates
    count = MaterialFavorite.objects.filter(material=rid).count()
    data = {'favorite': count}
    return Response(data)

