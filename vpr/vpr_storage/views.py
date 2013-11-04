# Create your views here.
from os.path import realpath
import requests
import os
import json

from zipfile import ZipFile, ZIP_DEFLATED
from django.http import Http404, HttpResponse

from vpr_content.models import Material, MaterialFile, MaterialExport
from vpr_content.models import listMaterialFiles, MaterialExport
from vpr_content.models import getLatestMaterial, getMaterialLatestVersion
from vpr_content import models

from django.conf import settings

ZIP_INDEX_MODULE = 'metadata.json'
ZIP_INDEX_COLLECTION = 'collection.json'
ZIP_HTML_FILE = 'index.html'
ZIP_FILE_NAME = 'm-%s-%s.zip'

MTYPE_MODULE = 1
MTYPE_COLLECTION = 2

MATERIAL_LICENSE = "http://creativecommons.org/licenses/by/3.0/"
MATERIAL_SOURCE_URL = 'http://voer.edu.vn/m/%s/%d'

HTTP_CODE_PROCESSING = 102
HTTP_CODE_SUCCESS = 200 

EXPORT_TYPE = 'pdf'
EXPORT_URL = os.path.join(settings.VPT_URL, 'export')

def postMaterialZip(material):
    """Load and send zip file to exporting service"""
    try:
        mzip = open(zipMaterial(material), 'rb')
        payload = {'token': '', 
                'cid': '',
                'output': EXPORT_TYPE}
        files = {'file': (mzip.name.split('/')[-1], mzip.read())}
        return requests.post(EXPORT_URL, files=files, data={})
    except:
        pass
        # some logs saved here
    finally:
        mzip.close()
        os.remove(mzip.name) 


def downloadFile(url, path):
    """Download a file from given URl and saved to path"""
    res = requests.get(url)
    save_ok = False
    if res.status_code == 200:
        try:
            with open(path, 'wb') as ofile:
                ofile.write(res.content)
            save_ok = True
        except:
            # log
            pass
    else: 
        # log
        pass
    return save_ok
        

def generateExportPath(material_id, material_version):
    """Return the full path of export file based on material ID and version"""
    exp_path = '%s-%d.pdf' % (material_id, material_version)
    return os.path.join(settings.EXPORT_DIR, exp_path)


def storeMaterialExport(url, exp_obj):
    """Download and store export metadata into DB. Export object required"""
    export_path = generateExportPath(exp_obj.material_id, exp_obj.version)              
    attempt = 3
    while attempt > 0:
        if downloadFile(url, export_path):
            exp_obj.path = export_path
            exp_obj.file_type = EXPORT_TYPE
            exp_obj.save()
            break
        elif attemp == 1:
            # delete the export object in case of 3-time failed
            exp_obj.delete()
        attempt -= 1


TASK_ID_PREFIX = '...'


def isExportProcessing(export_obj):
    """Check if the export file is under converting or not"""
    return export_obj.path[:len(TASK_ID_PREFIX)] == TASK_ID_PREFIX


def requestMaterialPDF(material):
    """ Create the zip package and post it to vpt in order to 
        receive the PDF genereated.
        After receiving the file exported, an entry of export
        material will be created (as MaterialExport). This returns:
            True: Export file is ready to get.
            False: Export file is not ready. Try again later.
    """
    
    res_pending = 'PENDING'
    res_success = 'SUCCESS'

    ready = False

    # check export status 
    export_obj = MaterialExport.objects.filter(
        material_id = material.material_id,
        version = material.version)
    
    # in case of nothing have been saved
    if export_obj.count() == 0:
        res = postMaterialZip(material)
        values = json.loads(res.content)
        new_export = MaterialExport(
            material_id = material.material_id,
            version = material.version)
        if values['status'] == res_pending:
            new_export.path = TASK_ID_PREFIX + values['task_id']
            new_export.save()
        elif values['status'] == res_success:
            storeMaterialExport(values['url'], export_obj)
            ready = True
        else:
            # failure, delete the export object
            export_obj.delete()
    else:
        # check for the status if existed
        export_obj = export_obj[0]
        if isExportProcessing(export_obj):
            # conversion not completed, ask again
            task_id = export_obj.path[3:]
            res = requests.get(EXPORT_URL+'?task_id='+task_id)
            values = json.loads(res.content)
            # download the PDF if done
            if values['status'] == res_success:
                storeMaterialExport(values['url'], export_obj)
                ready = True
            elif values['status'] != res_pending:
                # failure, delete the export object
                export_obj.delete()
        elif export_obj.path:
            ready = True
    return ready


