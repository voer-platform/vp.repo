"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from vpc_api.models import APIClient
from views import createAuthor, createEditor, createModule
from models import Author, Metadata, Category


class AuthorTestCase(TestCase):

    fn = 'Barrack Obama',
    aid = 'b_obama',
    bio = 'Re-elected US president'

    def setUp(self):
        # call the function
        params = {
            'fullname': self.fn,
            'author_id': self.aid,
            'bio': self.bio
            }
        self.author = createAuthor(**params)

    def testCreate(self):
        self.assertNotEqual(self.author.id, None)
        self.assertEqual(self.author.fullname, self.fn)
        self.assertEqual(self.author.author_id, self.aid)
        self.assertEqual(self.author.bio, self.bio)


def createAPIClient(name, cid, org='Sample Org', secret='secret'):
    return APIClient.objects.create(client_id=cid, name=name, organization=org, secret_key=secret)


def createCategory(number=1):
    cats = []
    for cat in range(number):
        cats.append(Category.objects.create(name='Category '+str(cat+1), 
                                            description='Description '+str(cat+1)))
    return cats


class EditorTestCase(TestCase):
    client = None
    eid = 'my_editor_id'
    editor = None

    def setUp(self):
        self.client = createAPIClient('John Service', 'johnser')
        params = {
            'editor_id': self.eid,
            'client': self.client,
            }
        self.editor = createEditor(**params)

    def testCreate(self):
        self.assertNotEqual(self.editor.id, None)
        self.assertEqual(self.editor.editor_id, self.eid)
        self.assertEqual(self.editor.client, self.client)

       
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
