import requests
import zipfile
import re
import json
import requests as rq
import os

from os import path, listdir
from migrate import getTagContent, getAuthorInfo, buildRegex, getMetadata
from migrate import shell_getAllPersons, getAllPersons, getAllCategories, out, toResume
from migrate import VPR_URL, LOG_FILE, FAILED_FILE, RESUME_FILE, ORIGINAL_PREFIX

URL = 'http://rhaptos.voer.vn/content/%s/latest/source/'
URL_ZIP = 'http://rhaptos.voer.vn/content/%s/latest/complete/'
URL_ZIP_2 = 'http://rhaptos.voer.vn/content/%s/latest/module_export?format=zip'

vpr_categories = {}
vpr_persons = {}
vpr_idmap = {}

def downloadCollectionCNXML(cid):
    """Download and save cnxml file of specific collection"""
    try:
        url = URL_ZIP % cid
        res = requests.get(url)
        if res.status_code == 200:
            ofile = open(cid+'.zip', 'w')
            ofile.write(res.content)
            ofile.close()
            print "ZIP downloaded: " + cid
        else:
            print "Error while getting ZIP content of collection %s. Try to download CNXML file... " % cid
            url = URL % cid
            res = requests.get(url)
            if res.status_code == 200:
                ofile = open(cid+'.cnxml', 'w')
                ofile.write(res.content)
                ofile.close()
            else:
                print "Both were failed. Pls try this manually (%s)" % cid
    except:
        print "Both were failed. Pls try this manually (%s)" % cid
    

def downloadModule(mid):
    """ """
    try:
        url = URL_ZIP_2 % mid
        res = requests.get(url)
        if res.status_code == 200:
            ofile = open(mid+'.zip', 'w')
            ofile.write(res.content)
            ofile.close()
            print "ZIP downloaded: " + mid
        else:
            raise
    except:
        print 'Error when downloading module ' + mid


def downloadAllModules():
    """ """
    mf = open('missing_modules.txt', 'r')
    missing = json.loads(mf.read())
    for mid in missing:
        downloadModule(mid)
    return 'DONE'


def downloadAllCollections():
    all_ids = [cid.strip() for cid in RAW_COLLECTION_IDS.split('\n')]
    for cid in all_ids:
        if cid:
            downloadCollectionCNXML(cid) 



def getCollectionXML(collection_path):
    col_path = collection_path.lower().strip()
    xml_content = ''

    # extract the module ID in case of ZIP file
    if col_path.endswith('.zip'):
        zf = zipfile.ZipFile(col_path)
        xml_path = ''
        for file_name in zf.namelist():            
            if file_name.lower().endswith('collection.xml'):
                xml_path = file_name
                break
        if xml_path:
            xf = zf.open(xml_path)
            xml_content = xf.read()
            xf.close()
        zf.close()
    elif col_path.endswith('.cnxml') or col_path.endswith('.xml'): 
        cf = open(col_path)
        xml_content = cf.read()
        cf.close()
    xml_content = xml_content.replace('\n', '')

    return xml_content


def listIncludedModules(collection_path):
    """Returns list of modules IDs inside a collection"""

    xml_content = getCollectionXML(collection_path) 

    # read the list of modules
    re_module = re.compile('(?<=document=").*?(?=")')
    RTAG = '(?<=<%(tag)s\s).*?(?=</%(tag)s>)'
    rtag = buildRegex('col:module', RTAG)
    res = rtag.findall(xml_content)
    children = []
    for line in res:
        try:
            module_id = re_module.findall(line)[0]
            module_title = getTagContent('md:title', line)[0]
            children.append((module_id, module_title))
        except:
            pass
    
    return children
        
def saveAllNeededModules(root_path):
    """Save all needed modules into external file"""
    collections = listdir(root_path)
    included_modules = {}
    for col in collections:
        print '.'
        modules = listIncludedModules(path.join(root_path, col))
        for mod in modules:
            if mod[0] not in included_modules:
                included_modules[mod[0]] = mod[1]
    
    of = open('needed_modules.txt', 'w')
    of.write(json.dumps(included_modules))
    of.close()


# ./manage.py shell
def getMissingModules(mfile='needed_modules.txt'):
    """Determine if a module if missing from database"""
    from vpr_content.models import OriginalID

    mf = open(mfile, 'r')
    modules = json.loads(mf.read())
    mf.close()
    missing = {}

    for item in modules:
        try:
            oid = OriginalID.objects.filter(original_id__startswith=item)
            if len(oid) > 0:
                print item + ' exists'
            else:
                missing[item] = modules[item]
                print item + ' missing'
        except OriginalID.DoesNotExist:
            missing[item] = modules[item]
            print item + ' missing'
    
    mf = open('missing_modules.txt', 'w')
    mf.write(json.dumps(missing))
    mf.close()


