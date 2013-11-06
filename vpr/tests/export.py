import requests
import json

CONCURRENT = 10

url = 'http://dev.voer.vn:6543/export'
path = './export/sample00.zip'
zip_file = open(path, 'rb')

files = {'file': ('sample00.zip', zip_file.read())}
zip_file.close()
task_ids = []

for ci in range(CONCURRENT): 
    try:
        res = requests.post(url, files=files, data={})
        #import pdb;pdb.set_trace()
        values = json.loads(res.content)
        print '[%d] >> %d - Task ID: %s' % (ci, res.status_code, values['task_id'])
    except:
        #import pdb;pdb.set_trace()
        print res.status_code, res.content

