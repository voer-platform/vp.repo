# Create your views here.
from os.path import realpath
import requests
import os

from zipfile import ZipFile, ZIP_DEFLATED
from django.http import Http404 

from vpr_content.models import Material, MaterialFile
from vpr_content.models import listMaterialFiles, MaterialExport

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

    # receive and save to file (PDF)
    if res.status_code == 200:
        export_path = material.material_id + '-' + str(material.version)
        export_path += '.pdf'
        export_path = os.path.join(settings.EXPORT_DIR, export_path)
        with open(export_path, 'wb') as ofile:
            ofile.write(res.content)
            export_path= os.path.dirname(ofile.name)

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
        pass


def zipMaterial(material):
    """ Collects all material info and put it into a ZIP file.
        Full path of the zip file will be returned to the caller.
    """

    mid = material.material_id
    version = material.version
    
    # init the zip package
    zf = ZipFile('m-'+str(mid)+'-'+str(version)+'.zip', 'w', ZIP_DEFLATED) 

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
