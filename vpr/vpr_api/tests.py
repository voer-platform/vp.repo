"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from vpr_api.models import APIClient
from vpr_api.views import authenticate, createAuthCombination


def createClient(client_dict=None):
    """docstring for createClient"""
    if not client_dict:
        client_dict = {
            'name': 'Test Client',
            'client_id': 'test_client',
            'secret_key': 'this is not a secret',
            'email': 'test@test.com',
            }
    client = APIClient(**client_dict)
    client.save()
    return client


class AuthenticationTest(TestCase):
    """For testing API authentication"""
    comb = ''
    api_client = None
    sugar = ''

    def setUp(self):
        """docstring for setup"""
        self.api_client = createClient()
        self.sugar = 'sugar!'
        self.comb = createAuthCombination(self.api_client.secret_key, self.sugar)
        pass

    def test_authenticate_post(self):
        """Perform success authentication using POST
        """
        res = self.client.post('/1/auth/' + self.api_client.client_id + '/',
                               {'sugar':self.sugar, 'comb':self.comb},
                               )
        self.assertEqual(res.status_code, 200)

    def test_authentication_get(self):
        """Perform success authentication using GET
        """
        res = self.client.get('/1/auth/' + self.api_client.client_id + '/' + 
                               '?sugar='+self.sugar+'&comb='+self.comb
                               )
        self.assertEqual(res.status_code, 200)

    def test_authenticate_bad_comb(self):
        """Perform failed authentication 
        """
        res = self.client.post('/1/auth/' + self.api_client.client_id + '/',
                               {'sugar': self.sugar, 'comb': self.comb+'ERR'},
                               )
        self.assertEqual(res.status_code, 406)

    def test_authenticate_bad_client(self):
        """Perform failed authentication 
        """
        res = self.client.post('/1/auth/' + self.api_client.client_id + 'omg/',
                               {'sugar': self.sugar, 'comb': self.comb+'ERR'},
                               )
        self.assertEqual(res.status_code, 406)

