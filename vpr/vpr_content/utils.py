from django.db.models import Q

from models import Material, Person


def get_page(pid, qset, per_page=20):
    """ Returns item list of specific page in result
            pid: ID of page, start from 1
    """
    start_on = (pid-1)*per_page
    res = qset[start_on:start_on+per_page]
    return res


class MaterialScanner(object):
    """docstring for MaterialScanner"""

    extract_fields = ['id', 'material_type', 'title', 'material_id', 'version']

    def __init__(self, **kwargs):
        super(MaterialScanner, self).__init__()
        self.m = Material.objects
        self.per_page = 20
    
    def filter(self, condition):
        func = getattr(self, 'filter_'+condition)    
        return func()

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

    def filter_text(self, text_limit=500):
        res = self.m.extra(where=['CHAR_LENGTH(text)<'+str(text_limit)]).values(*self.extract_fields)
        return res 
