import re

from oauth2.test import unittest
from oauth2.tokengenerator import URandomTokenGenerator, Uuid4TokenGenerator, StatelessTokenGenerator


class StatelessTokenGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.sekret_key = "xxx"
        self.token_len_with_grant_type = 100
        self.refresh_token_len_with_grant_type = 102

    def test_create_code_token_data_no_expiration(self):
        generator = StatelessTokenGenerator(self.sekret_key)

        result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id=None, client_id=None)

        self.assertEqual(result["token_type"], "Bearer")

    def test_check_access_token_for_diff_secret_key(self):
        generator = StatelessTokenGenerator(self.sekret_key)
        generator1 = StatelessTokenGenerator('yyy')

        result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id='user1', client_id=None)

        result1 = generator1.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id='user1', client_id=None)

        self.assertEqual(result["token_type"], "Bearer")
        self.assertEqual(result1["token_type"], "Bearer")

        self.assertNotEqual(result["access_token"], result1["access_token"])

    def test_create_code_token_data_with_expiration(self):
        generator = StatelessTokenGenerator(self.sekret_key)

        generator.expires_in = {'test_grant_type': 600}

        result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id=None, client_id=None)

        self.assertEqual(result["token_type"], "Bearer")
        self.assertEqual(len(result["refresh_token"]), self.refresh_token_len_with_grant_type)
        self.assertEqual(result["expires_in"], 600)

    def test_check_code_and_access_token(self):
        generator = StatelessTokenGenerator(self.sekret_key)
        user1 = 'user1'

        code_result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                         user_id=None, client_id=None)

        code_result1 = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                          user_id=None, client_id=None)

        token_result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                          user_id=user1, client_id=None)

        token_result1 = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                           user_id=user1, client_id=None)

        self.assertEqual(code_result["token_type"], "Bearer")
        self.assertEqual(code_result1["token_type"], "Bearer")
        self.assertEqual(token_result["token_type"], "Bearer")
        self.assertEqual(token_result1["token_type"], "Bearer")

        # Access_token, Code result shold be diff
        self.assertNotEqual(code_result["access_token"], code_result1["access_token"])
        self.assertNotEqual(code_result["access_token"], token_result["access_token"])
        self.assertEqual(token_result["access_token"], token_result1["access_token"])

        # Unserialize result for access_token shold be the same
        result_token = generator.unserialize(token_result["access_token"])
        result1_token = generator.unserialize(token_result1["access_token"])
        self.assertEqual(result_token["user_id"], result1_token["user_id"])

    def test_create_code_token_data_with_expiration_scopes(self):
        generator = StatelessTokenGenerator(self.sekret_key)

        generator.expires_in = {'test_grant_type': 600}

        result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id=None, client_id=None)

        self.assertEqual(result["token_type"], "Bearer")
        self.assertEqual(len(result["refresh_token"]), self.refresh_token_len_with_grant_type)
        self.assertEqual(result["expires_in"], 600)

    def test_check_stateless_token(self):
        generator = StatelessTokenGenerator(self.sekret_key)

        generator.expires_in = {'test_grant_type': 600}
        scopes1 = ['xxx', 'yyy']
        user1 = 'user1'
        client1 = 'client1'

        result = generator.create_access_token_data(data=None, scopes=scopes1, grant_type='test_grant_type',
                                                    user_id=user1, client_id=client1)

        self.assertEqual(result["token_type"], "Bearer")
        self.assertEqual(result["expires_in"], 600)

        access_token = result["access_token"]
        refresh_token = result["refresh_token"]

        data = generator.unserialize(access_token)
        self.assertEqual(data["user_id"], user1)
        self.assertEqual(data["client_id"], client1)
        self.assertEqual(data["scopes"], scopes1)
        self.assertEqual(data["type"], 'access_token')

        refresh_data = generator.unserialize(refresh_token)
        self.assertEqual(refresh_data["user_id"], user1)
        self.assertEqual(refresh_data["client_id"], client1)
        self.assertEqual(refresh_data["scopes"], scopes1)
        self.assertEqual(refresh_data["type"], 'refresh_token')


class URandomTokenGeneratorTestCase(unittest.TestCase):
    def test_generate(self):
        length = 20

        generator = URandomTokenGenerator(length=length)

        result = generator.generate()

        self.assertTrue(isinstance(result, str))
        self.assertEqual(len(result), length)


class Uuid4TokenGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.uuid_regex = r"^[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}-[a-z0-9]{12}$"

    def test_create_access_token_data_no_expiration(self):
        generator = Uuid4TokenGenerator()

        result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id=None, client_id=None)

        self.assertRegexpMatches(result["access_token"], self.uuid_regex)
        self.assertEqual(result["token_type"], "Bearer")

    def test_create_access_token_data_with_expiration(self):
        generator = Uuid4TokenGenerator()

        generator.expires_in = {'test_grant_type': 600}

        result = generator.create_access_token_data(data=None, scopes=None, grant_type='test_grant_type',
                                                    user_id=None, client_id=None)

        self.assertRegexpMatches(result["access_token"], self.uuid_regex)
        self.assertEqual(result["token_type"], "Bearer")
        self.assertRegexpMatches(result["refresh_token"], self.uuid_regex)
        self.assertEqual(result["expires_in"], 600)

    def test_generate(self):
        generator = Uuid4TokenGenerator()

        result = generator.generate()
        regex = re.compile(self.uuid_regex)
        match = regex.match(result)

        self.assertEqual(result, match.group())

if __name__ == "__main__":
    unittest.main()
