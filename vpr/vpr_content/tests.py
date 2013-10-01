"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from vpr_api.models import APIClient
from models import Category
from datetime import datetime
from django.conf import settings

import time

VPR_LOCAL = 'http://127.0.0.1:8000'

CODE_DELETED = 204
CODE_SUCCESS = 200
CODE_CREATED = 201
CODE_NOT_FOUND = 404
CODE_BAD_REQUEST = 400


def normRes(res):
    return eval(res.content.replace('null', 'None'))


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
    res0 = None

    def setUp(self):
        self.res0 = self.client.post('/1/persons/', self.sample_dict)

    def test_create_success(self):
        self.assertEqual(self.res0.status_code, CODE_CREATED)
        for k in self.sample_dict:
            self.assertEqual(self.sample_dict[k], normRes(self.res0)[k])

    def test_create_with_avatar(self):
        img = open('tests/test.png','rb')
        new_person = self.sample_dict.copy()
        new_person['avatar'] = img
        res = self.client.post('/1/persons/', new_person)
        self.assertEqual(res.status_code, CODE_CREATED)
        content = normRes(res)
        pid = content['id']
        for k in self.sample_dict:
            self.assertEqual(new_person[k], content[k])
        self.assertNotEqual(content['avatar'], '')
        res = self.client.get('/1/persons/%d/avatar/' % pid)
        self.assertEqual(res.status_code, 200)

    def test_create_missing(self):
        miss_dict = self.sample_dict.copy()
        miss_dict['user_id'] = ''
        res = self.client.post('/1/persons/', miss_dict)
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_BAD_REQUEST)
        self.assertEqual(content['user_id'], ["This field is required."])

    def test_get_detail(self):
        pid = normRes(self.res0)['id']
        res = self.client.get('/1/persons/%d/' % pid)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        for k in self.sample_dict:
            self.assertEqual(self.sample_dict[k], normRes(res)[k])

    def test_get_count(self):
        pid = normRes(self.res0)['id']
        res = self.client.get('/1/persons/%d/?count=1' % pid)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        content = normRes(res)
        for role in settings.VPR_MATERIAL_ROLES:
            self.assertEqual(content[role], 0)

    def test_list(self):
        self.client.post('/1/persons/', self.sample_dict)
        res = self.client.get('/1/persons/')
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        self.assertEqual(content['count'], 2)

    def test_update(self):
        content = normRes(self.res0)
        pid = str(content['id'])
        update_dict = self.sample_dict.copy()
        update_dict['fullname'] = 'Osama'
        res = self.client.put('/1/persons/%s/' % pid, update_dict)
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        for k in update_dict:
            self.assertEqual(update_dict[k], content[k])

    def test_delete(self):
        content = normRes(self.res0)
        pid = str(content['id'])
        self.client.post('/1/persons/', self.sample_dict)
        res = self.client.delete('/1/persons/%s/' % pid)
        self.assertEqual(res.status_code, CODE_DELETED)
        content = normRes(self.client.get('/1/persons/'))
        self.assertEqual(content['count'], 1)


class CategoryTestCase(TestCase): 
    sample_dict = {
        'name' : 'First Category',
        'parent' : 0,
        'description' : 'This is only the first description',
        }
    res0 = None

    def setUp(self):
        self.res0 = self.client.post('/1/categories/', self.sample_dict)

    def test_create_success(self):
        self.assertEqual(self.res0.status_code, CODE_CREATED)
        for k in self.sample_dict:
            self.assertEqual(self.sample_dict[k], normRes(self.res0)[k])

    def test_create_missing(self):
        miss_dict = self.sample_dict.copy()
        miss_dict['name'] = ''
        res = self.client.post('/1/categories/', miss_dict)
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_BAD_REQUEST)
        self.assertEqual(content['name'], ["This field is required."])

    def test_get_count(self):
        # tested in the MaterialTestCase
        pass

    def test_list(self):
        self.client.post('/1/categories/', self.sample_dict)
        res = self.client.get('/1/categories/')
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        self.assertEqual(len(content), 2)

    def test_update(self):
        content = normRes(self.res0)
        pid = str(content['id'])
        update_dict = self.sample_dict.copy()
        update_dict['name'] = 'Osama Category'
        update_dict['description'] = 'Nothing new'
        res = self.client.put('/1/categories/%s/' % pid, update_dict)
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        for k in update_dict:
            self.assertEqual(update_dict[k], content[k])

    def test_delete(self):
        content = normRes(self.res0)
        pid = str(content['id'])
        self.client.post('/1/categories/', self.sample_dict)
        res = self.client.delete('/1/categories/%s/' % pid)
        self.assertEqual(res.status_code, CODE_DELETED)
        content = normRes(self.client.get('/1/categories/'))
        self.assertEqual(len(content), 1)


