from django.test.client import Client
client = Client()

image = open('test-image.png', 'r')

mdata = {}
mdata['material_type'] = 1
mdata['title'] = 'Nothing left'
mdata['text'] = 'Nothing in this body'
mdata['version'] = 1
mdata['description'] = 'Just a quick intro of this material'
mdata['categories'] = [1]
mdata['authors'] = 1
mdata['editor_id'] = 1
mdata['license_id'] = 1
mdata['language'] = 1
mdata['image'] = image
mdata['mf01'] = image
mdata['mf02'] = image
mdata['mf01_name'] = 'Hello this is the first file'
mdata['mf02_name'] = 'And this is the second file'
res = client.post('/1/materials/', mdata)
res.status_code

print res

