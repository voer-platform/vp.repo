from os import path, listdir
from subprocess import call

import libxml2
import libxslt
import re
import requests as rq


#VPR_URL = 'http://vpr.net/1'
VPR_URL = 'http://localhost:8000/1'


def convert2HTML(module_path):
    """Converts the module from CNXML to HTML5, using path to the 
       module as parameter"""
    # check for validity first 
    if path.exists(module_path):
        try:
            index_path = path.join(module_path, 'index.cnxml')
            target_path = path.join(module_path, 'index.html')
            code = call('xsltproc cnxml2html.xsl '+index_path+' > '+target_path, shell=True, stdout=None)
            if code != 0: 
                raise
            print '>> Converted CNXML to ' + target_path
        except:
            print "Error: Something wrong with module: " + module_path


def convertAllModules(root_path):
    """Converts all sub-directories found inside the current directory"""
    # convert all cnxml to html first
    module_list = listdir(root_path)
    mcount = 0
    for module in module_list:
        if path.isdir(module):
            convert2HTML(module)
            mcount += 1
    print "%d module(s) converted" % mcount

    
def buildRegex(tag, template=''):
    """Returns the compiled regex from given tag name"""
    RTAG = template or '(?<=<%(tag)s>).*?(?=</%(tag)s>)'
    rg = re.compile(RTAG % {'tag':tag})
    return rg


def getTagContent(tag, content, default=''):
    """Returns data between given tag inside content text"""
    rtag = buildRegex(tag)
    res = rtag.findall(content)
    if not res:
        res = default
    return res


def getAuthorInfo(cnxml):
    """Get all information about actors and roles"""
    # firstly, collect all roles with nicknames
    RTAG1 = '(?<=<%(tag)s type=").*?(?=</%(tag)s>)'
    rtag = buildRegex('md:role', RTAG1)
    res = rtag.findall(cnxml)
    roles = {}
    for item in res:
        key, value = item.split('">')
        if not roles.has_key(key):
            roles[key] = []
        roles[key].append(value)

    # extract the person info
    cnxml = cnxml.replace('\n', '')
    rg_person = re.compile('(?<=<md:person userid=").*?(?=\s*</md:person>)')
    person_tags = rg_person.findall(cnxml)
    persons = {}
    for ptag in person_tags:
        pid = ptag.split('">')[0]
        person_info = {}
        person_info['firstname'] = getTagContent('md:firstname', ptag)
        person_info['surname'] = getTagContent('md:surname', ptag)
        person_info['fullname'] = getTagContent('md:fullname', ptag)
        person_info['email'] = getTagContent('md:email', ptag)
        persons[pid] = person_info

    return persons, roles


def getMetadata(cnxml):
    """Extract metadata from the cnxml content"""
    metadata = {}
    info_needed = ('title', 'version', 'created', 'keyword', 
                   'subject', 'abstract', 'language', 
                   'repository')
    for info in info_needed:
        metadata[info] = getTagContent('md:'+info, cnxml)

    # ensure having no empty fields

    if not metadata['abstract'] or metadata['abstract'][0] == '':
        metadata['abstract'] = '-'
    
    if not metadata['title']:
        metadata['title'] = getTagContent('title', cnxml, ['Untitled'])
    metadata['title'] = metadata['title'][0]

    if not metadata['language']:
        metadata['language'] = ['-']

    return metadata



def prepareCategory(categories):
    """Return the category ID of every category in list. Creating new in
    case of not existed"""
    # get list of category first
    res = requests.get(VPR_URL+'/categories/')
    res = eval(res.content.replace('null', 'None'))
    cat_names = [cat['name'].lower().strip() for cat in res]

    cat_ids = []
    for cat in categories:
        norm_cat = cat.lower().strip()
        if norm_cat in cat_names:
            cat_id = res[cat_names.index(norm_cat)]['id']
        else:
            # create new category
            data = {'name': cat.strip(),
                    'description':''}
            res = requests.post(VPR_URL+'/categories/', data=data)
            res = eval(res.replace('null', 'None'))
            cat_id = res['id']
        cat_ids.append(cat_id)

    return cat_ids


