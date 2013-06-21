from os import path, listdir
from subprocess import call

import libxml2
import libxslt
import re
import request

#from vpr_content import models

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
            print '>> ' + target_path
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


def getTagContent(tag, content):
    """Returns data between given tag inside content text"""
    rtag = buildRegex(tag)
    return rtag.findall(content)


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
    for info in info_need:
        metadata[info] = getTagContent('md:'+info)


VPR_URL = 'http://dev.voer.edu.vn/1/'

def migrateModule(module_path):
    """Convert current module at given path into material inside VPR"""

    cnxml_path = os.path.join(module_path, 'index.cnxml')
    if os.path.exists(cnxml_path):
        # extract the module information
        with open(cnxml_path, 'r') as f0:
            cnxml = f0.read()
            persons, roles = getAuthorInfo(cnxml)
            metadata = getMetadata(cnxml)

        # convert module into html and load the content
        convert2HTML(module_path)
        with open(os.path.join(module_path, 'index.html')) as f1:
            html = f1.read()

        # load all the files
        module_files = os.listdir(module_path)
        module_files.remove('index.html')
        module_files.remove('index.cnxml')

        # add persons into VPR
        roles['author']

        # add material into VPR
        m_info = {
            'material_type': 1,
            'title': metadata['title'],
            'text': html,
            'version': 1, 
            'description': metadata['abstract'],
            'language': metadata['language'],
            }
        



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
