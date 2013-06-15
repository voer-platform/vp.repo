from django.test.client import Client
client = Client()

i0 = 'tests/test.png'
image = open(i0, 'r')
f01 = open(i0, 'r')
f02 = open(i0, 'r')

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
mdata['mf01'] = f01
mdata['mf02'] = f02
mdata['mf01_name'] = 'Hello this is the first file'
mdata['mf02_name'] = 'And this is the second file'
res = client.post('/1/materials/', mdata)
res.status_code

image.close()
f01.close()
f02.close()


print res

