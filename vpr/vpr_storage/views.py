# Create your views here.
import requests
import os
import json

from datetime import datetime
from os.path import realpath
from shutil import rmtree
from subprocess import Popen
from zipfile import ZipFile, ZIP_DEFLATED

from django.http import Http404, HttpResponse
from django.template.defaultfilters import slugify

from vpr_content.models import Material, MaterialFile, MaterialExport
from vpr_content.models import listMaterialFiles
from vpr_content.models import getMaterialLatestVersion
from vpr_content import models
from vpr_api.decorators import api_log

from django.conf import settings

ZIP_INDEX_MODULE = 'metadata.json'
ZIP_INDEX_COLLECTION = 'collection.json'
ZIP_HTML_FILE = 'index.html'
ZIP_FILE_NAME = 'm-%s-%s.zip'

MTYPE_MODULE = 1
MTYPE_COLLECTION = 2

MATERIAL_LICENSE = "http://creativecommons.org/licenses/by/3.0/"
MOD_SOURCE_URL = 'http://voer.edu.vn/m/%s'
COL_SOURCE_URL = 'http://voer.edu.vn/c/%s'

HTTP_CODE_PROCESSING = 102
HTTP_CODE_SUCCESS = 200

EXPORT_TYPE = 'pdf'
EXPORT_URL = os.path.join(settings.VPT_URL, 'export')
TASK_ID_PREFIX = '...'
EXPORT_TIME_FORMAT = "%Y/%m/%d %H:%M"
EXPORT_TIME_LIMIT = 300    # seconds


def postZipFromPath(zip_path, export_format=''):
    """
    """
    res = None
    with open(zip_path, 'rb') as mzip:
        payload = {
            'token': '',
            'cid': '',
            'output': export_format,
            }
        files = {'file': mzip}
        res = requests.post(EXPORT_URL, files=files, data=payload)
        os.remove(mzip.name)
    return res


def postMaterialZip(material, export_format=''):
    """Load and send zip file to exporting service"""
    zip_path = zipMaterial(material)
    return postZipFromPath(zip_path, export_format)


def zipMaterial(material):
    """ Compresses the material and returns zip path
    """
    zip_path = None
    try:
        zip_path = zipMaterialExternal(material)
    except:
        # I'm not sure we should maintenance this anymore.
        #zip_path = zipMaterialInternal(material)
        pass
    return zip_path


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


def generateExportPath(material_id, material_version, export_format):
    """Return the full path of export file based on material ID and version"""
    export_type = export_format.name.lower()
    sub_folder = datetime.now().strftime('%y%m')
    exp_path = '%s-%d.%s' % (material_id, material_version, export_type)
    return os.path.join(
        settings.EXPORT_DIR, export_type, sub_folder, exp_path)


def storeMaterialExport(url, exp_obj):
    """Download and store export metadata into DB. Export object required"""
    export_path = generateExportPath(exp_obj.material_id, exp_obj.version,
                                     exp_obj.export_format)
    if not os.path.exists(os.path.dirname(export_path)):
        os.makedirs(os.path.dirname(export_path))
    attempt = 3
    while attempt > 0:
        if downloadFile(url, export_path):
            exp_obj.path = export_path
            exp_obj.file_type = EXPORT_TYPE
            exp_obj.name = ''
            exp_obj.save()
            break
        elif attempt == 1:
            # delete the export object in case of 3-time failed
            exp_obj.delete()
        attempt -= 1


def isExportProcessing(export_obj):
    """Check if the export file is under converting or not"""
    return export_obj.path[:len(TASK_ID_PREFIX)] == TASK_ID_PREFIX


def requestMaterialExport(material, export_format):
    """ Request export material with given format
    """
    res_pending = 'PENDING'
    res_success = 'SUCCESS'

    ready = False

    # get export format
    exp_format = models.ExportFormat.objects.get(name=export_format)

    # check export status
    export_obj = MaterialExport.objects.filter(
        material_id=material.material_id,
        export_format=exp_format,
        version=material.version)

    # in case of nothing have been saved
    if export_obj.count() == 0:
        res = postMaterialZip(material, export_format)
        try:
            values = json.loads(res.content)
            new_export = MaterialExport(
                material_id=material.material_id,
                export_format=exp_format,
                version=material.version)
            if values['status'] == res_pending:
                new_export.path = TASK_ID_PREFIX + values['task_id']
                new_export.name = datetime.now().strftime(EXPORT_TIME_FORMAT)
                new_export.save()
            elif values['status'] == res_success:
                storeMaterialExport(values['url'], export_obj)
                ready = True
            else:
                # failure, delete the export object
                export_obj.delete()
        except ValueError:
            pass
    else:
        # check for the status if existed
        export_obj = export_obj[0]
        if isExportProcessing(export_obj):
            # conversion not completed, ask again
            task_id = export_obj.path[3:]
            print 'task id:', task_id
            res = requests.get(EXPORT_URL+'?task_id='+task_id)
            try:
                values = json.loads(res.content)

            except ValueError:
                # non-json content returned
                export_obj.delete()
            else:
                # download the PDF if done already
                if values['status'] == res_success:
                    storeMaterialExport(values['url'], export_obj)
                    ready = True
                elif values['status'] == res_pending:
                    # clear the object, prepare for retrying download
                    if isExportExpired(export_obj.name):
                        export_obj.delete()
                elif values['status'] != res_pending:
                    # failure, delete the export object
                    export_obj.delete()

        elif export_obj.path:
            ready = True
    return ready