# ./manage.py shell
def getMissingMaterials(mfile='all_ids.txt'):
    """Determine if a module if missing from database"""
    from vpr_content.models import OriginalID

    mf = open(mfile, 'r')
    all_ids = mf.read().split('\n')
    mf.close()
    of = open('missing_modules.txt', 'w')

    for item in all_ids:
        try:
            oid = OriginalID.objects.filter(original_id__startswith=item)
            if len(oid) > 0:
                print item + ' exists'
            else:
                of.write(item + '\n')
                print item + ' missing'
        except OriginalID.DoesNotExist:
            of.write(item + '\n')
            print item + ' missing'
    
    of.close()

# NEXT: EXTRACT COLLECTION INFORMATION


NO_AUTHOR_ID = 999999

def migrateCollection(col_path, dry=True):
    """Convert current module at given path into material inside VPR"""
    
    global vpr_persons
    out("Migrating: " + col_path)

    if path.exists(col_path):

        col_xml = getCollectionXML(col_path)

        # extract the correct module id
        collection_id = col_path.split('/')[-1]
        collection_id = collection_id.split('.')[0]

        # extract the module information
        persons, roles = getAuthorInfo(col_xml)
        metadata = getMetadata(col_xml)

        # add persons into VPR
        author_ids = []
        authors = roles.get('author', ['unknown'])
        for author_uid in authors:
            # check for existence first
            if vpr_persons.has_key(author_uid):
                author_id = vpr_persons[author_uid]['id']
            else:
                # post the new person into VPR
                p_info = {}
                p_info['user_id'] = author_uid
                try:
                    p_info['fullname'] = persons[author_uid]['fullname'][0] or ''
                    p_info['email'] = persons[author_uid]['email'][0] or ''
                except:
                    p_info['fullname'] = author_uid 
                    p_info['email'] = ''
                res = rq.post(VPR_URL + '/persons/', data=p_info)
                if res.status_code == 201:
                    per_dict = eval(res.content.replace('null', 'None'))
                    author_id = per_dict['id']
                    # add back to the global list
                    vpr_persons[author_uid] = per_dict
                else:
                    out('Error adding author for ' + collection_id)
                    author_id = NO_AUTHOR_ID
            author_ids.append(author_id)

        # getting categories
        cat_ids = prepareCategory(metadata['subject'], )

        # prepate material content
        col_text = genCollectionContent(col_xml)
        m_info = {
            'material_type': 2,
            'title': metadata['title'],
            'text': col_text,
            'version': 1, 
            'description': metadata['abstract'] or '-',
            'language': metadata.get('language', 'na'),
            'author': author_ids,
            'editor': author_id,
            'categories': cat_ids,
            'keywords': '\n'.join(metadata['keyword']),
            'original_id': ORIGINAL_PREFIX + collection_id,
            }

        m_info['export_later'] = 1

        # post to the site
        if not dry:
            res = rq.post(VPR_URL+'/materials/', data=m_info)
            if res.status_code == 201:
                toResume(collection_id)
            out('%s: %d' % (col_path, res.status_code))
        else:
            res = m_info 
        
        return res


def migrateAllCollections(root_path, dry=True, resume=False):
    """Do the migrate to all collections found inside path"""
    col_list = listdir(root_path)
     
    # prepare the resume list
    done_list = []
    try:
        rf = open(RESUME_FILE, 'r')
        if resume:
            done_list = rf.read()
            done_list = done_list.split('\n')
            rf.close()
        else:
            os.remove(os.path.realpath(rf.filename))    
    except:
        out('Error with resume file')
        

    nok_file = open(FAILED_FILE, 'w')
    m_count = 1
    m_total = len(col_list)

    try:
        for col in col_list:
            if col not in done_list:
                try:
                    res = migrateCollection(path.join(root_path, col), dry=dry)
                    if res.status_code == 201:
                        print '[%d/%d] OK\n' % (m_count, m_total) 
                    else:
                        nok_file.write('%d\t%s\n' % (res.status_code, col))
                        print '[%d/%d] %d - %s\n' % (m_count, m_total, res.status_code, col) 
                except:
                    nok_file.write('ERR\t%s\n' % col)
                    print '[%d/%d] ERR - %s\n' % (m_count, m_total, col) 
            else:
                out('Bypassing: ' + col)
            m_count += 1
    except:
        pass
    finally:
        nok_file.close()

from xml.dom import minidom

