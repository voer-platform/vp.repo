# Create your views here.
from os.path import realpath
import requests
import os

from zipfile import ZipFile, ZIP_DEFLATED
from django.http import Http404, HttpResponse

from vpr_content.models import Material, MaterialFile, MaterialExport
from vpr_content.models import listMaterialFiles, MaterialExport
from vpr_content.models import getLatestMaterial, getMaterialLatestVersion

from django.conf import settings

ZIP_HTML_FILE = 'index.html'


def requestMaterialPDF(material):
    """ Create the zip package and post it to vpt in order to 
        receive the PDF genereated.
        After receiving the file exported, an entry of export
        material will be created (as MaterialExport)

    """
    EXPORT_TYPE = 'pdf'

    # prepare the post data
    mzip = open(zipMaterial(material), 'rb')
    payload = {'token': '', 
               'cid': '',
               'output': EXPORT_TYPE}

    export_url = settings.VPT_URL + 'export'
    files = {'file': (mzip.name.split('/')[-1], mzip.read())}
    res = requests.post(export_url, files=files, data={})

    # delete the temp ZIP
    mzip.close()
    os.remove(mzip.name) 

    # receive and save to file (PDF)
    if res.status_code == 200:
        export_path = material.material_id + '-' + str(material.version)
        export_path += '.pdf'
        export_path = os.path.join(settings.EXPORT_DIR, export_path)
        with open(export_path, 'wb') as ofile:
            ofile.write(res.content)
            export_path= os.path.realpath(ofile.name)

        # create material export record
        try:
            me_obj = MaterialExport.objects.get(
                material_id = material.material_id,
                version     = material.version)
        except:
            me_obj = MaterialExport()
            me_obj.material_id = material.material_id
            me_obj.version = material.version
        me_obj.path = export_path
        me_obj.file_type = EXPORT_TYPE
        me_obj.save()
    else:
        print '[ERR] Exporting to PDF failed. Error occurs when calling the VPT export'
        print '\t' + res.content.replace('\n', '\n\t') + '\n'


def zipMaterial(material):
    """ Collects all material info and put it into a ZIP file.
        Full path of the zip file will be returned to the caller.
    """

    mid = material.material_id
    version = material.version
    
    # init the zip package
    zip_path = os.path.join(
        settings.TEMP_DIR,
        'm-'+str(mid)+'-'+str(version)+'.zip'
        )
    zf = ZipFile(zip_path, 'w', ZIP_DEFLATED) 

    # read all material files, and put into the zip package
    mfids = listMaterialFiles(mid, version)
    for mfid in mfids:
        mf = MaterialFile.objects.get(id=mfid)
        zf.writestr(mf.name, mf.mfile.read())
        mf.mfile.close()

    # add material text content
    zf.writestr(ZIP_HTML_FILE, material.text)
    zf.close()
    return realpath(zf.filename)


def getMaterialPDF(request, *args, **kwargs):
    """ Check and return the PDF file of given material if exist
    """
    mid = kwargs.get('mid', None)
    version = kwargs.get('version', None)
   
    if not version:
        version = getMaterialLatestVersion(mid)
    try:
        export_obj = MaterialExport.objects.get(material_id=mid,
                                                version=version)
        with open(export_obj.path, 'rb') as pdf:
            data = pdf.read()
        return HttpResponse(data, mimetype='application/pdf')
    except:
        raise Http404
    
