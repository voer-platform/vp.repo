from django.test.client import Client

client = Client()

def ct1(title='Sample Module Title'):
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
    mdata['authors'] = 1
    mdata['editor_id'] = 1
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

def ct2(title='Sample Collection Title'):
    collection_text = '[' 
    # create sample modules first
    for i in range(2):
        res = ct1('Sample collection module '+str(i+1))
        res = eval(res.content.replace('null', 'None'))
        node_text = COLLECTION_ITEM % (res['material_id'],
                                       res['version'],
                                       res['title'])
        collection_text += node_text + ','
    collection_text += ']'

    i0 = 'tests/test.png'
    image = open(i0, 'r')
    mdata = {}
    mdata['material_type'] = 2
    mdata['title'] = title
    mdata['text'] = collection_text
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

