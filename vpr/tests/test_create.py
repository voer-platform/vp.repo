from django.test.client import Client

client = Client()

def createMaterial(title='Sample Module Title'):
    i0 = 'tests/test.png'
    image = open(i0, 'r')
    f01 = open(i0, 'r')
    f02 = open(i0, 'r')
    mdata = {}
    mdata['material_type'] = 1
    mdata['title'] = title
    mdata['text'] = 'Nothing in this body'
    mdata['version'] = 1
    mdata['description'] = 'Just a quick intro of this material'
    mdata['categories'] = [1]
    mdata['author'] = '1, 2'
    mdata['editor'] = 1
    mdata['translator'] = 1
    mdata['contributor'] = 1
    mdata['licensor'] = 1
    mdata['license_id'] = 1
    mdata['language'] = 1
    mdata['image'] = image 
    mdata['mf01'] = f01
    mdata['mf02'] = f02
    mdata['mf01_name'] = 'Hello this is the first file'
    mdata['mf02_name'] = 'And this is the second file'
    mdata['export-now'] = 1 
    res = client.post('/1/materials/', mdata)
    res.status_code
    image.close()
    f01.close()
    f02.close()

    return res


COLLECTION_ITEM = """{"attr":{"id":"%s","version": %d,"rel" : "default"},
                      "data" : "%s",
                      "state" : ""
                      }"""


def createCollection(title='Sample Collection Title'):
    collection_dict = {'id': 'some_id',
                       'title': title
                      }
    collection_content = []
    # create sample modules first
    for i in range(2):
        res = createMaterial('Sample collection module '+str(i+1))
        res = eval(res.content.replace('null', 'None'))
        collection_content.append(
            {'type': 'module',
             'id': res['material_id'],
             'title': res['title']
            })
    collection_dict['content'] = collection_content
    i0 = 'tests/test.png'
    image = open(i0, 'r')
    mdata = {}
    mdata['material_type'] = 2
    mdata['title'] = title
    mdata['text'] = str(collection_dict)
    mdata['version'] = 1
    mdata['description'] = 'Just a quick intro of this material'
    mdata['categories'] = [1]
    mdata['authors'] = 1
    mdata['editor_id'] = 1
    mdata['license_id'] = 1
    mdata['language'] = 1
    mdata['image'] = image 
    res = client.post('/1/materials/', mdata)
    res.status_code
    image.close()

    return res

def createPerson(fullname='Person Name'):
    i0 = 'tests/test.png'
    image = open(i0, 'r')
    mdata = {}
    mdata['fullname'] = fullname
    mdata['first_name'] = 'First name'
    mdata['last_name'] = 'Last name'
    mdata['email'] = 'e@mail.com'
    mdata['title'] = 'Mr'
    mdata['homepage'] = 'google.com'
    mdata['affiliation'] = 'none'
    mdata['affiliation_url'] = 'none_url'
    mdata['national'] = 'vietnam' 
    mdata['avatar'] = image 
    mdata['biography'] = 'Hello this is the bio'
    mdata['client_id'] = 1 
    mdata['user_id'] = 'jamesbond' 
    res = client.post('/1/persons/', mdata)
    res.status_code
    image.close()

    return res

def checkinMaterial():
    #res = createMaterial() 
    #material_id = eval(res.content.replace('null', 'None'))['material_id']
    #url = '/1/materials/' + material_id + '/'
    url = '/1/materials/b1ba92fe/'

    i0 = 'tests/test.png'
    image = open(i0, 'r')
    f01 = open(i0, 'r')
    f02 = open(i0, 'r')
    mdata = {}
    mdata['material_type'] = 1
    mdata['title'] = 'Checkin Material'
    mdata['text'] = 'Nothing in this body'
    mdata['version'] = 1
    mdata['description'] = 'Just a quick intro of this material'
    mdata['categories'] = [1]
    mdata['author'] = '1, 2'
    mdata['editor'] = 1
    mdata['translator'] = 1
    mdata['contributor'] = 1
    mdata['licensor'] = 1
    mdata['license_id'] = 1
    mdata['language'] = 1
    mdata['image'] = image 
    mdata['mf01'] = f01
    mdata['mf02'] = f02
    mdata['mf01_name'] = 'Hello this is the first file'
    mdata['mf02_name'] = 'And this is the second file'
    mdata['export-now'] = 1 
    res = client.put(url, mdata)
    res.status_code
    image.close()
    f01.close()
    f02.close()

    return res
