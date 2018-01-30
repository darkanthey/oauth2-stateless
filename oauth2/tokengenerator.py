"""
Provides various implementations of algorithms to generate an Access Token or Refresh Token.
"""

import hashlib
import os
import uuid

import itsdangerous
from oauth2.error import AccessTokenNotFound


class TokenGenerator(object):
    """
    Base class of every token generator.
    """

    def __init__(self):
        """
        Create a new instance of a token generator.
        """
        self.expires_in = {}
        self.refresh_expires_in = 0

    def create_access_token_data(self, data, scopes, grant_type, user_id, client_id):
        """
        Create data needed by an access token.

        :param data: Arbitrary data as returned by the ``authenticate()`` method of a ``SiteAdapter``.
        :type data: dict
        :param grant_type:
        :type grant_type: str
        :param user_id: Identifier of the current user as returned by the ``authenticate()`` method of a ``SiteAdapter``
        :type user_id: int
        :param client_id: Identifier of the current client.
        :type client_id: str

        :return: A ``dict`` containing the ``access_token`` and the
                 ``token_type``. If the value of ``TokenGenerator.expires_in``
                 is larger than 0, a ``refresh_token`` will be generated too.
        :rtype: dict
        """
        result = {"access_token": self.generate(grant_type, data, scopes, user_id, client_id), "token_type": "Bearer"}

        grant_type_expires_in = self.expires_in.get(grant_type)
        if grant_type_expires_in:
            result["refresh_token"] = self.refresh_generate(grant_type, data, scopes, user_id, client_id)
            result["expires_in"] = grant_type_expires_in

        return result

    def generate(self, grant_type=None, data=None, scopes=None, user_id=None, client_id=None):
        """
        Implemented by generators extending this base class.

        :param grant_type: Identifier token grant_type
        :type grant_type: str
        :param data: Arbitrary data as returned by the ``authenticate()`` method of a ``SiteAdapter``.
        :type data: dict
        :param scopes: scopes for oauth session
        :type scopes: dict
        :param user_id: Identifier of the current user as returned by the ``authenticate()`` method of a ``SiteAdapter``
        :type user_id: int
        :param client_id: Identifier of the current client.
        :type client_id: str

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def refresh_generate(self, grant_type=None, data=None, scopes=None, user_id=None, client_id=None):
        """
        Implemented by refresh generators extending this base class.

        :param grant_type: Identifier token grant_type
        :type grant_type: str
        :param data: Arbitrary data as returned by the ``authenticate()`` method of a ``SiteAdapter``.
        :type data: dict
        :param scopes: scopes for oauth session
        :type scopes: dict
        :param user_id: Identifier of the current user as returned by the ``authenticate()`` method of a ``SiteAdapter``
        :type user_id: int
        :param client_id: Identifier of the current client.
        :type client_id: str

        :raises NotImplementedError:
        """
        raise NotImplementedError


class StatelessTokenGenerator(TokenGenerator):
    """
    Generate a token using JSON Web Tokens tokens.
    """

    def __init__(self, secret_key):
        self.serializer = itsdangerous.URLSafeTimedSerializer(secret_key)
        TokenGenerator.__init__(self)

    def json_serialize(self, data):
        _data = dict((k, v) for k, v in data.items() if v)  # Remove empty val
        return self.serializer.dumps(_data)

    def unserialize(self, serialized):
        try:
            payload, timestamp = self.serializer.loads(serialized, return_timestamp=True)
            payload["refresh_expires_at"] = timestamp
            return payload
        except (itsdangerous.BadSignature, itsdangerous.SignatureExpired):
            raise AccessTokenNotFound

    def validate_token(self, token, token_type):
        payload = self.unserialize(token)
        if payload['type'] != token_type:
            raise AccessTokenNotFound
        return payload

    def generate(self, grant_type=None, data=None, scopes=None, user_id=None, client_id=None):
        """
        :return: A new token
        :rtype: str
        """
        # We use the same generator for code and access_token
        # JWT will return the same code for different user
        user_id = user_id if user_id else str(uuid.uuid4())

        return self.json_serialize(dict(type='access_token', grant_type=grant_type, user_id=user_id, data=data,
                                        scopes=scopes, client_id=client_id))

    def refresh_generate(self, grant_type=None, data=None, scopes=None, user_id=None, client_id=None):
        """
        :return: A new refresh token
        :rtype: str
        """
        return self.json_serialize(dict(type='refresh_token', grant_type=grant_type, user_id=user_id, data=data,
                                        scopes=scopes, client_id=client_id))


class URandomTokenGenerator(TokenGenerator):
    """
    Create a token using ``os.urandom()``.
    """

    def __init__(self, length=40):
        self.token_length = length
        TokenGenerator.__init__(self)

    def generate(self, grant_type=None, data=None, scopes=None, user_id=None, client_id=None):
        """
        :return: A new token
        :rtype: str
        """
        random_data = os.urandom(100)

        hash_gen = hashlib.new("sha512")
        hash_gen.update(random_data)

        return hash_gen.hexdigest()[:self.token_length]

    refresh_generate = generate


class Uuid4TokenGenerator(TokenGenerator):
    """
    Generate a token using uuid4.
    """

    def generate(self, grant_type=None, data=None, scopes=None, user_id=None, client_id=None):
        """
        :return: A new token
        :rtype: str
        """
        return str(uuid.uuid4())

    refresh_generate = generate
