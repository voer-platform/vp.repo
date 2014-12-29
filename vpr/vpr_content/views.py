# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from django.http import Http404, HttpResponse
from django.db.models import Q
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
from vpr_api.models import APIRecord
from vpr_api.decorators import api_token_required, api_log
from vpr_storage.views import zipMaterial, requestMaterialExport
from material_views import MaterialComments, materialCounterView
from material_views import materialRatesView, materialFavoriteView
from search_views import GeneralSearch, facetSearchView, raise404
from utils import buildPageURLs

import os
import mimetypes
import models
import serializers
import math


#from vpr_log.logger import get_logger
#logger = get_logger('api')

mimetypes.init()


CACHE_TIMEOUT_CATEGORY = 180
CACHE_TIMEOUT_PERSON = 180
CACHE_TIMEOUT_MATERIAL = 180


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
        query_st = request.GET.urlencode() or 'all'
        cache_key = 'list-categories:%s' % query_st
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
        query_st = request.GET.urlencode() or 'all'
        cache_key = 'list-persons:%s' % query_st 
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
    cache_def = 'get-person:%s-%s'

    def retrieve(self, request, *args, **kwargs):
        pid = kwargs.get('pk', None)
        do_count = (request.GET.get('count', None) == '1')
        cache_key = self.cache_def % (str(pid), (do_count and 'count') or '')
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

        self.object.invalidate()

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
                if material_id: 
                    self.object_list = self.model.objects.filter(
                        material_id=material_id
                        )
                else:
                    # get the or criterias
                    or_crits = getOrFields(request)

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
                    self.object_list = queryCategory(
                        request,
                        self.object_list,
                        'categories' in or_crits
                        )

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
                    material = serializer.data['results'][res]
                    material['text'] = ''
                    if request.GET.get('names', None):
                        # add the category names
                        cats = []
                        for mc in material['categories']:
                            cats.append([mc, models.getCategoryName(mc)])
                        material['categories'] = cats
                        # .. and the person names
                        for role in settings.VPR_MATERIAL_ROLES:
                            if material.has_key(role):
                                persons = []
                                pids = [int(pid) for pid in material[role].split(',')]
                                for pc in pids:
                                    persons.append([pid, models.getPersonName(pid)])
                                material[role] = persons
                    serializer.data['results'][res] = material

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
                try:
                    if not request.DATA.get('export-later', 0):
                        requestMaterialPDF(self.object)
                except:
                    pass

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
        if request.META.get('HTTP_VOER', None) != '1':
            ret_code = 400
        else:  
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


@api_log
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
    similar = SearchQuerySet().models(models.Material).more_like_this(material)[:10]
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


def getOrFields(request):
    """ Get the fields for OR conditions from request
    """
    # get the OR criterias
    or_fields = request.GET.get('or', [])
    if or_fields:
        or_fields = [cr.lower().strip() for cr in or_fields.split(',')]
    return or_fields


def queryCategory(request, qset, use_or =True):
    """ Use the given QuerySet (qset) and continue querying on category
        using conditions provided from request
    """
    CAT_NAME = 'categories'
    if request.GET.has_key(CAT_NAME):
        sel_cats = request.GET.get(CAT_NAME, '').split(',')
        # search with OR or AND option
        if use_or:
            if sel_cats:
                first_cat = models.wrapAssignedCategory(sel_cats[0])
                q = Q(categories__contains=first_cat)
            for cat in sel_cats[1:]:
                org_cat = models.wrapAssignedCategory(cat)
                q = q | Q(categories__contains=org_cat)
            qset = qset.filter(q) 
        else:
            for cat in sel_cats:
                org_cat = models.wrapAssignedCategory(cat)
                qset = qset.filter(categories__contains=org_cat)
    return qset


@api_log
@api_view(['GET'])
@api_token_required
def queryMaterialByViewCount(request, *args, **kwargs):
    """ Returns QuerySet of all material sorted by view count
    """
    #per_page = settings.REST_FRAMEWORK['PAGINATE_BY']
    per_page = 50
    sql = """SELECT m.id, m.material_id, m.version, m.material_type, 
                    m.title, m.categories, m.description, m.modified,
                    mv.count
             FROM vpr_content_material as m
             INNER JOIN vpr_content_materialviewcount as mv
             ON (m.id=mv.material_id) 
             ORDER BY mv.count DESC LIMIT %d; 
             """ % (per_page)
    materials = []
    for m in models.Material.objects.raw(sql):

        # getting categories
        cids = models.restoreAssignedCategory(m.categories)
        categories = []
        for ci in range(len(cids)):
            categories.append((cids[ci], models.getCategoryName(cids[ci]))) 

        # getting authors
        pids = models.getMaterialPersons(m.id)['author'].split(',')
        pnames = models.getPersonName(pids)
        if not isinstance(pnames, list):
            pnames = [pnames,] 
        authors = []
        for pi in range(len(pids)):
            authors.append((pids[pi], pnames[pi])) 

        s_material = {
            'material_id': m.material_id,
            'version': m.version,
            'material_type': m.material_type,
            'title': m.title,
            'categories': categories, 
            'count': m.count,
            'author': authors,
            'modified': m.modified,
            }
        materials.append(s_material)

    return Response(materials)