def parseContentNode(node):
    """Return correspondent dict to content node"""

    if node.nodeName == '#text':
        return None
    res = {}
    # subcollection / section
    if node.nodeName == 'col:subcollection':
        res['type'] = 'subcollection'
        node_title = node.getElementsByTagName('md:title')[0]
        res['title'] = node_title.childNodes[0].nodeValue
        node_content = node.getElementsByTagName('col:content')[0] 
        res['content'] = parseContentNode(node_content)
    # module list
    elif node.nodeName == 'col:content':
        res = []
        for child in node.childNodes:
            cres = parseContentNode(child)
            if cres is not None:
                res.append(cres)
    # module
    elif node.nodeName == 'col:module':
      try:
        res['type'] = 'module'
        res['id'] = vpr_idmap[ORIGINAL_PREFIX + node.getAttribute('document')]
        node_title = node.getElementsByTagName('md:title')[0]
        res['title'] = node_title.childNodes[0].nodeValue
        res['version'] = 1
      except:
        import pdb;pdb.set_trace()

    return res
                

def genCollectionContent(xml):
    """Convert from CNXML collection structure to JSON"""
    xml = xml.replace('\n', '')
    root = minidom.parseString(xml)
    dom_content = root.getElementsByTagName('col:content')[0]
    col_dict = {'content':parseContentNode(dom_content)}

    return json.dumps(col_dict)
     

# ./manage.py shell
def exportOriginalIDs():
    from django.db import connection
    cur = connection.cursor()
    cur.execute('select original_id, material_id from vpr_content_originalid;')
    records = cur.fetchall()
    all_ids = {}
    for rec in records:
        old_id = rec[0].split('_')[0]
        all_ids[old_id] = rec[1]

    print 'Export ID mapper to file idmapper.json'
    id_file = open('idmapper.json', 'w')
    id_file.write(json.dumps(all_ids))
    id_file.close()

    return all_ids 


def importIDMapper():
    """Loads all IDs from file and put into global var"""
    try:
        out('Import all ID mappers')
        mf = open('idmapper.json')
        all_ids = json.loads(mf.read())
        mf.close()
        return all_ids
    except:
        print 'Error when importing ID mapper'


def prepareCategory(categories):
    """Return the category ID of every category in list. Creating new in
    case of not existed"""

    global vpr_categories

    cat_ids = []
    for cat in categories:
        norm_cat = cat.lower().strip()
        if vpr_categories.has_key(norm_cat):
            cat_id = vpr_categories[norm_cat]['id']
        else:
            # create new category
            out('Create new category: ' + cat.strip())
            data = {'name': cat.strip(),
                    'description':''}
            res = rq.post(VPR_URL+'/categories/', data=data)
            res = eval(res.content.replace('null', 'None'))
            cat_id = res['id']

            # add back to the global list
            vpr_categories[norm_cat] = res

        cat_ids.append(cat_id)

    return cat_ids


# ./manage.py shell
def correctPersonRecords():
    """Correct person records with spaces in user ID"""

    global vpr_persons

    out('Get list of incorrect person IDs')
    fault_ids = [pid for pid in vpr_persons.keys() if pid.find(' ') > 0]

    out('Determine which is really missing')
    really_missing = []
    for ids  in fault_ids:
        for pid in ids.strip().split(' '):
            if not vpr_persons.has_key(pid) and pid.strip() != '':
                really_missing.append(pid)
    
    out('Add the missing persons (if needed)')
    for pid in really_missing:
        p_info = {
            'user_id': pid,
            'fullname': pid,
            'email': '',
            }
        res = rq.post(VPR_URL + '/persons/', data=p_info)
        if res.status_code != 201:
            out('Error when adding person: ' + pid)
            raise 

    out('Reload the person list')
    vpr_persons = getAllPersons()

    out('Mapping the old and new IDs')
    idmaps = []
    for fid in fault_ids:
        current_id = vpr_persons[fid]['id']
        new_ids = []
        for pid in fid.strip().split(' '):
            new_ids.append(vpr_persons[pid]['id'])
        idmaps.append((current_id, new_ids))

    out('Update on database')
    from vpr_content.models import MaterialPerson, Person
    for idmap in idmaps:
        out(str(idmap))
        mps = MaterialPerson.objects.filter(person_id=idmap[0])
        for mp in mps:
            material_rid = mp.material_rid
            role = mp.role
            for neo_pid in idmap[1]:
                neo_mp = MaterialPerson(
                    material_rid = material_rid,
                    role = role,
                    person_id = neo_pid,
                    )
                neo_mp.save()
            mp.delete()
        # delete the person record
        Person.objects.get(id=idmap[0]).delete()

    return None 
        

RAW_COLLECTION_IDS = """
"""

# MUST RUN FIRST
if __name__ == '__main__':
    try:
        try:
            os.remove(LOG_FILE)
        except:
            pass
        vpr_idmap = importIDMapper()
        try:
            vpr_persons = shell_getAllPersons()
        except:
            vpr_persons = getAllPersons()
        vpr_categories = getAllCategories()
    except:
        raise
        print 'Error when initializing'
