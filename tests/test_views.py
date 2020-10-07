from django.contrib.auth.models import User
from django.core import management
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from app.models import Author, Occurrence

"""
All setUpTestData methods flush the database since we are using an external database for testing.
"""


class LoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        management.call_command('flush', interactive=False)
        User.objects.create_user(username="user", password="password")

    def test_valid_request(self):
        response = self.client.post('/login', data={'username': 'user', 'password': 'password'})
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(body['data'], {'username': 'user'})
        self.assertTrue('token' in body.keys())

    def test_invalid_body(self):
        response = self.client.post('/login', data={'username': 'user'})
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Invalid body')

    def test_invalid_credentials(self):
        response = self.client.post('/login', data={'username': 'user', 'password': 'wrong_password'})
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Invalid credentials')


class GetOccurrenceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        management.call_command('flush', interactive=False)
        user = User.objects.create_user(username="user", password="password")
        user2 = User.objects.create_user(username="user2", password="password2")
        author = Author.objects.create(user=user)
        author2 = Author.objects.create(user=user2)
        point = 'POINT(0 0)'
        point2 = 'POINT(1 0)'
        description = 'description'
        category = 'construction'
        category2 = 'incident'

        # Id -> 1 [Author: user; Point: 0,0; Category: construction]
        Occurrence.objects.create(author=author, point=point, description=description, category=category)
        # Id -> 2 [Author: user2; Point: 0,0; Category: incident]
        Occurrence.objects.create(author=author2, point=point, description=description, category=category2)
        # Id -> 3 [Author: user2; Point: 1,0; Category: construction]
        Occurrence.objects.create(author=author2, point=point2, description=description, category=category)

    # get id field from list of JSON objects
    def get_ids_from_list_of_json(self, list_of_json):
        return [dict(element)['id'] for element in list_of_json]

    def get_list_of_features_from_json_response(self, response):
        return list(dict(response.json())['features'])

    def test_get_all_occurrences(self):
        response = self.client.get('/get_occurrence')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 3)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [1, 2, 3])

    def test_get_all_occurrences_by_category(self):
        response = self.client.get('/get_occurrence?category=construction')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 2)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [1, 3])

        response = self.client.get('/get_occurrence?category=incident')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 1)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [2])

        response = self.client.get('/get_occurrence?category=special_event')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 0)

        # invalid category should return a bad request
        response = self.client.get('/get_occurrence?category=invalid_category')

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_occurrences_by_author(self):
        response = self.client.get('/get_occurrence?author__user__username=user')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 1)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [1])

        response = self.client.get('/get_occurrence?author__user__username=user2')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 2)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [2, 3])

        response = self.client.get('/get_occurrence?author__user__username=user3')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 0)

    def test_get_all_occurrences_by_location_range(self):
        # distance between (0,0) [point] and (0.1,0.1) is approximately 15.69 km
        # distance between (1,0) [point2] and (0.1,0.1) is approximately 100.7 km

        response = self.client.get('/get_occurrence?dist=15680&point=0.1,0.1')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 0)

        response = self.client.get('/get_occurrence?dist=15700&point=0.1,0.1')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 2)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [1, 2])

        response = self.client.get('/get_occurrence?dist=100600&point=0.1,0.1')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 2)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [1, 2])

        response = self.client.get('/get_occurrence?dist=100800&point=0.1,0.1')
        body = self.get_list_of_features_from_json_response(response)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(body), 3)
        self.assertCountEqual(self.get_ids_from_list_of_json(body), [1, 2, 3])


class AddOccurrenceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        management.call_command('flush', interactive=False)
        User.objects.create_user(username="user", password="password")
        user_author = User.objects.create_user(username="user2", password="password")
        Author.objects.create(user=user_author)

    def test_token_authentication(self):
        # token needed for the request
        response = self.client.post('/add_occurrence')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_authentication(self):
        # user is not an author - should be forbidden
        token = Token.objects.create(user_id=1)
        response = self.client.post('/add_occurrence', HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(body['detail'], 'Only authenticated authors can add occurrences')

    def test_invalid_body(self):
        token = Token.objects.create(user_id=2)

        # missing fields
        response = self.client.post('/add_occurrence', data={'description': 'description'},
                                    HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Invalid body')

        # invalid category
        response = self.client.post('/add_occurrence',
                                    data={'description': 'description', 'latitude': 0, 'longitude': 0,
                                          'category': 'invalid_category'}, HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Invalid body')

    def test_valid_request(self):
        token = Token.objects.create(user_id=2)
        response = self.client.post('/add_occurrence',
                                    data={'description': 'description', 'latitude': 0, 'longitude': 0,
                                          'category': 'construction'}, HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())['data']

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(body['properties']['author'], 'user2')
        self.assertEquals(body['properties']['description'], 'description')
        self.assertEquals(body['properties']['status'], 'to_validate')
        self.assertEquals(body['properties']['category'], 'construction')
        self.assertEquals(body['geometry']['coordinates'], [0.0, 0.0])


class UpdateOccurrenceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        management.call_command('flush', interactive=False)
        user = User.objects.create_user(username="user", password="password")
        User.objects.create_user(username="admin", password="password", is_superuser=True)
        author = Author.objects.create(user=user)
        point = 'POINT(0 0)'
        description = 'description'
        category = 'construction'
        Occurrence.objects.create(author=author, point=point, description=description, category=category)

    def test_token_authentication(self):
        # token needed for the request
        response = self.client.put('/update_occurrence/1')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_authentication(self):
        # user is not an admin - should be forbidden
        token = Token.objects.create(user_id=1)
        response = self.client.put('/update_occurrence/1', HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(body['detail'], 'Only authenticated admins can update an occurrences')

    def test_invalid_body(self):
        token = Token.objects.create(user_id=2)
        response = self.client.put('/update_occurrence/1', data={}, content_type="application/json",
                                   HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Invalid body')

        # invalid status
        response = self.client.put('/update_occurrence/1', data={'status': 'invalid_status'},
                                   content_type="application/json",
                                   HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Invalid body')

    def test_nonexistent_occurrence(self):
        token = Token.objects.create(user_id=2)
        response = self.client.put('/update_occurrence/2', data={'status': 'validated'},
                                   content_type="application/json",
                                   HTTP_AUTHORIZATION=f'Token {token}')

        body = dict(response.json())

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(body['detail'], 'Occurrence with id 2 doesnt exist')

    def test_valid_request(self):
        token = Token.objects.create(user_id=2)
        response = self.client.put('/update_occurrence/1', data={'status': 'validated'},
                                   content_type="application/json",
                                   HTTP_AUTHORIZATION=f'Token {token}')
        body = dict(response.json())['data']

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(body['properties']['status'], 'validated')
