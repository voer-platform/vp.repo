from django.db.models import Q
from models import Material, Person
import math


def get_page(pid, qset, per_page=20):
    """ Returns item list of specific page in result
            pid: ID of page, start from 1
    """
    start_on = (pid-1)*per_page
    count = 0
    if hasattr(qset, 'count'):
        count = qset.count()
    elif hasattr(qset, '__sizeof__'):
        count = qset.__sizeof__()
    page_total = int(math.ceil(1.0*count/per_page))
    res = qset[start_on:start_on+per_page]
    return res, page_total


class MaterialScanner(object):
    """docstring for MaterialScanner"""

    extract_fields = ['id', 'material_type', 'title', 'material_id', 'version']

    def __init__(self, **kwargs):
        super(MaterialScanner, self).__init__()
        self.m = Material.objects
        self.per_page = 20
    
    def filter(self, condition):
        func = getattr(self, 'filter_'+condition, None)    
        if func:
            return func()
        else:
            return []

    def filter_description(self):
        """ Return list of material having blank or no-blank description
        """
        q = Q(description__isnull=True)
        q = q | Q(description__regex='^(\s|-)*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_image(self):
        """ Return list of material having blank or no-blank description
        """
        q = Q(image__isnull=True) | Q(image='')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_keywords(self):
        q = Q(keywords__isnull=True)
        q = q | Q(keywords__regex='^\s*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_language(self):
        q = Q(keywords__isnull=True)
        q = q | Q(language__regex='^\s*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_categories(self):
        q = Q(categories__isnull=True)
        q = q | Q(categories__regex='^\s*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_author(self):
        sql0 = 'SELECT DISTINCT(material_rid) FROM vpr_content_materialperson WHERE role=0'
        sql1 = 'SELECT %s FROM vpr_content_material WHERE id NOT IN (%s)' % (','.join(self.extract_fields), sql0)
        res = self.m.raw(sql1)
        return res 

    def filter_content(self, text_limit=500):
        res = self.m.extra(where=['CHAR_LENGTH(text)<'+str(text_limit)]).values(*self.extract_fields)
        return res 


def buildPageURLs(request, pg_count=None):
    """ Return the URLs of next and previous page from current one
    """
    page = int(request.GET.get('page', 1))
    query = request.GET.dict()
    pre_location = request.path + '?' 
    url_next = url_prev = None

    if (pg_count and page < pg_count) or not pg_count:
        query['page'] = page + 1
        query_st = '&'.join([k+'='+unicode(query[k]) for k in query])
        next_location = pre_location + query_st 
        url_next = request.build_absolute_uri(next_location)
        
    if page > 1:
        query['page'] = page - 1
        query_st = '&'.join([k+'='+unicode(query[k]) for k in query])
        prev_location = pre_location + query_st 
        url_prev = request.build_absolute_uri(prev_location)

    return url_prev, url_next

