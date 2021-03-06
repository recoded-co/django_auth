# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils import simplejson as json
from django.utils.unittest import skip
      
class AuthenticationTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        User.objects.create_user(u'åäö', '', u'åäö')

    @skip('geonition_utils updated (HttpResponseCreated), view not updated as not in use at the moment')    
    def test_registration(self):
        """
        Tests that the registration works.
        """
        #valid post
        post_content = {'username':'mike', 'password':'mikepass'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 201)

        #logout
        self.client.logout()

        #invalid post
        post_content = {'something':'some'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 400)
        
        post_content = {'username':'mike'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 400)
        
        post_content = {'password':'mike'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 400)
        
        #conflict
        post_content = {'username':'mike', 'password':'mikepass'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 409)
        
        #test registering with username äöå
        post_content = {'username': u'ånänön', 'password': u'åäöåäöåäöåäö'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 201)

    @skip('geonition_utils updated (HttpResponseCreated), view not updated as not in use at the moment')    
    def test_login(self):
        """
        test the login procedure
        """
        #register a user
        post_content = {'username':'testuser', 'password':'testpass'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content), \
                                    content_type='application/json')
        self.assertEquals(response.status_code,
                          201,
                          'registration did not work')

        #logout after registration
        self.client.logout()
        
        #invalid login
        post_content = {'username':'some', 'password':'pass'}
        response = self.client.post(reverse('api_login'),
                                    json.dumps(post_content), 
                                    content_type='application/json')
        self.assertEquals(response.status_code, 401)
        post_content = {'username':'some', 'password':'testpass'}
        response = self.client.post(reverse('api_login'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 401)
        post_content = {'username':'testuser', 'password':'pass'}
        response = self.client.post(reverse('api_login'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code, 401)
        
        #valid login
        post_content = {'username':'testuser', 'password':'testpass'}
        response = self.client.post(reverse('api_login'),
                                    json.dumps(post_content), 
                                    content_type='application/json')
        self.assertEquals(response.status_code,
                          200,
                          'login with valid username and password did not work')
        
        #test login with username including swedish characters åöä
        self.client.logout()
        post_content = {'username': u'åäö', 'password': u'åäö'}
        response = self.client.post(reverse('api_login'),
                                    json.dumps(post_content), 
                                    content_type='application/json')
        self.assertEquals(response.status_code,
                          200,
                          'login with valid username and password did not work')
        
        
    def test_session(self):
        """
        This method tests the create session
        REST url.
        """
        #create the initial session
        response = self.client.post(reverse('api_session'))
        self.assertEqual(response.status_code,
                         200,
                         "The initial session creation through the session url did not work")
        
        #get the initial session key
        session_key_anonymous = self.client.get(reverse('api_session')).content
        
        #try to create a session
        response = self.client.post(reverse('api_session'))
        self.assertEqual(response.status_code,
                         200,
                         "The session creation through the session url did not work")
        
        
        #check that the session created is the same for all gets even if post in between
        session_key_anonymous_user = self.client.get(reverse('api_session')).content
        self.assertEqual(session_key_anonymous_user,
                            session_key_anonymous,
                            "The post to session url created a new session")
        
        #only one session can be created per anonymous user
        response = self.client.post(reverse('api_session'))
        self.assertEqual(response.status_code,
                         200,
                         "The session creation through the session url did not work")
        
        #get the possibly new session key
        session_key_anonymous_user_2 = self.client.get(reverse('api_session')).content
        
        self.assertEqual(session_key_anonymous_user,
                          session_key_anonymous_user_2,
                          "The session key is not persistent for anonymous user")
            
            
        #delete the session
        response = self.client.delete(reverse('api_session'))
        self.assertEqual(response.status_code,
                         200,
                         "The session deletion through the session url did not work")
        
        
        
        #only one session can be created per anonymous user
        response = self.client.post(reverse('api_session'))
        self.assertEqual(response.status_code,
                         200,
                         "The session creation through the session url did not work second time")

        #check that the new session created is not the same
        session_key_anonymous_user = self.client.get(reverse('api_session')).content
        self.assertNotEqual(session_key_anonymous_user,
                            session_key_anonymous,
                            "The post to session url did not create a new session for second anonymous user")
    
    @skip('geonition_utils updated (HttpResponseCreated), view not updated as not in use at the moment')    
    def test_new_password(self):
        
        post_content = {'username':'testuser', 'password':'testpass'}
        response = self.client.post(reverse('api_register'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        self.assertEquals(response.status_code,
                          201,
                          'registration did not work')
        
        
        
        user = User.objects.get(username = "testuser")
        user.email = "test@aalto.fi"
        user.save()

    def test_change_passwd(self):
        
        #i guess django is not running this test
        #change passowrd for user åäö
        self.client.login(username = u'åäö', password = u'åäö')
        
        post_content = {'old_password':'åäö', 'new_password':'betterpass'}
        response = self.client.post(reverse('api_change_password'),
                                    json.dumps(post_content),
                                    content_type='application/json')

        self.assertEquals(response.status_code,
                          200,
                          "The valid password was not changed")
        
        #login the user again
        self.client.login(username = u'åäö', password = u'betterpass')
        
        post_content = {'old_password':'betterpas', 'new_password':'short'}
        response = self.client.post(reverse('api_change_password'),
                                    json.dumps(post_content),
                                    content_type='application/json')
        
        self.assertEquals(response.status_code,
                          401,
                          "The invalid password was changed")
        
        
        