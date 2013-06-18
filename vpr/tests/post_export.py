import requests

export_url = 'http://dev.voer.edu.vn:6543/export'
zf = open('material-0.zip', 'rb')
files = {'file': ('material-0.zip', zf.read())}
res = requests.post(export_url, files=files, data={})
print res.status_code