def zipMaterial(material):
    """ Collects all material info and put it into a ZIP file.
        Full path of the zip file will be returned to the caller.
    """
    mid = material.material_id
    version = material.version
    mtype = material.material_type
    
    # init the zip package
    zip_path = os.path.join(
        settings.TEMP_DIR,
        ZIP_FILE_NAME % (str(mid), str(version))
        )
    zf = ZipFile(zip_path, 'w', ZIP_DEFLATED) 

    # check if module or collection
    if mtype == MTYPE_MODULE:
        # read all material files, and put into the zip package
        mfids = listMaterialFiles(mid, version)
        for mfid in mfids:
            mf = MaterialFile.objects.get(id=mfid)
            zf.writestr(mf.name, mf.mfile.read()) 
            mf.mfile.close()

        # add material text content
        raw_content = material.text
        try:
            raw_content = raw_content.encode('utf-8')
        except:
            raw_content = raw_content.decode('utf-8').encode('utf-8')
        zf.writestr(ZIP_HTML_FILE, raw_content)

        # generate material json
        persons = models.getMaterialPersons(material.id)
        try: 
            author_ids = persons['author'].split(',')
        except:
            author_ids = []
        author_names = models.getPersonName(author_ids)
        index_content = {
            'title': material.title,
            'url': MATERIAL_SOURCE_URL % (
                material.material_id,
                material.version),
            'authors': author_names,
            'version': material.version,
            }
        index_content = json.dumps(index_content)
        zf.writestr(ZIP_INDEX_MODULE, index_content)

    elif mtype == MTYPE_COLLECTION:

        # get list of all contained materials    
        all_materials = getNestedMaterials(material)

        # load materials into ZIP
        for cid in range(len(all_materials)):
            m_id = all_materials[cid][0]
            m_version = all_materials[cid][1]
            m_title = all_materials[cid][2]
            if m_version is None:
                m_version = getMaterialLatestVersion(m_id)
            mfids = listMaterialFiles(m_id, m_version)
            m_object = Material.objects.get(material_id=m_id)
            for mfid in mfids:
                try:
                    mf = MaterialFile.objects.get(id=mfid)
                    zf.writestr(m_id+'/'+mf.name, mf.mfile.read())
                    mf.mfile.close()
                except:
                    print 'Error when reading material file: ' + mf.name
            zf.writestr(m_id+'/'+ZIP_HTML_FILE, m_object.text)

        # prepare some fields
        editor_ids = models.getMaterialPersons(material.id)['editor']
        editor_ids = editor_ids.split(',')
        editors = models.getPersonName(editor_ids)
        if isinstance(editors, str): editors = [editors,]
        material_url = MATERIAL_SOURCE_URL % (
            material.material_id,
            material.version)

        # generate collection.json
        try:
            index_content = json.loads(material.text)
            index_content['id'] = material.material_id
            index_content['title'] = material.title
            index_content['version'] = str(material.version)
            index_content['license'] = MATERIAL_LICENSE
            index_content['url'] = material_url
            index_content['editors'] = editors 
            index_content = json.dumps(index_content)
        except:
            # another way
            index_content = '{"id":"%s",' % material.material_id
            index_content += '"title":"%s",' %  material.title
            index_content += '"version":"%s",' % str(material.version)
            index_content += '"license":"%s",' % MATERIAL_LICENSE
            index_content += '"url":"%s",' % material_url
            index_content += '"editors":"%s",' % editors 
            index_content += material.text[material.text.index('{')+1:]
        zf.writestr(ZIP_INDEX_COLLECTION, index_content)
        
    zf.close()
    return realpath(zf.filename)


def getNestedMaterials(material):
    """Returns list of material IDs of children inside collection material"""
    materials = []
    try:
        # get all material IDs and versions
        nodes = eval(material.text)['content']
        for node in nodes:
            materials.extend(extractMaterialInfo(node))
    except:
        print 'Error when getting nested materials of ' + material.material_id
    return materials
    

def extractMaterialInfo(node):
    """(recursively) Returns material IDs and version found"""
    found = []
    try:
        # extract child nodes
        if node.get('content', []):
            for child_node in node['content']:
                found.extend(extractMaterialInfo(child_node))
        else:
            # extract current node
            mid = node['id']
            mver = node.get('version', None)
            mtitle = node['title']
            found.append((mid, mver, mtitle))
    except:
        # where is the error?
        print "Error when getting collection modules"

    return found
        

def getMaterialPDF(request, *args, **kwargs):
    """Check and return the PDF file of given material if exist"""
    mid = kwargs.get('mid', None)
    version = kwargs.get('version', None)
    if not version: 
        version = getMaterialLatestVersion(mid) 
    material = Material.objects.get(material_id=material_id, version=version)
    get_it = False
    try: 
        export_obj = MaterialExport.objects.get(material_id=mid, version=version)
        if isExportProcessing(export_obj):
            get_it = requestMaterialPDF(material):
        else:  
            get_it = True
    except (MaterialExport.DoesNotExist, IOError): 
        get_it = requestMaterialPDF(material):
    except:
        raise Http404
    
    if get_it:
        export_obj = MaterialExport.objects.get(material_id=mid, version=version)
        # return the PDF content, this should be served be the web server
        with open(export_obj.path, 'rb') as pdf: 
            data = pdf.read() 
            return HttpResponse(data, 
                                mimetype = 'application/pdf', 
                                status = HTTP_CODE_SUCCESS) 
    else:
        return HttpResponse('CONTENT NOT READY', status=HTTP_CODE_PROCESSING) 


def getMaterialFile(request, *args, **kwargs):
    """Return request for downloading material file"""
    mfid = kwargs.get('mfid', None)

    try:
        mfile = MaterialFile.objects.get(id=mfid)  
        data = mfile.mfile.read()
        mime_type = mfile.mime_type
        mfile.mfile.close()
        return HttpResponse(data, mimetype=mime_type)
    except:
        raise Http404


def handlePersonAvatar(request, *args, **kwargs):
    """Returns the avatar image of specific person"""
    pid = kwargs.get('pk', None)
    delete = request.GET.get('delete', None) 
    try:
        person = models.Person.objects.get(id=pid)  
        if not delete: 
            data = person.avatar.read()
            person.avatar.close()
            return HttpResponse(data, mimetype='image/jpeg')    # oh dear
        elif delete == '1':
            person.avatar.delete() 
            return HttpResponse('Person avatar deleted', status=200)
    except:
        raise Http404

