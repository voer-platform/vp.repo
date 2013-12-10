from django.db import models
from django.db.models import CharField, TextField, FileField
from django.db.models import IntegerField, CommaSeparatedIntegerField
from django.db.models import DateTimeField, ImageField, ForeignKey
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete

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
    fullname = CharField(max_length=256)
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
    modified = DateTimeField(default=datetime.utcnow)
    derived_from = CharField(max_length=64, blank=True, null=True)
    image = ImageField(upload_to="./mimgs", blank=True, null=True) 

    def __unicode__(self):
        type_name = settings.MATERIAL_TYPES[self.material_type][:3]
        return '%s - %s (%s)' % (type_name, self.title, self.material_id)


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


class MaterialComment(models.Model):
    """ Comments of materials
    """
    material = ForeignKey('Material')
    person = ForeignKey('Person')
    comment = TextField()
    modified = DateTimeField(default=datetime.utcnow)


class MaterialRating(models.Model):
    """ Store extra information of material, like: favorite, rated
    """
    material = ForeignKey('Material')
    person = ForeignKey('Person')
    rate = IntegerField()


class MaterialFavorite(models.Model):
    """ Store extra information of material, like: favorite, rated
    """
    material = ForeignKey('Material')
    person = ForeignKey('Person')


class MaterialViewCount(models.Model):
    """ View count of material
    """
    material = ForeignKey('Material', primary_key=True)
    count = IntegerField()
    last_visit = DateTimeField(default=datetime.utcnow)


# ----------------


def getMaterial(material_id='', version=None, raw_id=None):
    """ Short call for getting material using its ID and version. If
        raw ID is provided, function will use it and bypass other params.
    """
    material = None
    if not raw_id:
        if not version:
            material = getLatestMaterial(material_id) 
        else:
            material = Material.objects.get(
                material_id=material_id, 
                version = version)
    else:
        material = Material.objects.get(pk=raw_id)

    return material 


def getLatestMaterial(material_id):
    """ Returns the latest version of the material with given ID """
    material = Material.objects.filter(material_id=material_id)\
                                      .order_by('version') \
                                      .reverse()[0]
    return material 


def getMaterialLatestVersion(material_id):
    """ Returns the value of newest material version
    """
    version = Material.objects.filter(material_id=material_id)\
                                      .order_by('version') \
                                      .reverse().values('version')[0]
    return version['version'] 


def listMaterialFiles(material_id, version):
    """Returns all IDs of files attached to specific material, except the material image
    """
    file_ids = []
    if material_id and version:
        mfiles = MaterialFile.objects.filter(material_id=material_id, 
                                             version=version)
        file_ids = [mf.id for mf in mfiles]

    return file_ids   


def getMaterialRawID(material_id, version=None):
    """ Returns the raw ID of specific material
    """
    try:
        if not version:
            version = getMaterialLatestVersion(material_id)
        mrid = Material.objects.filter(
            material_id=material_id, version=version).values('id')[0]
        mrid = mrid['id']
    except:
        mrid = None
    return mrid


def convertMaterialRawID(material_rid):
    """ Return correspondent material_id and version of given raw ID
    """
    try:
        data = Material.objects.filter(id=material_rid).values('material_id', 'version')[0]
        return data['material_id'], data['version']
    except IndexError:
        pass 
    except ValueError:
        pass


def getMaterialPersons(material_rid):
    """Returns dict of persons related to specific material. This uses
    material raw ID instead of material_id"""

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


def getPersonName(person_id):
    """Returns name of given person IDs. Accept input as string or 
    list & tuple"""

    if isinstance(person_id, list) or isinstance(person_id, tuple):
        persons = Person.objects.filter(pk__in=person_id)
        name_dict = {}
        for p in persons:
            name_dict[str(p.id)] = p.fullname or p.user_id
        result = [name_dict[str(pid)] for pid in person_id if pid in name_dict]
    else:
        try:
            person = Person.objects.get(id=person_id)
            result = person.fullname or person.user_id
        except:
            result = ''
    return result


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
        enclosed_id = SINGLE_ASSIGNED_CATEGORY % str(category_id)
        cmd = "SELECT COUNT(id) FROM vpr_content_material WHERE categories LIKE '%%%%%s%%%%';" % enclosed_id 
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


def deleteMaterial(material_id, version):
    """Try to delete material with given ID and version"""
    try:
        obj = Material.objects.get(
            material_id=material_id,
            version=version)
        obj.delete()
        result = True
    except Material.DoesNotExist:
        result = True
    except:
        result = False 
    return result


@receiver(post_delete, sender=Material)
def finishDeleteMaterial(sender, **kwargs):
    """Delete all related data right after deleting the material"""
    material_id = kwargs['instance'].material_id
    mrid = kwargs['instance'].id

    # remove all related content
    OriginalID.objects.filter(material_id=material_id).delete()
    MaterialExport.objects.filter(material_id=material_id).delete()
    MaterialFile.objects.filter(material_id=material_id).delete()
    MaterialPerson.objects.filter(material_rid=mrid).delete()


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
    

def migratePersonFullname():
    """ Auto use user id as fullname if blank 
    """
    res = Person.objects.filter().values('id', 'user_id', 'fullname')
    persons = [item for item in res if not item['fullname']]
    for p in persons:
        Person.objects.filter(pk=p['id']).update(fullname=p['user_id'])


def refineAllMaterialContent():
    """ Run refineMaterialContent() on all existing records 
    """
    all_ids = Material.objects.filter(material_type=1).values('id')
    all_ids = [_['id'] for _ in all_ids]
    for rid in all_ids:
        text = Material.objects.filter(pk=rid).values('text')[0]['text']
        text = refineMaterialContent(text)
        Material.objects.filter(pk=rid).update(text=text)
        print rid


def refineMaterialContent(text):
    """ Refine the body of material, remove some danger tags,...
            <em class="emphasis" effect="italics"/>
            <strong class="emphasis" effect="bold"/>
        This also should remove Js and styling content.
    """
    kill_list = (
        '<em class="emphasis" effect="italics"/>',
        '<strong class="emphasis" effect="bold"/>',
        )
    for piece in kill_list:
        text = text.replace(piece, '')
        
    return text


if __name__ == '__main__':
    import doctest
    doctest.testmod()
