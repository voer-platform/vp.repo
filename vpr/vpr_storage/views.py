# Create your views here.
from os.path import realpath
import requests

from zipfile import ZipFile, ZIP_DEFLATED
from django.http import Http404 

from vpr_content.models import Material, MaterialFile
from vpr_content.models import listMaterialFiles

from django.conf import settings

ZIP_HTML_FILE = 'index.html'


def requestMaterialPDF(material):
    """ Create the zip package and post it to vpt in order to 
        receive the PDF genereated
    """
    mzip = open(zipMaterial(material), 'rb')

    payload = {'token': '', 
               'cid': '',
               'output': 'pdf', 
               'file': mzip}

    res = requests.post(settings.VPT_URL + '/export', payload) 

    print res.status_code



def zipMaterial(material):
    """ Collects all material info and put it into a ZIP file.
        Full path of the zip file will be returned to the caller.
    """

    mid = material.material_id
    version = material.version
    
    # init the zip package
    zf = ZipFile('m-'+str(mid)+'-'+str(version)+'.zip', 'wb', ZIP_DEFLATED) 

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
