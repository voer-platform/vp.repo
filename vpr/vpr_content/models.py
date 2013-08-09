from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from django.db.models import DateTimeField, ImageField 
from django.conf import settings
from hashlib import md5
from datetime import datetime
import time

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


def generateMaterialId():
    """ Ensure generating of unique material ID
    """
    sugar = ''
    while True:
        #temp_id = md5(str(datetime.now()) + sugar).hexdigest()
        temp_id = md5(str(time.time()) + sugar).hexdigest()
        temp_id = temp_id[:MATERIAL_ID_SIZE]
        if Material.objects.filter(material_id=temp_id).count() > 0:
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
    keywords = TextField(blank=True, null=True)
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


class MaterialPerson(models.Model):
    """Assign role to each person inside material"""
    material_rid = IntegerField()
    person_id = IntegerField()
    role = IntegerField()   # see the settings.VPR_MATERIAL_ROLES


# ----------------


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


def getMaterialPersons(material_rid):
    """
    """
    roles = settings.VPR_MATERIAL_ROLES
    mapped_roles = MaterialPerson.objects.filter(material_rid=material_rid)
    material_roles = {}
    for mrole in mapped_roles:
        try:
            material_roles[roles[mrole.role]].append(str(mrole.person_id))
        except KeyError:
            material_roles[roles[mrole.role]] = [str(mrole.person_id)]
    
    for role in material_roles:
        material_roles[role] = ','.join(material_roles[role])

    return material_roles
            

def setMaterialPersons(material_rid, request):
    """ """
    # remove all existing record of the material
    material_rid = int(material_rid)
    MaterialPerson.objects.filter(material_rid=material_rid).delete()
    for role in settings.VPR_MATERIAL_ROLES:
        try:
            values = request.get(role, '').split(',')
            for pid in values:
                mp = MaterialPerson(
                    material_rid = material_rid,
                    person_id = int(pid),
                    role = settings.VPR_MATERIAL_ROLES.index(role)
                    )
                mp.save()
        except:
            pass

    

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


def countPersonMaterial(person_id, roles=()):
    """Counts number of material where person participates into"""
    result = {}
    query = "SELECT COUNT(id) FROM vpr_content_materialperson"
    query += " WHERE role=%d AND person_id=%d;"

    person_id = int(person_id)
    if type(roles) not in (tuple, list):
        roles = (int(roles),)

    for role_id in roles:
        try:
            cur = connection.cursor()
            cur.execute(query % (role_id, person_id))
            result[settings.VPR_MATERIAL_ROLES[role_id]] = int(cur.fetchone()[0])
        except:
            pass
    return result


# MIGRATING FUNCTIONS


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


def resetPersonRoles():
    """Refresh values of person roles to original set"""

    roles = ('author', 'editor', 'licensor', 'maintainer', 'translator')
    MaterialRole.objects.all().delete()
    rmap = {}
    for rname in roles:
        role = MaterialRole(name=rname)
        role.save()
        rmap[rname] = role.id

    return rmap

    
def migratePersonRoles():
    """ """
    roles = settings.VPR_MATERIAL_ROLES
    
    cursor = connection.cursor()
    cursor.execute('SELECT id, authors, editor_id FROM vpr_content_material')
    old_values = cursor.fetchall()

    role_author = roles.index('author')
    role_editor = roles.index('editor')
    
    for val in old_values:
        assign_person = MaterialPerson(
            material_rid = val[0], 
            person_id = int(val[1]), 
            role = role_author)
        assign_person.save()

        assign_person = MaterialPerson(
            material_rid = val[0], 
            person_id = int(val[1]), 
            role = role_editor)
        assign_person.save()
    

if __name__ == '__main__':
    import doctest
    doctest.testmod()
