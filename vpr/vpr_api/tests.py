"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from vpr_api.models import APIClient
from vpr_api.views import authenticate, createAuthCombination


def createClient():
    """docstring for createClient"""
    client = APIClient()
    client.name = 'Test Client'
    client.client_id = 'test_client'
    client.secret_key = 'this is not a secret'
    client.email = 'test@user.com'
    client.save()
    return client


class AuthenticationTest(TestCase):
    """ """
    comb = ''
    api_client = None
    sugar = ''

    def setUp(self):
        """docstring for setup"""
        self.api_client = createClient()
        self.sugar = 'sugar!'
        self.comb = createAuthCombination(self.api_client.secret_key, self.sugar)
        pass

    def test_authenticate(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        # perform authenticate 
        res = self.client.post('/1/auth/' + self.api_client.client_id + '/',
                               {'sugar':self.sugar, 'comb':self.comb},
                               )
        self.assertEqual(res.status_code, 200)
