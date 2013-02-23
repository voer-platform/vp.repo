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
    token = ''

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
        try:
            token = eval(res.content)['token']
        except:
            token = ''
        print 'Combination: ' + self.comb
        print 'Token: ' + token
        self.assertNotEqual(token, '')
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


class TokenTest(TestCase):
    """For testing API token"""
    api_client = None
    token = ''

    def setUp(self):
        """docstring for setup"""
        self.api_client = createClient()
        sugar = 'sugar!'
        comb = createAuthCombination(self.api_client.secret_key, sugar)
        res = self.client.post('/1/auth/' + self.api_client.client_id + '/',
                               {'sugar':sugar, 'comb':comb},
                               )
        self.token = eval(res.content)['token']

    def test_authenticate_token(self):
        """Test good token with listing materials
        """
        self.client.cookies['vpr_token'] = self.token
        self.client.cookies['vpr_client'] = self.api_client.client_id
        res = self.client.get('/1/materials/')
        print res.content
        self.assertEqual(res.status_code, 200)


