from django.db import connection
from vpr_content import models

def removeDuplicatedTitleInMaterial():
    cur = connection.cursor()
    qr0 = 'select id from vpr_content_material'
    qr1 = 'select text from vpr_content_material where id=%d'
    qr2 = 'update vpr_content_material set text=\'%s\' where id=%d'
    pt0 = '<div class="title">'
    pt1 = '</div>'

    cur.execute(qr0)
    mids = cur.fetchall()

    for mid in mids:
        try:
            mid = mid[0]
            cur.execute(qr1 % mid)
            text = cur.fetchone()[0]

            p0 = text.find(pt0)
            p1 = text.find(pt1, p0)
            text = text[:p0] + text[p1+len(pt1)+1:]
            
            material = models.Material.objects.get(pk=mid)
            material.text = text
            material.save()

            print mid
        except:
            raise
            print 'Updating failed at ' + str(mid)


