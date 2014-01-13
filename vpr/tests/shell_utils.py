from vpr_content import models
from datetime import datetime, timedelta
import random


def generate_fav_sample():
    """Add sample favorite data into database
    """
    random.seed(str(datetime.utcnow()))
    pids = {random.randint(1,100) for _ in range(10)}

    while pids:
        pid = pids.pop()
        lknum = random.randint(1, 40)
        liked = []
        for lk in range(lknum):
            mid = random.randint(1, 10000)
            while mid in liked:
                mid = random.randint(1, 10000)
            try:
                new_like = models.MaterialFavorite(material_id=mid, person_id=pid)
                new_like.save()
                liked.append(mid)
            except:
                print 'Error adding: %d - %d' % (mid, pid)


def testSimilar():
    from vpr_content.models import Material
    m = Material.objects.get(material_id='c218f699')
    from haystack.query import SearchQuerySet as SQS;
    res = SQS().models(models.Material).more_like_this(m)[:10]
    [item for item in res[:10]]
    return res

def addMissingMP(person_id, slist):
    # get material raw IDs
    mids = slist.split('\n')
    rids = [item['id'] for item in models.Material.objects.filter(material_id__in=mids).values('id')]
    print rids
    for rid in rids:
        models.MaterialPerson.objects.create(
            material_rid = rid,
            person_id = person_id,
            role=0)
        models.MaterialPerson.objects.create(
            material_rid = rid,
            person_id = person_id,
            role=1)
    print 'DONE'
