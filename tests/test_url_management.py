"""Testing url management functionalities."""
import unittest
import json
from app import create_app, db
from app.models import LongUrl, ShortUrl, UrlActivityLogs, User
from base64 import b64encode
from flask import url_for
from time import sleep


class ApiShorten(unittest.TestCase):
    """Testing url management functionalities."""

    def setUp(self):
        """Setup app for testing before each test case."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.user = User(first_name='ichiato', last_name='ikikin',
                         email='ichiato@yahoo.com', password='password')

    def tearDown(self):
        """Delete app and db instances after each test case."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_auth_token(self, email_header=None):
        """Get a valid token for authentication."""
        self.user.save()
        if not email_header:
            email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                       'password')

        token_response = self.client.get(url_for('api.get_token'),
                                         headers=email_header)
        json_token_response = json.loads(token_response.data.decode('utf-8'))
        token = json_token_response['token']
        token_header = self.api_token_auth_headers(token)
        return token_header

    def shorten_4_url(self):
        """Shorten four urls for use in other test cases."""
        post_data = json.dumps({"url": "http://www.andela.com"})
        post_data2 = json.dumps({"url": "http://www.google.com"})
        post_data3 = json.dumps({"url": "http://www.wikipedia.com"})
        post_data4 = json.dumps({"url": "http://www.devops.com"})
        token_header = self.get_auth_token()
        shorten_response_with_token_auth = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=post_data)
        sleep(2)
        shorten_response_with_token_auth2 = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=post_data2)
        sleep(2)
        shorten_response_with_token_auth3 = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=post_data3)
        sleep(2)
        shorten_response_with_token_auth4 = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=post_data4)
        return [shorten_response_with_token_auth,
                shorten_response_with_token_auth2,
                shorten_response_with_token_auth3,
                shorten_response_with_token_auth4]

    def api_email_auth_headers(self, email, password):
        """Setup an authorization header with an email and password."""
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def api_token_auth_headers(self, token):
        """Setup an authorization header with a token."""
        return {
            'Authorization': 'Basic ' + b64encode(
                (token + ':' + '').encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_anonymous_user_delete_url(self):
        """Test that anonymous users cannot delete a short_url via the API."""
        self.shorten_4_url()
        response = self.client.delete(url_for('api.delete_urls', id=1))
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'Permission required! You are not allowed access'
                         ' to this resource.')

    def test_registered_user_delete_via_api(self):
        """Test that registered users can delete a short_url via the API."""
        self.shorten_4_url()
        token_header = self.get_auth_token()
        response = self.client.delete(url_for('api.delete_urls', id=1),
                                      headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'Deleted')

    def test_shorturl_delete_twice(self):
        """Test that a short_url cannot be deleted twice."""
        self.shorten_4_url()
        token_header = self.get_auth_token()
        response = self.client.delete(url_for('api.delete_urls', id=1),
                                      headers=token_header)
        response2 = self.client.delete(url_for('api.delete_urls', id=1),
                                       headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        json_response2 = json.loads(response2.data.decode('utf-8'))
        msg = json_response['message']
        msg2 = json_response2['error']
        self.assertEqual(msg, 'Deleted')
        self.assertEqual(msg2, 'Resource not found')

    def test_toogle_is_active(self):
        """Test that users can deactivate and activate their short_urls."""
        self.shorten_4_url()
        token_header = self.get_auth_token()
        url = '/api/v1/short_url/1/deactivate'
        response = self.client.put(url, headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'Deactivation Successful.')
        self.assertEqual(200, response.status_code)
        url2 = '/api/v1/short_url/1/activate'
        response2 = self.client.put(url2, headers=token_header)
        json_response2 = json.loads(response2.data.decode('utf-8'))
        msg2 = json_response2['message']
        self.assertEqual(msg2, 'Activation Successful.')
        self.assertEqual(200, response.status_code)

    def test_toogle_other_users_shorturl(self):
        """Test that users can only deactivate their short_urls."""
        user2 = User(first_name='sefia', last_name='ikikin',
                     email='sefiaomo@yahoo.com', password='password')
        user2.save()
        self.shorten_4_url()
        email_header = self.api_email_auth_headers('sefiaomo@yahoo.com',
                                                   'password')
        token_header = self.get_auth_token(email_header)
        url = '/api/v1/short_url/1/deactivate'
        response = self.client.put(url, headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['error']
        self.assertTrue(response.status_code == 404)
        self.assertEqual(msg, 'Resource not found')

    def test_delete_other_users_shorturl(self):
        """Test that users can only delete their short_urls."""
        user2 = User(first_name='sefia', last_name='ikikin',
                     email='sefiaomo@yahoo.com', password='password')
        user2.save()
        self.shorten_4_url()
        email_header = self.api_email_auth_headers('sefiaomo@yahoo.com',
                                                   'password')
        token_header = self.get_auth_token(email_header)
        response = self.client.delete(url_for('api.delete_urls', id=1),
                                      headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['error']
        self.assertTrue(response.status_code == 404)
        self.assertEqual(msg, 'Resource not found')

    def test_shorturl_redirection(self):
        """Test the redirection of active short_urls."""
        token_header = self.get_auth_token()
        responses = self.shorten_4_url()
        post_data_response = json.loads(responses[0]
                                        .data.decode('utf-8'))
        short_url = post_data_response['short_url']
        response = self.client.get(url_for('api.get_url',
                                   shorturl=short_url[22:]),
                                   headers=token_header)
        self.assertEqual(302, response.status_code)
        self.assertIn('http://www.andela.com', str(response.data))

    def test_inactive_shorturl_redirection(self):
        """"Test that inactive short_urls don't redirect."""
        responses = self.shorten_4_url()
        token_header = self.get_auth_token()
        url = '/api/v1/short_url/1/deactivate'
        response = self.client.put(url, headers=token_header)
        post_data_response = json.loads(responses[0].data.decode('utf-8'))
        short_url = post_data_response['short_url']
        response = self.client.get(url_for('api.get_url',
                                   shorturl=short_url[22:]),
                                   headers=token_header)
        self.assertEqual(400, response.status_code)
        self.assertNotIn('http://www.andela.com', str(response.data))

    def test_deleted_shorturl_redirection(self):
        """Test that already deleted short_urls don't redirect."""
        responses = self.shorten_4_url()
        token_header = self.get_auth_token()
        response = self.client.delete(url_for('api.delete_urls', id=1),
                                      headers=token_header)
        post_data_response = json.loads(responses[0]
                                        .data.decode('utf-8'))
        short_url = post_data_response['short_url']
        response = self.client.get(url_for('api.get_url',
                                   shorturl=short_url[22:]),
                                   headers=token_header)
        self.assertEqual(404, response.status_code)
        self.assertNotIn('http://www.andela.com', str(response.data))

    def test_get_shorturl_by_popularity(self):
        """Test the sorting of short_urls based on popularity."""
        token_header = self.get_auth_token()
        responses = self.shorten_4_url()
        post_data_response = json.loads(responses[0]
                                        .data.decode('utf-8'))
        short_url = post_data_response['short_url']
        post_data_response2 = json.loads(responses[1]
                                         .data.decode('utf-8'))
        short_url2 = post_data_response2['short_url']
        post_data_response3 = json.loads(responses[2]
                                         .data.decode('utf-8'))
        short_url3 = post_data_response3['short_url']
        self.client.get(url_for('api.get_url', shorturl=short_url[22:]),
                        headers=token_header)
        self.client.get(url_for('api.get_url', shorturl=short_url[22:]),
                        headers=token_header)
        self.client.get(url_for('api.get_url', shorturl=short_url[22:]),
                        headers=token_header)
        self.client.get(url_for('api.get_url', shorturl=short_url2[22:]),
                        headers=token_header)
        self.client.get(url_for('api.get_url', shorturl=short_url2[22:]),
                        headers=token_header)
        self.client.get(url_for('api.get_url', shorturl=short_url3[22:]),
                        headers=token_header)
        response = self.client.get(url_for('api.sort_urls',
                                   url_type='shorturl',
                                   sort_type='popularity'),
                                   headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        url_list = json_response['url_list']
        self.assertEqual(200, response.status_code)
        self.assertTrue(url_list[0]['Times_visted'] >
                        url_list[1]['Times_visted'])
        self.assertTrue(url_list[1]['Times_visted'] >
                        url_list[2]['Times_visted'])
        self.assertTrue(url_list[2]['Times_visted'] >
                        url_list[3]['Times_visted'])

    def test_get_shorturl_by_date(self):
        """Sort all short_url by most recently created."""
        token_header = self.get_auth_token()
        self.shorten_4_url()
        response = self.client.get(url_for('api.sort_urls',
                                   url_type='shorturl',
                                   sort_type='date'),
                                   headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        url_list = json_response['url_list']
        self.assertEqual(200, response.status_code)
        self.assertTrue(url_list[0]['Date_added'] >
                        url_list[1]['Date_added'])
        self.assertTrue(url_list[1]['Date_added'] >
                        url_list[2]['Date_added'])
        self.assertTrue(url_list[2]['Date_added'] >
                        url_list[3]['Date_added'])

    def test_update_target_url(self):
        """Test the updating of a short_url target url.

        This target URL never existed in the database and thus needs to be
        newly persisted to the databse.
        """
        post_data = json.dumps({"url": "http://www.easterbunny.com"})
        self.shorten_4_url()
        token_header = self.get_auth_token()
        former_url = ShortUrl.query.get(1).long_url
        self.client.put(url_for('api.change_long_url', id=1),
                        headers=token_header, data=post_data)
        new_url = ShortUrl.query.get(1).long_url
        self.assertNotEqual(former_url, new_url)
        self.assertIn('http://www.andela.com', former_url.__repr__())
        self.assertIn('http://www.easterbunny.com', new_url.__repr__())

    def test_update_target_url2(self):
        """Test the updating of a short_url target url.

        This target URL already exist in the database and thus need not to be
        saved to the database again.
        """
        post_data = json.dumps({"url": "http://www.devops.com"})
        self.shorten_4_url()
        token_header = self.get_auth_token()
        former_url = ShortUrl.query.get(1).long_url
        self.client.put(url_for('api.change_long_url', id=1),
                        headers=token_header, data=post_data)
        new_url = ShortUrl.query.get(1).long_url
        self.assertNotEqual(former_url, new_url)
        self.assertIn('http://www.andela.com', former_url.__repr__())
        self.assertIn('http://www.devops.com', new_url.__repr__())

    def test_update_another_user_short_url_targeturl(self):
        """Test updating another users short_url target url."""
        user2 = User(first_name='sefia', last_name='ikikin',
                     email='sefiaomo@yahoo.com', password='password')
        user2.save()
        self.shorten_4_url()
        email_header = self.api_email_auth_headers('sefiaomo@yahoo.com',
                                                   'password')
        token_header = self.get_auth_token(email_header)
        post_data = json.dumps({"url": "http://www.easterbunny.com"})
        former_url = ShortUrl.query.get(1).long_url
        self.client.put(url_for('api.change_long_url', id=1),
                        headers=token_header, data=post_data)
        new_url = ShortUrl.query.get(1).long_url
        self.assertEqual(former_url, new_url)
        self.assertIn('http://www.andela.com', former_url.__repr__())
        self.assertNotIn('http://www.easterbunny.com', new_url.__repr__())
        self.assertIn('http://www.andela.com', new_url.__repr__())

    def test_update_target_url_with_bad_body(self):
        """Update a short_url long_url with missing keys returns 400 error."""
        post_data = json.dumps({"u": "http://www.easterbunny.com"})
        self.shorten_4_url()
        token_header = self.get_auth_token()
        former_url = ShortUrl.query.get(1).long_url
        response = self.client.put(url_for('api.change_long_url', id=1),
                                   headers=token_header, data=post_data)
        new_url = ShortUrl.query.get(1).long_url
        self.assertEqual(400, response.status_code)
        self.assertEqual(former_url, new_url)
        self.assertIn('http://www.andela.com', former_url.__repr__())
        self.assertNotIn('http://www.easterbunny.com', new_url.__repr__())
        self.assertIn('http://www.andela.com', new_url.__repr__())

    def test_update_target_url_with_no_body(self):
        """Update a short_url target url with no body returns a  400 error."""
        self.shorten_4_url()
        token_header = self.get_auth_token()
        former_url = ShortUrl.query.get(1).long_url
        response = self.client.put(url_for('api.change_long_url', id=1),
                                   headers=token_header)
        new_url = ShortUrl.query.get(1).long_url
        self.assertEqual(400, response.status_code)
        self.assertEqual(former_url, new_url)
        self.assertIn('http://www.andela.com', former_url.__repr__())
        self.assertNotIn('http://www.easterbunny.com', new_url.__repr__())
        self.assertIn('http://www.andela.com', new_url.__repr__())

    def test_no_duplication_of_long_url(self):
        """Test that long urls are not duplicated in the database."""
        user2 = User(first_name='sefia', last_name='ikikin',
                     email='sefiaomo@yahoo.com', password='password')
        user2.save()
        self.shorten_4_url()
        email_header = self.api_email_auth_headers('sefiaomo@yahoo.com',
                                                   'password')
        token_header = self.get_auth_token(email_header)
        post_data = json.dumps({"url": "http://www.andela.com"})
        post_data2 = json.dumps({"url": "http://www.google.com"})
        self.client.post(url_for('api.shorten_url'), headers=token_header,
                         data=post_data)
        self.client.post(url_for('api.shorten_url'), headers=token_header,
                         data=post_data2)
        query_long_url = LongUrl.query.filter_by(
            long_url="http://www.andela.com")
        query_long_url2 = LongUrl.query.filter_by(
            long_url="http://www.google.com")
        with self.assertRaises(IndexError):
            query_long_url[1]
        with self.assertRaises(IndexError):
            query_long_url2[1]

    def test_short_url_activity_logs(self):
        """Test that short_url visited records logs of its visitors."""
        responses = self.shorten_4_url()
        post_data_response = json.loads(responses[0]
                                        .data.decode('utf-8'))
        short_url = post_data_response['short_url']
        self.client.get(url_for('api.get_url', shorturl=short_url[22:]),
                        environ_base={'HTTP_USER_AGENT': 'chrome, windows',
                        'REMOTE_ADDR': '221.192.199.49'})
        log = UrlActivityLogs.query.get(1)
        self.assertEqual(log.ip, '221.192.199.49')
        self.assertEqual(log.platform, 'windows')
        self.assertEqual(log.browser, 'chrome')

    def test_get_user_shorturl(self):
        """Test getting user short_url list."""
        self.shorten_4_url()
        token_header = self.get_auth_token()
        response = self.client.get(url_for('api.get_user_short_urls'),
                                   headers=token_header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['short_url list'][0]
        self.assertTrue(msg['Date_added'])
        self.assertEqual(msg['Times_visted'], 0)
        self.assertTrue(msg['Active status'])
        self.assertTrue(msg['short_url'])