MAT_BASIC_FIELDS = ('id', 'material_id', 'version', 'title', \
    'categories', 'material_type')


@api_log
@api_view(['GET'])
@api_token_required
def get_person_favs(request, *args, **kwargs):
    """ Returns list of materials which are selected as favorite of person
    """
    pid = kwargs.get('pk', None)
    # get paging infomation
    per_page = settings.REST_FRAMEWORK['PAGINATE_BY']
    page = int(request.GET.get('page', 1))
    start_on = (page-1)*per_page

    # get the favs
    qset = models.MaterialFavorite.objects.filter(person_id=pid).order_by('id')
    fav_count = qset.count()
    qset = qset[start_on:start_on+per_page].values_list('material_id')
    res = [item[0] for item in qset]
   
    # now extract material info in list
    mats = models.Material.objects.filter(id__in=res).values(*MAT_BASIC_FIELDS)
    for material in mats:
        material['categories'] = models.restoreAssignedCategory(
            material['categories']) 
        # get related persons
        mroles = models.getMaterialPersons(material['id'])
        material['author'] = mroles.get('author', None)
        del material['id']

    # build the result page 
    page_total = math.ceil(fav_count*1.0/per_page)
    page_prev, page_next = buildPageURLs(request, page_total) 
    # alter serialization data
    page_result = {
        'next': page_next,
        'previous': page_prev,
        'results': mats,
        'count': fav_count,
        }

    return Response(page_result)
    

from django.db import connection

@api_log
@api_view(['GET'])
@api_token_required
def get_most_faved(request, *args, **kwargs):
    """ Returns QuerySet of all material sorted by view count
    """
    per_page = settings.REST_FRAMEWORK['PAGINATE_BY']
    sql = """
        SELECT m.id, m.material_id, m.title, m.version, m.categories, 
               m.material_type, m.modified, count(f.person_id) AS fc
        FROM vpr_content_material AS m
        INNER JOIN vpr_content_materialfavorite AS f
        ON m.id = f.material_id
        GROUP BY m.id
        ORDER BY fc DESC
        LIMIT %d;
        """ % per_page
    cur = connection.cursor()
    res = cur.execute(sql)

    materials = []
    for m in cur:

        # getting categories
        cids = models.restoreAssignedCategory(m[4])
        categories = []
        for ci in range(len(cids)):
            categories.append((cids[ci], models.getCategoryName(cids[ci]))) 

        # getting authors
        pids = models.getMaterialPersons(m[0])['author'].split(',')
        pnames = models.getPersonName(pids)
        if not isinstance(pnames, list):
            pnames = [pnames,] 
        authors = []
        for pi in range(len(pids)):
            authors.append((pids[pi], pnames[pi])) 

        s_material = {
            'material_id': m[1],
            'version': m[3],
            'material_type': m[5],
            'title': m[2],
            'categories': categories, 
            'favorites': m[7],
            'author': authors,
            'modified': m[6],
            }
        materials.append(s_material)

    return Response(materials)


@api_log
@api_view(['GET'])
@api_token_required
def get_top_rated(request, *args, **kwargs):
    """ Returns QuerySet of all material sorted by view count
    """
    per_page = settings.REST_FRAMEWORK['PAGINATE_BY']
    sql = """
        SELECT m.id, m.material_id, m.title, m.version, m.categories,
               m.material_type, m.modified, avg(mr.rate) as avg_rate, count(mr.rate) AS rate_count
        FROM vpr_content_material AS m
        INNER JOIN vpr_content_materialrating AS mr
        ON m.id = mr.material_id
        GROUP BY mr.material_id
        ORDER BY avg_rate DESC, rate_count DESC
        LIMIT %d;
        """ % per_page
    cur = connection.cursor()
    res = cur.execute(sql)

    materials = []
    for m in cur:

        # getting categories
        cids = models.restoreAssignedCategory(m[4])
        categories = []
        for ci in range(len(cids)):
            categories.append((cids[ci], models.getCategoryName(cids[ci]))) 

        # getting authors
        pids = models.getMaterialPersons(m[0])['author'].split(',')
        pnames = models.getPersonName(pids)
        if not isinstance(pnames, list):
            pnames = [pnames,] 
        authors = []
        for pi in range(len(pids)):
            authors.append((pids[pi], pnames[pi])) 

        s_material = {
            'material_id': m[1],
            'version': m[3],
            'material_type': m[5],
            'title': m[2],
            'categories': categories, 
            'rating': m[7],
            'rating_count': m[8],
            'author': authors,
            'modified': m[6],
            }
        materials.append(s_material)

    return Response(materials)


@api_log
@api_view(['GET'])
@api_token_required
def material_links_view(request, *args, **kwargs):
    mid = kwargs['mid'].lower()
    # temporarily bypass version for now, not really good
    #version = kwargs.get('version', None)
    sqs = SearchQuerySet().models(models.Material)
    res = sqs.filter(text__exact='"'+mid+'"', material_type=2)
    materials = []
    for collection in res:
        materials.append({
            'material_id': collection.material_id,
            'version': collection.version,
            'title': collection.title,
            })
    return Response(materials)
