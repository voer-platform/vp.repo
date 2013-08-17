import requests
import zipfile
import re
import json
import requests as rq
import os

from os import path, listdir
from migrate import getTagContent, getAuthorInfo, buildRegex, getMetadata
from migrate import getAllPersons, getAllCategories, out, prepareCategory, toResume
from migrate import VPR_URL, LOG_FILE, FAILED_FILE, RESUME_FILE

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
    elif col_path.endswith('.cnxml'):
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
                    p_info['fullname'] = 'unknown'
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
        cat_ids = prepareCategory(metadata['subject'])

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
            'original_id': collection_id,
            }

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
        res['type'] = 'module'
        res['id'] = vpr_idmap[node.getAttribute('document')]
        node_title = node.getElementsByTagName('md:title')[0]
        res['title'] = node_title.childNodes[0].nodeValue

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


RAW_COLLECTION_IDS = """
col10001
col10002
col10003
col10004
col10005
col10006
col10007
col10008
col10009
col10010
col10011
col10012
col10013
col10014
col10015
col10016
col10017
col10018
col10019
col10020
col10021
col10022
col10023
col10024
col10025
col10026
col10027
col10028
col10029
col10030
col10031
col10032
col10033
col10034
col10035
col10036
col10037
col10038
col10039
col10040
col10041
col10042
col10043
col10044
col10045
col10046
col10047
col10048
col10049
col10050
col10051
col10052
col10053
col10054
col10055
col10056
col10057
col10058
col10059
col10060
col10061
col10062
col10063
col10064
col10065
col10066
col10067
col10068
col10069
col10070
col10071
col10072
col10073
col10074
col10075
col10076
col10077
col10078
col10079
col10080
col10081
col10082
col10083
col10084
col10085
col10086
col10087
col10088
col10089
col10090
col10091
col10092
col10093
col10094
col10095
col10096
col10097
col10098
col10099
col10100
col10101
col10102
col10103
col10104
col10105
col10106
col10107
col10108
col10109
col10110
col10111
col10112
col10113
col10114
col10115
col10116
col10117
col10118
col10119
col10120
col10121
col10122
col10123
col10124
col10125
col10126
col10127
col10128
col10129
col10130
col10131
col10132
col10133
col10134
col10135
col10136
col10137
col10138
col10139
col10140
col10141
col10142
col10143
col10144
col10145
col10146
col10147
col10148
col10149
col10150
col10151
col10152
col10153
col10154
col10155
col10156
col10157
col10158
col10159
col10160
col10161
col10162
col10163
col10164
col10165
col10166
col10167
col10168
col10169
col10170
col10171
col10172
col10173
col10174
col10175
col10176
col10177
col10178
col10179
col10180
col10181
col10182
col10183
col10184
col10185
col10186
col10187
col10188
col10189
col10190
col10191
col10192
col10193
col10194
col10195
col10196
col10197
col10198
col10199
col10200
col10201
col10202
col10203
col10204
col10205
col10206
col10207
col10208
col10209
col10210
col10211
col10212
col10213
col10214
col10215
col10216
col10217
col10218
col10219
col10220
col10221
col10222
col10223
col10224
col10225
col10226
col10227
col10228
col10229
col10230
col10231
col10232
col10233
col10234
col10235
col10236
col10237
col10238
col10239
col10240
col10241
col10242
col10243
col10244
col10245
col10246
col10247
col10248
col10249
col10250
col10251
col10252
col10253
col10254
col10255
col10256
col10257
col10258
col10259
col10260
col10261
col10262
col10263
col10264
col10265
col10266
col10267
col10268
col10269
col10270
col10271
col10272
col10273
col10274
col10275
"""

# MUST RUN FIRST
if __name__ == '__main__':
    try:
        os.remove(LOG_FILE)
        vpr_idmap = importIDMapper()
        vpr_persons = getAllPersons()
        vpr_categories = getAllCategories()
    except:
        raise
        print 'Error when initializing'
