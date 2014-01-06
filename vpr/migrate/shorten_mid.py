from vpr_content.models import Material, generateMaterialId
from vpr_content.models import OriginalID, MaterialFile, MaterialExport 
from django.db import connection, transaction

def get_long_mids():
    """ Returns all id and material_id of material having old id style
    """
    res = Material.objects.filter().extra(where=['CHAR_LENGTH(material_id)>8'])
    return res.values_list('material_id', flat=True)
    

def shorten_material_id(old_id):
    """ Reduce length of long material IDs from 32 to 8 characters
    """
    try:
        new_id = generateMaterialId()
        Material.objects.filter(material_id=old_id).update(material_id=new_id)
        OriginalID.objects.filter(material_id=old_id).update(material_id=new_id)
        MaterialFile.objects.filter(material_id=old_id).update(material_id=new_id)
        MaterialExport.objects.filter(material_id=old_id).update(material_id=new_id)
        print '%s >> %s' % (old_id, new_id)
    except:
        print 'Error with ' + old_id


def shorten_material_id_2(old_id):
    """ Reduce length of long material IDs from 32 to 8 characters
    """
    cur = connection.cursor()
    try:
        new_id = generateMaterialId()
        tables = (
            'vpr_content_material',
            'vpr_content_originalid', 
            'vpr_content_materialexport',
            'vpr_content_materialfile'
            )
        for t in tables:
            sql = """UPDATE %s SET material_id='%s' WHERE material_id='%s';""" \
                % (t, new_id, old_id)
            res = cur.execute(sql)
        transaction.commit_unless_managed()
        print '%s >> %s' % (old_id, new_id)
    except:
        raise
        print 'Error with ' + old_id


if __name__ == '__main__':
    count = 0
    all_mids = get_long_mids();
    for mid in all_mids:
        shorten_material_id(mid)
        count += 1
    print 'TOTAL: ' + str(count)

