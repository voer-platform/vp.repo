"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from vpr_api.models import APIClient
from models import Category


VPR_LOCAL = 'http://127.0.0.1:8000'

class PersonTestCase(TestCase):

    sample_dict = {
        'fullname' : 'Barrack Obama',
        'biography' : 're-elected US president',
        'first_name' : 'Barrack',
        'last_name' : 'Obama',
        'email' : 'president@us.com',
        'title' : 'Mr',
        'homepage' : 'us.com',
        'affiliation' : 'Nothing',
        'affiliation_url' : 'nothing.com',
        'national' : 'US',
        'client_id' : 1,
        'user_id' : 'barracko',
        }

    def setUp(self):
        # call the function
        pass

    def test_create_success(self):
        res = self.client.post('/1/persons/', self.sample_dict)
        self.assertEqual(res.status_code, 201)
        content = eval(res.content.replace('null', 'None'))
        for k in self.sample_dict:
            self.assertEqual(self.sample_dict[k], content[k])

    def test_create_missing(self):
        miss_dict = self.sample_dict.copy()
        miss_dict['user_id'] = ''
        res = self.client.post('/1/persons/', miss_dict)
        content = eval(res.content.replace('null', 'None'))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(content['user_id'], ["This field is required."])

    def test_list(self):
        self.client.post('/1/persons/', self.sample_dict)
        self.client.post('/1/persons/', self.sample_dict)
        res = self.client.get('/1/persons/')
        content = eval(res.content.replace('null', 'None'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['count'], 2)

    def test_update(self):
        self.client.post('/1/persons/', self.sample_dict)
        update_dict = self.sample_dict.copy()
        update_dict['fullname'] = 'Osama'
        res = self.client.put('/1/persons/1/', update_dict)
        content = eval(res.content.replace('null', 'None'))
        self.assertEqual(res.status_code, 201)
        for k in update_dict:
            self.assertEqual(update_dict[k], content[k])


class ModuleTestCase(TestCase):
    """docstring for ModuleTestCase"""

    def setUp(self):
        client = createAPIClient('John Service', 'johnser')
        self.meta_params = {
            'title':'Sample module',
            'description':'Module description here',
            #'categories':createCategory(1)[0],
            #'authors':[createAuthor('John Lennon', 'john_lennon', 'Singer')],
            'keywords':'hello, there, fine',
            'editor':createEditor('editor_one', client)
            }
        self.meta = Metadata.objects.create(**self.meta_params)
        
        self.module_params = {
            'text': 'This is the content',
            'metadata': self.meta,
            'attachment': None,
            'client_id': ''
            }
        self.module = createModule(**self.module_params) 
        
    def testCreate(self):
        print self.module
        self.assertNotEqual(self.module, None)
        #self.assertEqual(self.module.text, 'This is the content')
        #self.assertEqual(self.module.metadata, self.meta)
        #self.assertEqual(self.module.attachment, None)
