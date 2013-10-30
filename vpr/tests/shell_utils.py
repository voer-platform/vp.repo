from vpr_content import models
from datetime import datetime, timedelta


def timeMe(func):
    """Get time executing a function"""
    t0 = datetime.now()
    res = func()
    delta = datetime.now() - t0
    print '[ ', delta.total_seconds(), ' ]'
    return res

def qp0():
    from haystack.query import SearchQuerySet as SQS;
    res = SQS().models(models.Person).filter(content='minh')
    [item for item in res]
    return res


def qm0():
    from haystack.query import SearchQuerySet as SQS;
    res = SQS().models(models.Material).filter(content='minh')
    print res.count()
    [item for item in res[:10]]
    return res

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