def isExportExpired(request_time):
    """ Check if the export has exceeded limit time or not.
        If yes: delete the export object.
    """
    if isinstance(request_time, str) or isinstance(request_time, unicode):
        rq_time = datetime.strptime(request_time, EXPORT_TIME_FORMAT)
    else:
        rq_time = request_time
    delta = datetime.now() - rq_time
    return delta.total_seconds() > EXPORT_TIME_LIMIT


def writeFileToDir(dir_path, file_name, content):
    """ Write a file with given file name and content into specific directory
    """
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'wb') as wf:
        wf.write(content)


def buildZipPath(path):
    """ Return the path of material zip file
    """
    if path[-1] == '/':
        path = path[:-1]
    return path + '.zip'


def buildZipCommand(path):
    """ Build the external command for zipping material files
    """
    #return 'zip -5 %s %s/*' % (buildZipPath(path), path)
    return 'zip -5 %s ./*' % buildZipPath(path)


def createDirectory(dir_path):
    """ Create new directory, and ensure it's empty
    """
    try:
        os.mkdir(dir_path)
    except OSError:
        rmtree(dir_path)
        os.mkdir(dir_path)


def createMaterialDirectory(dir_path, material):
    """ Create directory for material which includes all material files,
        HTML content, and manifest file
    """
    mid = material.material_id
    version = material.version

    createDirectory(dir_path)

    # add material text content
    raw_content = material.text
    try:
        raw_content = raw_content.encode('utf-8')
    except:
        raw_content = raw_content.decode('utf-8').encode('utf-8')
    writeFileToDir(dir_path, ZIP_HTML_FILE, raw_content)

    # read all material files, and put into the zip package
    mfids = listMaterialFiles(mid, version)
    for mfid in mfids:
        try:
            mf = MaterialFile.objects.get(id=mfid)
            writeFileToDir(dir_path, mf.name, mf.mfile.read())
            mf.mfile.close()
        except:
            print "Error getting material file %s" % mf.name

    # generate material json
    persons = models.getMaterialPersons(material.id)
    try:
        author_ids = persons['author'].split(',')
    except:
        author_ids = []
    author_names = models.getPersonName(author_ids)
    index_content = {
        'title': material.title,
        'url': MOD_SOURCE_URL % material.material_id,
        'authors': author_names,
        'version': material.version,
        'language': material.language,
        }
    index_content = json.dumps(index_content)
    writeFileToDir(dir_path, ZIP_INDEX_MODULE, index_content)


def zipMaterialExternal(material):
    """ Collects all material info and put into a folder, then call
        external zip command to do its job.
        Full path of the zip file will be returned to the caller.
    """
    mid = material.material_id
    version = material.version
    mtype = material.material_type

    # create material directory
    dir_path = os.path.join(settings.TEMP_DIR, '%s-%d' % (mid, version))

    # check if module or collection
    if mtype == MTYPE_MODULE:
        createMaterialDirectory(dir_path, material)

    elif mtype == MTYPE_COLLECTION:
        createDirectory(dir_path)

        # get list of all contained materials
        all_materials = getNestedMaterials(material)

        # load materials into ZIP
        for cid in range(len(all_materials)):
            m_id = all_materials[cid][0]
            m_version = all_materials[cid][1] or \
                models.getMaterialLatestVersion(m_id)
            m_object = models.getMaterial(m_id, m_version)
            m_path = os.path.join(dir_path, m_id)
            createMaterialDirectory(m_path, m_object)

        # prepare some fields
        try:
            editor_ids = models.getMaterialPersons(material.id)['editor']
            editor_ids = editor_ids.split(',')
            editors = models.getPersonName(editor_ids)
        except KeyError:
            editors = ['']
        if isinstance(editors, str):
            editors = [editors,]
        material_url = COL_SOURCE_URL % material.material_id

        # generate collection.json
        try:
            index_content = json.loads(material.text)
            index_content['id'] = material.material_id
            index_content['title'] = material.title
            index_content['version'] = material.version
            index_content['license'] = MATERIAL_LICENSE
            index_content['url'] = material_url
            index_content['editors'] = editors
            index_content['language'] = material.language
            index_content = json.dumps(index_content)
        except:
            # another way
            index_content = '{"id":"%s",' % material.material_id
            index_content += '"title":"%s",' % material.title
            index_content += '"version":"%s",' % str(material.version)
            index_content += '"license":"%s",' % MATERIAL_LICENSE
            index_content += '"url":"%s",' % material_url
            index_content += '"editors":"%s",' % editors
            index_content += '"language":"%s",' % material.language
            index_content += material.text[material.text.index('{')+1:]

        with open(os.path.join(dir_path, ZIP_INDEX_COLLECTION), 'w') as mnf:
            mnf.write(index_content)

    # zip the material files
    cmd = 'zip -r5 %s ./*' % buildZipPath(dir_path)
    process = Popen(cmd, shell=True, cwd=dir_path)
    try:
        process.wait()
    except TimeoutExpired:
        print 'Timed-out when creating material ZIP file'
    finally:
        rmtree(dir_path)

    if process.poll() == 0:
        return buildZipPath(dir_path)