def migrateModule(module_path):
    """Convert current module at given path into material inside VPR"""
    
    cnxml_path = path.join(module_path, 'index.cnxml')
    if path.exists(cnxml_path):
        # extract the module information
        with open(cnxml_path, 'r') as f0:
            cnxml = f0.read()
            persons, roles = getAuthorInfo(cnxml)
            metadata = getMetadata(cnxml)

        # convert module into html and load the content
        convert2HTML(module_path)
        with open(path.join(module_path, 'index.html')) as f1:
            html = f1.read()

        # load all the files
        module_files = listdir(module_path)
        module_files.remove('index.html')
        module_files.remove('index.cnxml')

        # add persons into VPR
        author_ids = []
        authors = roles.get('author', ['unknown'])
        for author_uid in authors:
            p_info = {}
            p_info['user_id'] = author_uid
            try:
                p_info['fullname'] = persons[author_uid]['fullname'][0] or ''
                p_info['email'] = persons[author_uid]['email'][0] or ''
            except:
                p_info['fullname'] = 'unknown'
                p_info['email'] = ''
            res = requests.post(VPR_URL + '/persons/', data=p_info)
            if res.status_code == 201:
                per_dict = eval(res.content.replace('null', 'None'))
                author_id = per_dict['id']
            else:
                author_id = 999999
            author_ids.append(author_id)

        # getting categories
        cat_ids = prepareCategory(metadata['subject'])

        # add material into VPR
        m_info = {
            'material_type': 1,
            'title': metadata['title'],
            'text': html,
            'version': 1, 
            'description': metadata['abstract'] or '-',
            'language': metadata.get('language', 'na'),
            'authors': author_ids,
            'editor_id': author_id,
            'categories': cat_ids,
            'keywords': '\n'.join(metadata['keyword']),
            }
        mfiles = {}
        for mfid in module_files:
            mf = open(path.join(module_path, mfid), 'r')
            mfiles['f'+str(len(mfiles))] = (mfid, mf.read())
            mf.close()

        # post to the site
        res = requests.post(VPR_URL+'/materials/', files=mfiles, data=m_info)

        print res.status_code


def migrateAllModules(root_path):
    """Do the migrate to all modules found inside path"""
    module_list = listdir(root_path)
    for module in module_list:
        if path.isdir(path.join(root_path,module)):
            print "\nMIGRATING " + module
            migrateModule(path.join(root_path,module))
            print "\nMIGRATING " + module + "... DONE"



def out2File(file_name, content):
    """Export the content into file"""
    f0 = open(file_name, 'w')
    f0.write(content)
    f0.close()


def normalizeResponse(response):
    """Correct the text reponse and convert it to appropriate type"""
    response = response.content.replace('null', 'None')
    return eval(response)


def out(text):
    """Just print to screen"""
    print '\n>> %s\n' % text


def getAllPersons():
    """Browse every page of the ../persons/ and extract all person info"""

    out('Start downloading all person data')
    persons = {}
    res = rq.get(VPR_URL + '/persons/')    
    res = normalizeResponse(res)

    # add the first page into list
    for item in res['results']:
        if not persons.has_key(item['user_id']):
            persons[item['user_id']] = item

    while res['next'] != None:
        out('Downloading next person page...')
        res = rq.get(res['next'])    
        res = normalizeResponse(res)
        # add the current page into list
        for item in res['results']:
            if not persons.has_key(item['user_id']):
                persons[item['user_id']] = item
    
    out('DONE: Download person data')
    return persons



# MUST RUN FIRST
vpr_persons = getAllPersons()


"""
doc0 = libxml2.parseFile('cnxml-to-html5.xsl')
style = libxslt.parseStylesheetDoc(doc0)

doc1 = libxml2.parseFile('index.cnxml')
result = style.applyStylesheet(doc1, None)

style.saveResultToFilename('test-result', result, 0)
style.freeStylesheet()

doc1.freeDoc()
result.freeDoc()
"""
