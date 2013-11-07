# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from hashlib import md5
from datetime import datetime
from rest_framework import mixins
from haystack.query import SearchQuerySet 
from django.conf import settings
from django.core.cache import cache

import os
import mimetypes

from vpr_api.models import APIRecord
from vpr_api.decorators import api_token_required
from vpr_api.utils import APILogger
from vpr_api.decorators import api_token_required, api_log
from vpr_storage.views import zipMaterial, requestMaterialPDF

import models
import serializers


#from vpr_log.logger import get_logger
#logger = get_logger('api')
#apilog = APILogger() 

mimetypes.init()


CACHE_TIMEOUT_CATEGORY = 180
CACHE_TIMEOUT_PERSON = 180
CACHE_TIMEOUT_MATERIAL = 180


def raise404(request, message=''):
    """Record failed API call and raise 404 exception"""
    raise Http404(message)


def splitPath(path):
    """ Return necessary elements in path
        
        >>> path = '/hello/from/paris/'
        >>> splitPath(path)
        ['hello', 'from', 'paris']

    """
    path = path.split('/')
    path = [item for item in path if len(item)>0]
    return path


# CATEGORY CALLS

class CategoryList(generics.ListCreateAPIView):
    """docstring for AuthorList"""
    model = models.Category
    serializer_class = serializers.CategorySerializer
    paginate_by = None

    def list(self, request, *args, **kwargs):
        """Original list function with caching implemented"""
        cache_key = 'list-categories:'
        result = cache.get(cache_key)
        if result:
            sr_data = eval(result)
        else:
            self.object_list = self.get_filtered_queryset()

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
            cache.set(cache_key, str(sr_data), CACHE_TIMEOUT_CATEGORY)

        return Response(sr_data)

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.list(request, *args, **kwargs)        
        return response

    @api_log
    @api_token_required
    def post(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.create(request, *args, **kwargs)
        return response


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for CategoryDetail"""
    model = models.Category
    serializer_class = serializers.CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        cid = kwargs.get('pk', None)
        do_count = (request.GET.get('count', None) == '1')
        cache_key = 'get-category:%s-%s' % (
            str(cid),
            (do_count and '-count') or '')
        result = cache.get(cache_key)

        if not result:
            self.object = self.get_object()
            serializer = self.get_serializer(self.object)

            # check if request for counting
            if do_count:
                serializer.data['material'] = models.countAssignedMaterial(cid)
           
            sr_data = dict(serializer.data)
            cache.set(cache_key, sr_data, CACHE_TIMEOUT_CATEGORY)
        else:
            sr_data = result

        return Response(sr_data)

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.retrieve(request, *args, **kwargs)
        return response

    @api_log
    @api_token_required
    def put(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.update(request, *args, **kwargs)
        return response

    @api_log
    @api_token_required
    def delete(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.destroy(request, *args, **kwargs)
        return response


# PERSON

class PersonList(generics.ListCreateAPIView):
    """docstring for PersonList"""
    model = models.Person
    serializer_class = serializers.MiniPersonSerializer

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.list(request, *args, **kwargs)
        return response


    @api_log
    @api_token_required
    def post(self, request, *args, **kwargs):
        """Old post method with decorator"""
        self.serializer_class = serializers.PersonSerializer
        response = self.create(request, *args, **kwargs)
        self.serializer_class = serializers.MiniPersonSerializer
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save()
            
            # add the avatar if uploaded
            avatar = request.FILES.get('avatar', None)
            if avatar is not None:
                self.object.avatar = avatar 
                self.object.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """Original list function with caching implemented"""
        cache_key = 'list-persons:'
        result = cache.get(cache_key)
        if result:
            sr_data = eval(result)
        else:
            self.object_list = self.get_filtered_queryset()

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
            cache.set(cache_key, str(sr_data), CACHE_TIMEOUT_PERSON)

        return Response(sr_data)


class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for PersonDetail"""
    model = models.Person
    serializer_class = serializers.PersonSerializer

    def retrieve(self, request, *args, **kwargs):
        pid = kwargs.get('pk', None)
        do_count = (request.GET.get('count', None) == '1')
        cache_key = 'get-person:%s-%s' % (
            str(pid),
            (do_count and 'count') or '')
        result = cache.get(cache_key)

        if not result:
            self.object = self.get_object()
            serializer = self.get_serializer(self.object)

            # check if request for counting
            if request.GET.get('count', None) == '1':
                pid = kwargs.get('pk', None)
                person_stats = models.countPersonMaterial(
                    person_id = pid,
                    roles = range(len(settings.VPR_MATERIAL_ROLES)))
                for role in person_stats:
                    serializer.data[role] = person_stats[role]

            sr_data = dict(serializer.data)
            cache.set(cache_key, sr_data, CACHE_TIMEOUT_PERSON)
        else:
            sr_data = result

        return Response(sr_data)

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.retrieve(request, *args, **kwargs)
        return response

    @api_log
    @api_token_required
    def put(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.update(request, *args, **kwargs)

        # update the avatar if needed
        avatar = request.FILES.get('avatar', None)
        if avatar is not None:
            self.object.avatar = avatar 
            self.object.save()

        return response

    @api_log
    @api_token_required
    def delete(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.destroy(request, *args, **kwargs)
        return response


# MODULE

class MaterialList(generics.ListCreateAPIView):
    """ Return list of material or create a new one
    """
    model = models.Material
    serializer_class = serializers.MaterialSerializer
    br_fields = ['language', 'material_type']

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():

            # this call consumes a lot of queries and time
            self.pre_save(serializer.object)
            self.object = serializer.save()

            # update the person and roles
            models.setMaterialPersons(self.object.id, request.DATA)

            # correct modified time to now
            self.object.modified = datetime.utcnow()

            # add the attached image manually
            self.object.image = request.FILES.get('image', None)
            self.object.save()

            # next, add all other files submitted
            material_id = self.object.material_id
            material_version = self.object.version 
            for key in request.FILES.keys():
                if key == 'image': continue
                mfile = models.MaterialFile()
                mfile.material_id = material_id 
                mfile.version = material_version
                file_content = request.FILES.get(key, None)
                mfile.mfile = file_content 
                #mfile.mfile.close()
                mfile.name = request.FILES[key].name
                mfile.description = request.DATA.get(key+'_description', '')
                mfile.mime_type = mimetypes.guess_type(
                    os.path.realpath(mfile.mfile.name))[0] or ''
                mfile.save()
            
            # add original record if having
            if request.DATA.get('original_id', ''):
                orgid = models.OriginalID()
                orgid.material_id = material_id
                orgid.original_id = request.DATA.get('original_id')
                orgid.save()

            # (module/collection) create the zip package and post to vpt
            if not request.DATA.get('export_later', 0):
                import pdb;pdb.set_trace()
                requestMaterialPDF(self.object) 

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_log
    @api_token_required
    def list(self, request, *args, **kwargs):
        """ Customized function for listing materials with same ID
        """
        # in case of listing all version of specific material
        material_id = kwargs.get('mid', None)

        # caching
        query_st = request.GET.urlencode() or material_id or 'all'
        cache_key = 'list-materials:' + query_st
        result = cache.get(cache_key)

        if result:
            sr_data = eval(result)
        else:
            try: 
                # show all versions of specific material
                if kwargs.get('mid', None):
                    self.object_list = self.model.objects.filter(material_id=kwargs['mid'])
                # list materials
                else:
                    self.object_list = self.model.objects
                    # filter by person roles
                    mp_objs = models.MaterialPerson.objects
                    mp_list = []
                    role_in_query = False
                    for role in settings.VPR_MATERIAL_ROLES:
                        role_id = settings.VPR_MATERIAL_ROLES.index(role)
                        if request.GET.get(role, ''):
                            query = request.GET.get(role, '').split(',')
                            query = [int(pid) for pid in query]
                            mp_list.extend(mp_objs.filter(role=role_id, person_id__in=query))
                            role_in_query = True
                    allow_materials = []
                    for mp in mp_list:
                        if mp.material_rid not in allow_materials:
                            allow_materials.append(int(mp.material_rid))

                    # do the filtering
                    browse_on = {}
                    fields = [item for item in request.GET if item in self.br_fields]
                    [browse_on.update({item:request.GET[item]}) for item in fields]
                    if role_in_query:
                        browse_on['pk__in'] = allow_materials
                    self.object_list = self.object_list.filter(**browse_on)

                    # custom fileting with categories 
                    if request.GET.get('categories', ''):
                        sel_cats = request.GET.get('categories', '').split(',')
                        for cat in sel_cats:
                            org_cat = models.refineAssignedCategory(cat)
                            self.object_list = self.object_list.filter(
                                categories__contains=org_cat)

                    # continue with sorting
                    sort_fields = request.GET.get('sort_on', '')
                    if sort_fields:
                        #import pdb;pdb.set_trace()
                        self.object_list = self.object_list.order_by(sort_fields)
            except:
                raise404(request) 

            # Default is to allow empty querysets.  This can be altered by setting
            # `.allow_empty = False`, to raise 404 errors on empty querysets.
            allow_empty = self.get_allow_empty()
            if not allow_empty and len(self.object_list) == 0:
                error_args = {'class_name': self.__class__.__name__}
                raise404(request, self.empty_error % error_args)

            # Pagination size is set by the `.paginate_by` attribute,
            # which may be `None` to disable pagination.
            page_size = self.get_paginate_by(self.object_list)
            if page_size:
                packed = self.paginate_queryset(self.object_list, page_size)
                paginator, page, queryset, is_paginated = packed
                serializer = self.get_pagination_serializer(page)
            else:
                serializer = self.get_serializer(self.object_list)

            # silly steps: remove heavy data from response
            try:
                for res in range(len(serializer.data['results'])):
                    serializer.data['results'][res]['text'] = ''
            except:
                # should we shout anything?
                pass

            # setting cache
            sr_data = serializer.data
            for mi in sr_data['results']:
                mi['modified'] = str(mi['modified'])
            cache.set(cache_key, str(sr_data), CACHE_TIMEOUT_MATERIAL)

        return Response(sr_data)

    @api_log
    @api_token_required
    def post(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.create(request, *args, **kwargs)
        return response 


    #def get(self, request, *args, **kwargs):
    #    """docstring for get"""
    #    return Response({'a':'b'})

class MaterialDetail(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    """
    Return material data, update/check-in it or delete it
    """
    model = models.Material
    serializer_class = serializers.MaterialSerializer

    def get_object(self, material_id, version='', request=None):
        """ Customized get_object() function, used for Material objects
            which will be get by ID and version.
        """
        try:
            args = {'material_id':material_id}
            # get latest or specific version
            object = self.model.objects
            if version:
                args['version'] = version
                object = object.get(**args)
            else:
                object = models.getLatestMaterial(material_id)
            return object 
        except:
            raise404(request, 404)

    def retrieve(self, request, *args, **kwargs):
        """ Customized to the Material objects """
        # implement cache
        mid = kwargs.get('mid', '')
        mvs = kwargs.get('version', '')
        cache_key = 'get-material:'+mid + '-' + str(mvs)
        result = cache.get(cache_key)
        
        if not result:
            self.object = self.get_object(material_id=kwargs.get('mid', ''),
                                        version=kwargs.get('version', ''),
                                        request=request)

            serializer = self.get_serializer(self.object)
            sr_data = dict(serializer.data)
            cache.set(cache_key, sr_data, CACHE_TIMEOUT_MATERIAL)
        else:
            sr_data = result

        response = Response(sr_data)
        return response

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.retrieve(request, *args, **kwargs)
        return response

    @api_log
    @api_token_required
    def put(self, request, *args, **kwargs):
        """ Check in a material  """
        try: 
            serializer = self.get_serializer(data=request.DATA)
            response = None
            if serializer.is_valid():

                # check if valid editor or new material will be created
                sobj = serializer.object
                sobj.material_id = material_id = kwargs['mid']

                # special update or checkin?
                if request.GET.get('magic-update', None):
                    sobj.version = current_version = int(kwargs['version'])
                    res = models.deleteMaterial(material_id, current_version)
                    if not res:
                        raise   # 404
                else:
                    last_version = models.getMaterialLatestVersion(sobj.material_id)
                    try:
                        sobj.version = last_version + 1
                    except AttributeError:
                        sobj.version = 1
                        
                self.pre_save(sobj)
                self.object = serializer.save()

                # update the person and roles
                models.setMaterialPersons(self.object.id, request.DATA)

                # add the attached image manually
                self.object.image = request.FILES.get('image', None)
                self.object.save()

                # next, add all other files submitted
                material_id = self.object.material_id
                material_version = self.object.version 
                for key in request.FILES.keys():
                    if key == 'image': continue
                    mfile = models.MaterialFile()
                    mfile.material_id = material_id 
                    mfile.version = material_version
                    file_content = request.FILES.get(key, None)
                    mfile.mfile = file_content 
                    mfile.name = request.FILES[key].name
                    mfile.description = request.DATA.get(key+'_description', '')
                    mfile.mime_type = mimetypes.guess_type(
                        os.path.realpath(mfile.mfile.name))[0] or ''
                    mfile.save()

                # (module/collection) create the zip package and post to vpt
                if not request.DATA.get('export-later', 0):
                    requestMaterialPDF(self.object) 

                response = Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            

            return response
        except: 
            raise404(request)


    @api_log
    @api_token_required
    def destroy(self, request, *args, **kwargs):
        """ Delete the material """
        try:
            res = models.deleteMaterial(
                kwargs.get('mid'), 
                kwargs.get('version'))
            if res:
                ret_code = status.HTTP_200_SUCCESS
            else:
                ret_code = status.HTTP_204_NO_CONTENT
        except:
            raise404(request)

        return Response(status=ret_code)


class GeneralSearch(generics.ListAPIView):
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
                self.serializer_class = serializers.IndexMaterialSerializer
                allow_models = [models.Material]
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


class MaterialFiles(generics.ListCreateAPIView):
    """View for listing and creating MaterialFile"""
    model = models.MaterialFile
    serializer_class = serializers.MaterialFileSerializer
    
    def get_object(self, mfid, version='', request=None):
        """ Customized get_object() function, used for Material objects
            which will be get by ID and version.
        """
        try:
            object = self.model.objects.get(id=mfid)
            return object 
        except:
            raise404(request, 404)

    def retrieve(self, request, *args, **kwargs):
        """ Customized to the Material objects """
        self.object = self.get_object(mfid=kwargs.get('mfid', ''),
                                      request=request)

        serializer = self.get_serializer(self.object)

        response = Response(serializer.data)
        return response

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """docstring for get"""
        response = self.retrieve(request, *args, **kwargs)
        return response


@api_view(['GET'])
def listMaterialFiles(request, *args, **kwargs):
    """Lists all files attached to the specific material, except the material image
    """
    material_id = kwargs.get('mid', None)
    version = kwargs.get('version', None)
    # why possibly version gets nothing as value?
    if not version:
        version = models.getMaterialLatestVersion(material_id)
    file_ids = models.listMaterialFiles(material_id, version)

    return Response(file_ids)   


SM_WEIGHT_KEYWORD = 3
SM_WEIGHT_TITLE = 2
SM_WEIGHT_TITLE = 1


def getSimilarByKeywords(material_id, version):
    """Returns list of similar materials getting by comparing keywords"""

    # why possibly version gets nothing as value?
    if not version:
        version = models.getMaterialLatestVersion(material_id)

    try:
        weight_list = {}
        material = models.Material.objects.filter(
            material_id=material_id, 
            version=version).values('keywords')[0]

        # build the keyword query
        keywords = material.get('keywords', '')
        keywords = keywords.split('\n')
        for kw in keywords:
            objs = models.Material.objects.exclude(material_id=material_id).\
                filter(keywords__contains=kw).values('material_id', 'title')
            m_list = [(item['material_id'], item['title']) for item in objs]
            for m_item in m_list:
                mid = m_item[0]
                if not weight_list.has_key(mid):
                    item_dict = {'material_id': m_item[0], 'title': m_item[1]}
                    weight_list[mid] = [0, item_dict]
                weight_list[mid][0] += SM_WEIGHT_KEYWORD 
        
        # sort by weights then limit the results
        couples = weight_list.values()
        couples.sort(reverse=True)
        result = [item[1] for item in couples[:10]]
    except:
        raise404(request, 404)
    return result


def getSimilarByHaystack(material_id, version):
    """Return list of similar materials using Haystack"""
    if not version:
        material = models.getLatestMaterial(material_id)
    else:
        material = models.Material.objects.filter(
            material_id = material_id,
            version = version)[0]

    similar = SearchQuerySet().more_like_this(material)[:10]
    result = []
    for item in similar:
        item_dict = {}
        item_dict['material_id'] = item.material_id
        item_dict['title'] = item.title
        item_dict['version'] = item.version
        item_dict['material_type'] = item.material_type
        item_dict['modified'] = item.modified
        result.append(item_dict)

    return result


@api_log
@api_view(['GET'])
@api_token_required
def getSimilarMaterials(request, *args, **kwargs):
    """Lists all files attached to the specific material, except the material image
    """
    material_id = kwargs.get('mid', None)
    version = kwargs.get('version', None)
    cache_key = 'get-similar:'+material_id + '-' + str(version)
    res_cache = cache.get(cache_key)
    if res_cache:
        result = res_cache
    else:               
        result = getSimilarByHaystack(material_id, version)
        cache.set(cache_key, result, CACHE_TIMEOUT_MATERIAL)

    return Response(result)


@api_log
@api_token_required
def getMaterialImage(request, *args, **kwargs):
    """ Return image data of material cover 
    """
    mid = kwargs['mid']
    material = models.getMaterial(kwargs['mid'], kwargs.get('version', None))
    if material.image:
        response = HttpResponse(
            content = material.image.read(),
            mimetype = 'image/jpg')
        # not for file downloading
        #response['content-disposition'] 
        return response

    raise Http404

