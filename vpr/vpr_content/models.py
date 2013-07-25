from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from django.db.models import DateTimeField, ImageField 
from hashlib import md5
from datetime import datetime

from vpr_api.models import APIClient
from repository import MaterialBase

MATERIAL_ID_SIZE = 8

# Create your models here.
class Category(models.Model):
    name = CharField(max_length=255)
    parent = IntegerField(default=0)
    description = TextField(blank=True)


class Person(models.Model):
    user_id = CharField(max_length=64)
    fullname = CharField(max_length=256, blank=True, null=True)
    first_name = CharField(max_length=64, blank=True, null=True)
    last_name = CharField(max_length=64, blank=True, null=True)
    email = CharField(max_length=64, blank=True, null=True)
    title = CharField(max_length=32, blank=True, null=True)
    homepage = CharField(max_length=255, blank=True, null=True)
    affiliation = CharField(max_length=255, blank=True, null=True)
    affiliation_url = CharField(max_length=255, blank=True, null=True)
    national = CharField(max_length=255, blank=True, null=True)
    biography = TextField(blank=True, null=True)
    client_id = IntegerField(default=0)
    avatar = ImageField(upload_to="./mimgs/persons", blank=True, null=True) 


class Editor(models.Model):
    fullname = CharField(max_length=255, blank=True)
    user_id = CharField(max_length=64, blank=True)
    client_id = IntegerField(default=0)

# (z) I don't think we will use this anymore.
# Using normal pk field would be good enough.
def generateMaterialId():
    """ Ensure generating of unique material ID
    """
    sugar = ''
    while True:
        temp_id = md5(str(datetime.now) + sugar).hexdigest()
        temp_id = temp_id[:MATERIAL_ID_SIZE]
        if len(Material.objects.filter(material_id=temp_id)) > 0:
            sugar += '1'
        else:
            break
    return temp_id


def assignSingleCat(material_rid, cat_id):
    mcat = MaterialCategory()
    mcat.material_rid = material_rid 
    mcat.category_id = cat_id
    mcat.save()
    return mcat


class Material(models.Model, MaterialBase):
    material_id = CharField(max_length=64, default=generateMaterialId)
    material_type = IntegerField(default=1)
    text = TextField()
    version = IntegerField(default=1)
    title = CharField(max_length=255)
    description = TextField(blank=True, null=True)
    categories = CharField(max_length=256, blank=True, null=True)
    authors = CommaSeparatedIntegerField(max_length=8)
    editor_id = IntegerField()
    keywords = TextField(blank=True, null=True)
    #file = FileField(upload_to=".", null=True)
    #file_type = CharField(max_length=64, blank=True)
    language = CharField(max_length=2, blank=True)
    license_id = IntegerField(null=True)
    modified = DateTimeField(default=datetime.now)
    derived_from = CharField(max_length=64, blank=True, null=True)
    image = ImageField(upload_to="./mimgs", blank=True, null=True) 


class OriginalID(models.Model):
    material_id = CharField(max_length=64, primary_key=True)
    original_id = CharField(max_length=32)


class MaterialFile(models.Model):
    material_id = CharField(max_length=64)
    version = IntegerField(default=1)
    name = CharField(max_length=255, blank=True, null=True)
    description = TextField(blank=True, null=True)
    mfile = FileField(upload_to="./mfiles")
    mime_type = CharField(max_length=100)


class MaterialExport(models.Model):
    """ Model for storing export product of the Material
    """
    material_id = CharField(max_length=64)
    version = IntegerField(default=1)
    name = CharField(max_length=255, blank=True, null=True)
    path = CharField(max_length=255)
    file_type = CharField(max_length=32, blank=True, null=True)


def getLatestMaterial(material_id):
    """ Returns the latest version of the material with given ID """
    material = Material.objects.filter(material_id=material_id)\
                                      .order_by('version') \
                                      .reverse()[0]
    return material 


def getMaterialLatestVersion(material_id):
    """ Returns the value of newest material version
    """
    material = getLatestMaterial(material_id)
    return material.version


def listMaterialFiles(material_id, version):
    """Returns all IDs of files attached to specific material, except the material image
    """
    file_ids = []
    if material_id and version:
        mfiles = MaterialFile.objects.filter(material_id=material_id, 
                                             version=version)
        file_ids = [mf.id for mf in mfiles]

    return file_ids   


from django.db import connection

SINGLE_ASSIGNED_CATEGORY = '(%s)'

def countAssignedMaterial(category_id):
    """Counts and returns the number of material assigned to specific 
    category"""
    res = None
    try:
        category_id = SINGLE_ASSIGNED_CATEGORY % str(category_id)
        cmd = "SELECT COUNT(id) FROM vpr_content_material WHERE categories LIKE '%s';" % category_id
        cur = connection.cursor()
        cur.execute(cmd)
        res = cur.fetchone()[0]
    except:
        pass
        # fires some log here
    return res

def refineAssignedCategory(category_id):
    """Returns the standardized value of categories, which will be saved
    into DB"""
    cat_list = category_id.split(',')
    new_value = ''
    for cat_id in cat_list:
        if cat_id.strip():
            new_value += SINGLE_ASSIGNED_CATEGORY % cat_id.strip()
    return new_value


def restoreAssignedCategory(value):
    """Converts the formatted values of categoriy IDs into normal numbers.
    Example:
    >>> restoreAssignedCategory('(123)')
    [123]
    >>> restoreAssignedCategory(' (123) ')
    [123]
    >>> restoreAssignedCategory('(123)')
    [123]
    >>> restoreAssignedCategory('(1)(321)')
    [1, 321]
    >>> restoreAssignedCategory('()')
    []
    >>> restoreAssignedCategory('(321)(wrong)')
    [321]
    >>> restoreAssignedCategory('123)')
    []
    >>> restoreAssignedCategory('(123')
    []
    """
    try:
        value = value.strip()
    except:
        value = ''
    cat_list = []
    w0 = SINGLE_ASSIGNED_CATEGORY[0]
    w1 = SINGLE_ASSIGNED_CATEGORY[-1]
    temp = ''
    for ch in value:
        if ch == w0: 
            temp = '+'
            continue
        elif ch == w1:
            try:
                cat_list.append(int(temp))
                temp = ''
            except ValueError:
                temp = ''
        elif temp: 
            temp += ch

    return cat_list


# MIGRATION

def changeMaterialCatValues():
    """Changes all assigned categories from format:
    '1, 2' to '(1)(2)'"""
    all_materials = Material.objects.all()  # OMG
    m_count = 1
    m_total = len(all_materials)
    w0 = SINGLE_ASSIGNED_CATEGORY[0]
    for material in all_materials:
        print '[%d/%d]' % (m_count, m_total)
        try:       
            if material.categories[0] != w0:
                material.categories = refineAssignedCategory(material.categories) 
                material.save()
        except:
            pass
        m_count += 1


if __name__ == '__main__':
    import doctest
    doctest.testmod()
