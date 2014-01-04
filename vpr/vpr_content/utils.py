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
    
    def filter_description(self, null=True):
        """ Return list of material having blank or no-blank description
        """
        q = Q(description__isnull=null)
        if null:
            q = q | Q(description__regex='^(\s|-)*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_image(self, null=True):
        """ Return list of material having blank or no-blank description
        """
        q = Q(image__isnull=null)
        return self.m.filter(q).values(*self.extract_fields)

    def filter_keywords(self, null=True):
        q = Q(keywords__isnull=null)
        if null:
            q = q | Q(keywords__regex='^\s*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_language(self, null=True):
        q = Q(keywords__isnull=null)
        if null:
            q = q | Q(language__regex='^\s*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_categories(self, null=True):
        q = Q(categories__isnull=null)
        if null:
            q = q | Q(categories__regex='^\s*$')
        return self.m.filter(q).values(*self.extract_fields)

    def filter_author(self):
        sql0 = 'SELECT DISTINCT(material_rid) FROM vpr_content_materialperson WHERE role=0'
        sql1 = 'SELECT %s FROM vpr_content_material WHERE id NOT IN (%s)' % (','.join(self.extract_fields), sql0)
        res = self.m.raw(sql1)
        return res 

    def filter_text(self, text_limit=500):
        sql1 = 'SELECT %s FROM vpr_content_material WHERE CHAR_LENGTH(text)<%d' % (','.join(self.extract_fields), text_limit)
        res = self.m.extra(where=['CHAR_LENGTH(text)<500']).values(*self.extract_fields)
        return res 
