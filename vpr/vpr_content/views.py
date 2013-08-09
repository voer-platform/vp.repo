# from django.http import HttpResponse, HttpRequest
# from django.core import urlresolvers
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework.reverse import reverse
from django.http import Http404
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

from vpr_api.decorators import api_token_required, api_log
from vpr_storage.views import zipMaterial, requestMaterialPDF

import models
import serializers


#from vpr_log.logger import get_logger
#logger = get_logger('api')
#apilog = APILogger() 

mimetypes.init()


CACHE_TIMEOUT_CATEGORY = 60
CACHE_TIMEOUT_MATERIAL = 60


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

    @api_log
    @api_token_required
    def get(self, request, *args, **kwargs):
        """Old post method with decorator"""
        response = self.list(request, *args, **kwargs)        
        #apilog.record(request, response.status_code)
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
        cache_key = 'category-%s%s' % (
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

class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    """docstring for PersonDetail"""
    model = models.Person
    serializer_class = serializers.PersonSerializer

    def retrieve(self, request, *args, **kwargs):
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

        return Response(serializer.data)

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
                mfile.mfile.close()
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
            if request.DATA.get('export-now', 0):
                requestMaterialPDF(self.object) 

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_log
    @api_token_required
    def list(self, request, *args, **kwargs):
        """ Customized function for listing materials with same ID
        """
        try: 
            self.object_list = self.model.objects
            if kwargs.get('mid', None):
                self.object_list = self.object_list.filter(material_id=kwargs['mid'])

            # filter by person roles
            mp_objs = models.MaterialPerson.objects
            mp_list = []
            for role in settings.VPR_MATERIAL_ROLES:
                role_id = settings.VPR_MATERIAL_ROLES.index(role)
                if request.GET.get(role, ''):
                    query = request.GET.get(role, '').split(',')
                    query = [int(pid) for pid in query]
                    mp_list.extend(mp_objs.filter(role=role_id, person_id__in=query))
            allow_materials = []
            for mp in mp_list:
                if mp.material_rid not in allow_materials:
                    allow_materials.append(int(mp.material_rid))

            # do the filtering
            browse_on = {}
            fields = [item for item in request.GET if item in self.br_fields]
            [browse_on.update({item:request.GET[item]}) for item in fields]
            if allow_materials:
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

        response = Response(serializer.data)
        return response

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
        cache_key = mid + '__' + str(mvs)
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
                sobj.material_id = kwargs.get('mid')

                last_material = models.getLatestMaterial(sobj.material_id)
                try:
                    sobj.version = last_material.version + 1
                except AttributeError:
                    sobj.version = 1

                self.pre_save(sobj)
                self.object = serializer.save()
                response = Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            

            return response
        except: 
            raise 
            raise404(request)

    @api_log
    @api_token_required
    def destroy(self, request, *args, **kwargs):
        """ Delete the material """
        try:
            self.object = self.get_object(material_id=kwargs.get('mid', ''),
                                          version=kwargs.get('version', ''))
            self.object.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)
            return response
        except:
            raise404(request)


class GeneralSearch(generics.ListAPIView):
    """docstring for Search"""
    model = models.Material

    @api_log
    @api_token_required
    def list(self, request, *args, **kwargs):
        """docstring for list"""
        keywords = request.GET.get('kw', '')
        try:
            limit = request.GET.get('on', '')

            # branching for the person case
            if limit.lower() == 'p':  
                self.serializer_class = serializers.PersonSerializer
                allow_models = [models.Person,]                                
            else: 
                self.serializer_class = serializers.IndexMaterialSerializer
                allow_models = [models.Material]

            results = SearchQuerySet().models(*allow_models)
            results = results.filter(content=keywords)
            self.object_list = [obj.object for obj in results] 
        except:
            raise404(request)

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            error_args = {'class_name': self.__class__.__name__}
            raise404(self.empty_error % error_args)

        # Pagination size is set by the `.paginate_by` attribute,
        # which may be `None` to disable pagination.
        page_size = self.get_paginate_by(self.object_list)
        if page_size:
            packed = self.paginate_queryset(self.object_list, page_size)
            paginator, page, queryset, is_paginated = packed
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list)

        response = Response(serializer.data) 
        return response


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
