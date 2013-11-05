"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from vpr_content import models
import os
import views


class UtilTestCase(TestCase):

    def test_downloadFile(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        url = 'http://www.google.com/images/srpr/logo11w.png'
        path = 'google-logo.jpg'
        res = views.downloadFile(url, path)
        self.assertEqual(res, True)
        with open(path, 'rb') as logo_file:
            self.assertNotEqual(logo_file.read(), '')
            os.remove(path)

    def test_downloadFile_failed(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        url = 'http://google.com/images/nerver-existed.png'
        path = 'google-logo.jpg'
        res = views.downloadFile(url, path)
        self.assertEqual(res, False)
    
    def test_storeMaterialExport(self):
        """
        """
        url = 'http://www.google.com/images/srpr/logo11w.png'
        me = models.MaterialExport(material_id='test-mid', version=1)
        views.storeMaterialExport(url, me)
        self.assertNotEqual(me.path, '')
        self.assertNotEqual(me.file_type, '')