def getNestedMaterials(material):
    """Returns list of material IDs of children inside collection material"""
    materials = []
    try:
        # get all material IDs and versions
        nodes = eval(material.text)['content']
        for node in nodes:
            materials.extend(extractMaterialInfo(node))
    except:
        print 'Error getting nested materials of ' + material.material_id
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


@api_log
def getMaterialZip(request, *args, **kwargs):
    """ Return compressed files (Zip) of a material
    """
    material = models.getMaterial(kwargs['mid'], kwargs.get('version', None))
    zip_path = zipMaterial(material)
    try:
        with open(zip_path, 'rb') as zf:
            zip_name = '%s-%d.zip' % (material.material_id, material.version)
            response = HttpResponse(zf.read(),
                                    mimetype='application/zip')
            response['content-disposition'] = 'attachment; filename='+zip_name
            return response
    except:
        raise Http404


@api_log
def getMaterialExport(request, *args, **kwargs):
    """ Check and return the PDF file of given material if exist
    """
    format_name = request.path.strip('/').split('/')[-1].lower()
    mid = kwargs.get('mid', None)
    version = kwargs.get('version', None)
    if version:
        version = int(version)
    else:
        # only catch the case of missing version ~ getting latest
        # error will be raised in other cases
        version = getMaterialLatestVersion(mid)
    material = Material.objects.get(material_id=mid, version=version)
    export_format, created = models.ExportFormat.objects.get_or_create(
        name=format_name, description='', base_path=format_name)

    get_it = False
    try:
        export_obj = MaterialExport.objects.get(
            material_id=mid, export_format=export_format, version=version)

        if str(request.GET.get('refresh', None)) == '1':
            export_obj.delete()
            get_it = requestMaterialExport(material, format_name)
            raise IOError

        # check if exported file existing
        if isExportProcessing(export_obj):
            get_it = requestMaterialExport(material, format_name)
        elif not os.path.exists(export_obj.path):
            export_obj.delete()
            raise IOError
        else:
            get_it = True
    except (MaterialExport.DoesNotExist, IOError):
        get_it = requestMaterialExport(material, format_name)
    except:
        raise Http404

    # ready for download or not?
    if get_it:
        export_obj = MaterialExport.objects.get(pk=export_obj.id)
        # return the PDF content, this should be served be the web server
        with open(export_obj.path, 'rb') as pdf:
            pdf_name = '%s-%d.%s' % (mid, version, format_name)
            data = pdf.read()
            response = HttpResponse(
                data, mimetype=settings.EXPORT_MIMETYPES[format_name])
            try:
                friendly_name = '%s.%s' % (
                    material.title.encode('utf-8'),
                    format_name)
            except UnicodeEncodeError:
                friendly_name = '%s.%s' % slugify(material.title)
            except:
                friendly_name = pdf_name
            response['content-disposition'] = 'attachment; filename="%s"' % friendly_name
            return response
    else:
        return HttpResponse(status=HTTP_CODE_PROCESSING)


@api_log
def getMaterialFile(request, *args, **kwargs):
    """ Return request for downloading material file
    """
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
    """ Returns the avatar image of specific person
    """
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
            person.invalidate()
            return HttpResponse('Person avatar deleted', status=200)
    except:
        raise Http404


def zipMaterialInternal(material):
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
            try:
                mf = MaterialFile.objects.get(id=mfid)
                zf.writestr(mf.name, mf.mfile.read()) 
                mf.mfile.close()
            except:
                print "Error when getting material file %s" % mf.name

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
            'url': MOD_SOURCE_URL % material.material_id,
            'authors': author_names,
            'version': material.version,
            'language': material.language,
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
        material_url = COL_SOURCE_URL % material.material_id

        # generate collection.json
        try:
            index_content = json.loads(material.text)
            index_content['id'] = material.material_id
            index_content['title'] = material.title
            index_content['version'] = str(material.version)
            index_content['license'] = MATERIAL_LICENSE
            index_content['url'] = material_url
            index_content['editors'] = editors
            index_content['language'] = material.language
            index_content = json.dumps(index_content)
        except:
            # another way
            index_content = '{"id":"%s",' % material.material_id
            index_content += '"title":"%s",' %  material.title
            index_content += '"version":"%s",' % str(material.version)
            index_content += '"license":"%s",' % MATERIAL_LICENSE
            index_content += '"url":"%s",' % material_url
            index_content += '"editors":"%s",' % editors
            index_content += '"language": "%s",' %  material.language
            index_content += material.text[material.text.index('{')+1:]
        zf.writestr(ZIP_INDEX_COLLECTION, index_content)

    zf.close()
    return realpath(zf.filename)