class MaterialTestCase(TestCase):
    sample_material = {
        'material_type' : 1,  
        'text' : 'Lorem ipsum here',
        'version' : 1,
        'title' : 'This is sample material',
        'description' : 'Sample description',
        'categories' : '1',
        'author': '1',
        'editor': '1',
        'contributor': '1',
        'licensor': '1',
        'maintainer': '1',
        'translator': '1',
        'keywords' : 'sample\nmaterial\nmodule',
        'language' : 'en',
        'license_id' : 0,
        'modified' : None,
        'derived_from' : '',
        'export-later': 1,
        }
    sample_cat = {
        'name' : 'First Category',
        'parent' : 0,
        'description' : 'This is only the first description',
        }
    sample_person = {
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
    pid0 = None
    cid0 = None
    res0 = None
    content0 = None


    def compareRes(self, base, res):
        for k in base:
            if k == 'export-later':
                continue
            try:
                self.assertEqual(base[k], res[k])    
            except AssertionError:
                if k == 'modified':
                    today = datetime.utcnow().strftime('%Y-%m-%d')
                    self.assertEqual(
                        res['modified'][:10], 
                        today)
                else:
                    raise

    def setUp(self):
        res = self.client.post('/1/persons/', self.sample_person)
        self.pid0 = normRes(res)['id']
        res = self.client.post('/1/categories/', self.sample_cat)
        self.cid0 = normRes(res)['id']
        self.sample_material['categories'] = str(self.cid0)
        self.res0 = self.client.post('/1/materials/', self.sample_material)
        self.content0 = normRes(self.res0)

    def test_create_success(self):
        self.assertEqual(self.res0.status_code, CODE_CREATED)
        self.compareRes(self.sample_material, self.content0)

    def test_create_with_image(self):
        new_material = self.sample_material.copy()
        mimg = open('tests/test.png','rb')
        new_material['image'] = mimg
        res = self.client.post('/1/materials/', new_material)
        content = normRes(res)
        self.assertNotEqual(content['image'], '')
        material_id = content['material_id']
        res = self.client.get('/1/materials/%s/image/' % material_id)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        self.assertNotEqual(res.content, '')
        
    def test_create_multi_persons(self):
        new_material = self.sample_material.copy()
        new_material['author'] = '1,2'
        new_material['editor'] = '1,2'
        new_material['licensor'] = '1,2'
        new_material['contributor'] = '1,2'
        new_material['maintainer'] = '1,2'
        new_material['translator'] = '1,2'
        res = self.client.post('/1/materials/', new_material)
        self.assertEqual(res.status_code, CODE_CREATED) 
        content = normRes(res)
        self.compareRes(new_material, content)

    def test_create_multi_cats(self):
        new_material = self.sample_material.copy()
        new_material['categories'] = '%s,99' % str(self.cid0)
        res = self.client.post('/1/materials/', new_material)
        self.assertEqual(res.status_code, CODE_CREATED) 
        content = normRes(res)
        self.compareRes(new_material, content)
        res = self.client.get('/1/categories/%s/?count=1' % self.cid0)
        content = normRes(res)
        self.assertEqual(content['material'], 2)
    
    def test_create_missing(self):
        miss_dict = self.sample_material.copy()
        miss_dict['title'] = ''
        res = self.client.post('/1/materials/', miss_dict)
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_BAD_REQUEST)
        self.assertEqual(content['title'], ["This field is required."])

    def test_get_version(self):
        self.assertEqual(self.res0.status_code, CODE_CREATED)
        res = self.client.get('/1/materials/%s/' % self.content0['material_id'])
        self.compareRes(self.sample_material, normRes(res))
        res = self.client.get('/1/materials/%s/1/' % self.content0['material_id'])
        self.compareRes(self.sample_material, normRes(res))

    def test_put(self):
        sm1 = self.sample_material.copy()
        sm1['text'] = 'This is the new update of this version'
        res = self.client.put('/1/materials/%s/' % self.content0['material_id'], sm1)
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_CREATED)
        sm1['version'] = 2
        self.compareRes(sm1, content)

    def test_get_all_vers(self):
        sm1 = self.sample_material.copy()
        self.client.put('/1/materials/%s/' % self.content0['material_id'], sm1)
        # get the latest version
        res = self.client.get('/1/materials/%s/' % self.content0['material_id'])
        sm1['version'] = 2
        self.compareRes(sm1, normRes(res))
        res = self.client.get('/1/materials/%s/all/' % self.content0['material_id'])
        self.assertEqual(normRes(res)['count'], 2)

    def test_list(self):
        self.client.post('/1/materials/', self.sample_material)
        res = self.client.get('/1/materials/')
        content = normRes(res)
        self.assertEqual(res.status_code, CODE_SUCCESS)
        self.assertEqual(content['count'], 2)

    def test_list_filter_person(self):
        sm1 = self.sample_material.copy()
        sm2 = self.sample_material.copy()
        for p in settings.VPR_MATERIAL_ROLES:
            sm1[p] = '2'
            sm2[p] = '1,3'
        res = self.client.post('/1/materials/', sm1)
        self.assertEqual(res.status_code, 201)
        res = self.client.post('/1/materials/', sm2)
        self.assertEqual(res.status_code, 201)
        res = self.client.get('/1/materials/?author=1')
        self.assertEqual(normRes(res)['count'], 2)
        res = self.client.get('/1/materials/?author=2')
        self.assertEqual(normRes(res)['count'], 1)

    def test_list_filter_category(self):
        sm1 = self.sample_material.copy()
        sm2 = self.sample_material.copy()
        sm1['categories'] = '99'
        sm2['categories'] = '%s,98' % self.cid0
        res = self.client.post('/1/materials/', sm1)
        self.assertEqual(res.status_code, CODE_CREATED)
        res = self.client.post('/1/materials/', sm2)
        self.assertEqual(res.status_code, CODE_CREATED)
        res = self.client.get('/1/materials/?categories=%s' % str(self.cid0))
        self.assertEqual(normRes(res)['count'], 2)
        res = self.client.get('/1/materials/?categories=99')
        self.assertEqual(normRes(res)['count'], 1)

    def test_list_filter_type(self):
        sm1 = self.sample_material.copy()
        sm2 = self.sample_material.copy()
        sm1['material_type'] = '2'
        sm2['material_type'] = '1'
        res = self.client.post('/1/materials/', sm1)
        self.assertEqual(res.status_code, 201)
        res = self.client.post('/1/materials/', sm2)
        self.assertEqual(res.status_code, 201)
        res = self.client.get('/1/materials/?material_type=1')
        self.assertEqual(normRes(res)['count'], 2)
        res = self.client.get('/1/materials/?material_type=2')
        self.assertEqual(normRes(res)['count'], 1)

    def test_list_order(self):
        sm1 = self.sample_material.copy()
        sm1['modified'] = None
        time.sleep(2)
        res = self.client.post('/1/materials/', sm1)
        self.assertEqual(res.status_code, CODE_CREATED)
        mid1 = normRes(res)['material_id']
        res = self.client.get('/1/materials/?sort_on=modified')
        content = normRes(res)
        self.assertEqual(
            content['results'][0]['material_id'], 
            self.content0['material_id'])
        self.assertEqual(
            content['results'][1]['material_id'], 
            mid1)
        res2 = self.client.get('/1/materials/?sort_on=-modified')
        content2 = normRes(res2)
        self.assertEqual(
            content2['results'][1]['material_id'], 
            self.content0['material_id'])
        self.assertEqual(
            content2['results'][0]['material_id'], 
            mid1)

    def test_delete_success(self):
        pass

    def test_get_similar(self):
        sm1 = self.sample_material.copy()
        sm2 = self.sample_material.copy()
        sm1['title'] = 'Similar One'
        sm1['keywords'] = 'material'
        sm2['title'] = 'Similar Me'
        sm2['keywords'] = 'nothing'
        sm3 = sm1.copy() 
        sm3['title'] = 'Similar Tee'
        sm3['keywords'] = 'so\nsample'
        res = self.client.post('/1/materials/', sm1)
        self.assertEqual(res.status_code, 201)
        res = self.client.post('/1/materials/', sm2)
        self.assertEqual(res.status_code, 201)
        res = self.client.post('/1/materials/', sm3)
        self.assertEqual(res.status_code, 201)
        res = self.client.get('/1/materials/%s/similar/' % self.content0['material_id'])
        self.assertEqual(len(normRes(res)), 2)

    def test_get_pdf(self):
        res = self.client.get('/1/materials/%s/pdf/' % self.content0['material_id'])
        while res.status_code == 102:
            print 'retry getting PDF file...'
            time.sleep(2)    
            res = self.client.get('/1/materials/%s/pdf/' % self.content0['material_id'])
        self.assertEqual(res.status_code, 200)
