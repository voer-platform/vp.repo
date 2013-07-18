from django.db import connection
from vpr_storage.views import requestMaterialPDF
from vpr_content.models import Material


def getAllMaterialIDs():
    """ """
    cursor = connection.cursor()
    cursor.execute('select material_id from vpr_content_material')
    all_ids = [item[0] for item in cursor.fetchall()]

    # get exported materials
    cursor.execute('select material_id from vpr_content_materialexport')
    export_ids = [item[0] for item in cursor.fetchall()]
    for mid in export_ids:
        all_ids.remove(mid)

    return all_ids


def requestAllPDFs():
    mids = getAllMaterialIDs()
    count = 1
    for mid in mids:
        try:
            print '[%d/%d] Exporting material %s...' % (count, len(mids), mid)
            material = Material.objects.get(material_id=mid)
            requestMaterialPDF(material)
            count += 1
        except:
            print 'Failed by unknown error... sorry.'

    print 'All is done. Congrats!'
